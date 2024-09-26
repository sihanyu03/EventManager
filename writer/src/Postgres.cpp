#include <sstream>
#include <regex>
#include <unordered_set>
#include <unordered_map>
#include "Postgres.h"


Postgres::Postgres(const std::string& project_path) {
    try {
        std::unordered_map db_details {read_db_details(project_path)};
        this->generate_transaction(db_details);
        this->db_connection_status = "OK";
    } catch (const std::runtime_error& e) {
        this->db_connection_status = e.what();
    }
}

std::string Postgres::get_status() const {
    return this->db_connection_status;
}

void Postgres::generate_transaction(std::unordered_map<std::string, std::string>& db_details) {
    const std::string connection_string {"postgresql://" + db_details["user"] + ":" + db_details["password"] +
        "@localhost:5432/" + db_details["name"]};

    try {
        this->cx = std::make_unique<pqxx::connection>(connection_string);
    } catch (const pqxx::broken_connection& e) {
        throw std::runtime_error("Error: Failed to connect to database: " + std::string(e.what()));
    }

    if (!cx->is_open()) {
        throw std::runtime_error("Error: Failed to connect to database");
    }

    this->tx = std::make_unique<pqxx::work>(*cx);
}

bool Postgres::table_exists(const std::string& table_name) const {
    // Select 1 (a placeholder value) from the table and check if any value is found. If not, it means the table doesn't exist
    const std::string query {"SELECT EXISTS ("
                        "   SELECT 1"
                        "   FROM information_schema.tables"
                        "   WHERE table_schema = 'public'"
                        "   AND table_name = '" + table_name + "');"};

    try {
        const pqxx::result result = tx->exec(query);

        // Query returns a matrix, so take first column and first row and return it
        return result[0][0].as<bool>();
    } catch (pqxx::sql_error& e) {
        throw::std::runtime_error("Error: Failed to read database to check whether the table already exists: " + std::string(e.what()));
    }
}

void Postgres::create_table(const std::vector<std::string>& cols, const std::string& table_name) const {
    auto email_found {false};

    std::string query {"CREATE TABLE " + table_name + "(id SERIAL PRIMARY KEY,"};
    for (const std::string& col : cols) {
        // If column is "crsid" or "email", mark email as found and ensure it hasn't been already defined
        if (col == "crsid" || col == "email") {
            if (email_found) {
                throw std::invalid_argument("Error: CSV file contains multiple instances of email or crsid or both");
            }
            email_found = true;
            query += "email VARCHAR(255) UNIQUE,";
        } else if (col == "name") {
            query += "first_name VARCHAR(255), last_name VARCHAR(255),";
        } else {
            query += col + " VARCHAR(255),";
        }
    }
    query.pop_back();
    query += ");";

    if (!email_found) {
        throw std::invalid_argument("Error: CSV file is missing email or crsid");
    }

    try {
        this->tx->exec(query);
    } catch (const pqxx::sql_error& e) {
        throw std::runtime_error("Error: SQL error when creating table: " + std::string(e.what()));
    }
}

std::vector<std::string> Postgres::retrieve_cols(const std::string& table_name) const {
    const std::string query {"SELECT column_name "
                              "FROM information_schema.columns "
                              "WHERE table_name = '" + table_name + "';"};
    const pqxx::result result {this->tx->exec(query)};

    // Loop through all columns in the SQL table and check if the CSV file contains the column.
    std::vector<std::string> cols;
    for (const auto& row : result) {
        // Query returns a matrix, each column is the first and only 'column' of a row, so take row[0]
        const auto col {row[0].as<std::string>()};
        if (col == "id") {
            continue;
        }
        cols.push_back(col);
    }

    return cols;
}

std::vector<std::string> Postgres::get_names(const rapidcsv::Document& doc, const size_t i) {
    std::vector<std::string> names;
    const auto name {doc.GetCell<std::string>("name", i)};

    const std::regex re(", ");
    std::sregex_token_iterator it(name.begin(), name.end(), re, -1);
    std::sregex_token_iterator end;
    int j {0};

    while (it != end && j < 2) {
        if (it->length()) {
            names.push_back(*it);
            j++;
        }
        ++it;
    }

    if (names.size() < 2) {
        throw std::invalid_argument("Error: Column 'name' format wrong, should be 'last_name, first_name'");
    }

    return names;
}

std::string Postgres::get_email(const rapidcsv::Document& doc, const std::unordered_set<std::string>& csv_cols_set, const size_t i) {
    if (csv_cols_set.contains("crsid")) {
        return doc.GetCell<std::string>("crsid", i) + "@cam.ac.uk";
    }
    return doc.GetCell<std::string>("email", i);
}

std::string Postgres::get_first_name(const rapidcsv::Document& doc, const std::unordered_set<std::string>& csv_cols_set, const size_t i) {
    if(csv_cols_set.contains("name")) {
        return get_names(doc, i)[1];
    }
    return doc.GetCell<std::string>("first_name", i);
}

std::string Postgres::get_last_name(const rapidcsv::Document& doc, const std::unordered_set<std::string>& csv_cols_set, const size_t i) {
    if (csv_cols_set.contains("name")) {
        return get_names(doc, i)[0];
    }
    return doc.GetCell<std::string>("last_name", i);
}

void Postgres::write_rows(const rapidcsv::Document& doc, const std::vector<std::string>& db_cols, const std::unordered_set<std::string>& csv_cols_set, const std::string& table_name) const {
    std::string query {"INSERT INTO " + table_name + " ("};
    for (const std::string& col : db_cols) {
        query += col + ",";
    }
    query.pop_back();
    query += ") VALUES ";

    std::vector<std::string> names;
    const auto num_rows = doc.GetRowCount();

    for (size_t i {0}; i < num_rows; i++) {
        query += "(";
        for (const auto& col : db_cols) {
            std::string val;
            if (col == "email") {  // email could be in the form of crsid, so call get_email to handle it
                val = get_email(doc, csv_cols_set, i);
            } else if (col == "first_name") {  // first_name could be under a column "name", in the format last_name, first_name. Let get_first_name handle it
                val = get_first_name(doc, csv_cols_set, i);
            } else if (col == "last_name") {  // last_name could be under a column "name", in the format last_name, first_name. Let get_first_name handle it
                val = get_last_name(doc, csv_cols_set, i);
            } else {
                val = doc.GetCell<std::string>(col, i);
            }
            query += "'" + this->tx->esc(val) + "',";
        }
        query.pop_back();
        query += "),";
    }
    query.pop_back();
    query += " ON CONFLICT (email) DO NOTHING;";

    try {
        this->tx->exec(query);
    } catch (const pqxx::sql_error& e) {
        throw std::runtime_error("Error: SQL error when writing to the table: " + std::string(e.what()));
    }

    this->tx->commit();
}
