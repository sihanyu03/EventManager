#ifndef DATABASE_H
#define DATABASE_H
#include <pqxx/pqxx>
#include <nlohmann//json.hpp>
#include <rapidcsv.h>

using json = nlohmann::json;

class Database {
public:
    Database();
    [[nodiscard]] bool table_exists(const std::string&) const;
    void create_table(const std::vector<std::string>&, const std::string&) const;
    [[nodiscard]] std::vector<std::string> retrieve_cols(rapidcsv::Document&, const std::string&) const;
    void write_rows(const rapidcsv::Document&, const std::vector<std::string>&, const std::string&) const;
    void commit() const;
    [[nodiscard]] std::string get_status() const;

private:
    std::unique_ptr<pqxx::connection> cx;
    std::unique_ptr<pqxx::work> tx;
    std::string db_connection_status;
    [[nodiscard]] static std::unordered_map<std::string, std::string> read_db_details();
    void generate_transaction(std::unordered_map<std::string, std::string>&);
};



#endif //DATABASE_H
