#include <iostream>
#include <sstream>
#include "fstream"
#include <unordered_set>
#include <unordered_map>
#include <nlohmann//json.hpp>
#include "Postgres.h"

using json = nlohmann::json;

Postgres::Postgres() {
    try {
        std::unordered_map<std::string, std::string> db_details = read_db_details();
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
    const std::string connection_string = "postgresql://" + db_details["user"] + ":" + db_details["password"] +
        "@localhost:5432/" + db_details["name"];

    try {
        this->cx = std::make_unique<pqxx::connection>(connection_string);
    } catch (const pqxx::broken_connection& e) {
        throw std::runtime_error("Error: failed to connect to database: " + std::string(e.what()));
    }

    if (!cx->is_open()) {
        throw std::runtime_error("Error: failed to connect to database");
    }

    this->tx = std::make_unique<pqxx::work>(*cx);
}

bool Postgres::table_exists(const std::string& table_name) const {
    const std::string query = "SELECT EXISTS ("
                        "   SELECT 1"
                        "   FROM information_schema.tables"
                        "   WHERE table_schema = 'public'"
                        "   AND table_name = '" + table_name + "');";

    pqxx::result result;

    try {
        result = tx->exec(query);
    } catch (pqxx::sql_error& e) {
        throw::std::runtime_error("Error: failed to read database to check whether the table already exists: " + std::string(e.what()));
    }

    return result[0][0].as<bool>();
}

void Postgres::create_table(const std::vector<std::string>& cols, const std::string& table_name) const {
    if (cols.empty()) {
        throw std::runtime_error("Error: cannot create a table with no columns");
    }

    std::string query = "CREATE TABLE " + table_name + "(id SERIAL PRIMARY KEY,";
    for (const std::string& col : cols) {
        if (col == "crsid") {
            query += col + " VARCHAR(50) UNIQUE,";
        } else if (col == "name") {
            query += "first_name VARCHAR(50), last_name VARCHAR(50),";
        } else {
            query += col + " VARCHAR(50),";
        }
    }
    query.pop_back();
    query += ");";

    try {
        this->tx->exec(query);
    } catch (const pqxx::sql_error& e) {
        throw std::runtime_error("Error: SQL error when creating table: " + std::string(e.what()));
    }
}

std::vector<std::string> Postgres::retrieve_cols(rapidcsv::Document& doc, const std::string& table_name) const {
    const auto csv_cols = doc.GetColumnNames();
    const std::unordered_set csv_cols_set(csv_cols.begin(), csv_cols.end());

    const std::string query = "SELECT column_name "
                              "FROM information_schema.columns "
                              "WHERE table_name = '" + table_name + "';";
    const pqxx::result result = this->tx->exec(query);

    std::vector<std::string> cols;
    for (const auto& row : result) {
        const auto col = row[0].as<std::string>();
        if (col == "id") {
            continue;
        }
        if (!csv_cols_set.contains(col)) {
            if ((col != "first_name" && col != "last_name") || !csv_cols_set.contains("name")) {
                throw std::runtime_error("Error: Required column '" + col + "' not found from the csv file");
            }
            if (std::ranges::find(cols, "name") == cols.end()) {
                cols.emplace_back("name");
            }
        } else {
            cols.push_back(col);
        }
    }

    return cols;
}

void Postgres::write_rows(const rapidcsv::Document& doc, const std::vector<std::string>& cols, const std::string& table_name) const {
    std::string query = "INSERT INTO " + table_name + " (";
    for (const std::string& col : cols) {
        if (col != "name") {
            query += col + ",";
        } else {
            query += "first_name, last_name,";
        }
    }
    query.pop_back();
    query += ") VALUES ";

    const auto num_rows = doc.GetRowCount();
    for (size_t i {0}; i < num_rows; i++) {
        query += "(";
        for (const auto& col : cols) {
            const auto val = doc.GetCell<std::string>(col, i);
            if (col != "name") {
                query += "'" + this->tx->esc(val) + "',";
            } else {
                std::stringstream ss(val);
                std::string elem;
                std::vector<std::string> tokens;

                while (std::getline(ss, elem, ' ')) {
                    tokens.push_back(elem);
                }

                if (tokens.size() < 2) {
                    throw std::runtime_error("Error: Format of 'name' column not correct, should be 'first_name, last_name'");
                }

                for (int j = 0; j < std::min(static_cast<size_t>(2), tokens.size() - 1); j++) {
                    tokens[j].pop_back();
                }

                query += "'" + this->tx->esc(tokens[1]) + "','" + this->tx->esc(tokens[0]) + "',";
            }
        }
        query.pop_back();
        query += "),";
    }
    query.pop_back();
    query += " ON CONFLICT (crsid) DO NOTHING;";

    try {
        this->tx->exec(query);
    } catch (const pqxx::sql_error& e) {
        throw std::runtime_error("Error: SQL error when writing to the table: " + std::string(e.what()));
    }
}

void Postgres::commit() const {
    this->tx->commit();
}
