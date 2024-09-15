#ifndef DATABASE_H
#define DATABASE_H
#include <pqxx/pqxx>
#include <rapidcsv.h>


class Database {
public:
    virtual ~Database() = default;

    /**
     * Check if a CSV file exists
     *
     * @param table_name Name of the table
     * @return True if table exists, false if it doesn't
     */
    [[nodiscard]] virtual bool table_exists(const std::string& table_name) const = 0;

    /**
     * Initialise an SQL table given the columns and name of the table
     *
     * @param cols Vector of columns
     * @param table_name Name of the table
     */
    virtual void create_table(const std::vector<std::string>& cols, const std::string& table_name) const = 0;

    /**
     * Retrieves the columns of the SQL table that are to be filled
     *
     * @param table_name Name of the table
     * @return Vector of the columns
     */
    [[nodiscard]] virtual std::vector<std::string> retrieve_cols(const std::string& table_name) const = 0;

    /**
     * Write the rows into SQL table
     *
     * @param doc CSF file as a rapidcsv::Document type
     * @param cb_cols Vector of the columns
     * @param csv_cols_set Set of the columns for quick existence checking
     * @param table_name Name of the table
     */
    virtual void write_rows(const rapidcsv::Document& doc, const std::vector<std::string>& cb_cols, const std::unordered_set<std::string>& csv_cols_set, const std::string& table_name) const = 0;

    /**
     * Returns the status of the current connection
     *
     * @return The status as a std::string
     */
    [[nodiscard]] virtual std::string get_status() const = 0;

protected:
    [[nodiscard]] static std::unordered_map<std::string, std::string> read_db_details(const std::string& project_path);
};


#endif //DATABASE_H
