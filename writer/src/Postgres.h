#ifndef POSTGRES_H
#define POSTGRES_H
#include "Database.h"


class Postgres final : public Database {
public:
    explicit Postgres(const std::string& project_path);
    [[nodiscard]] bool table_exists(const std::string& table_name) const override;
    void create_table(const std::vector<std::string>& cols, const std::string& table_name) const override;
    [[nodiscard]] std::vector<std::string> retrieve_cols(const std::string& table_name) const override;
    void write_rows(const rapidcsv::Document& doc, const std::vector<std::string>& db_cols, const std::unordered_set<std::string>& csv_cols_set, const std::string& table_name) const override;
    [[nodiscard]] std::string get_status() const override;

private:
    std::unique_ptr<pqxx::connection> cx;
    std::unique_ptr<pqxx::work> tx;
    std::string db_connection_status;
    void generate_transaction(std::unordered_map<std::string, std::string>& db_details);
    [[nodiscard]] static std::string get_email(const rapidcsv::Document& doc, const std::unordered_set<std::string>& csv_cols_set, size_t i);
    [[nodiscard]] static std::string get_first_name(const rapidcsv::Document& doc, const std::unordered_set<std::string>& csv_cols_set, size_t i);
    [[nodiscard]] static std::string get_last_name(const rapidcsv::Document& doc, const std::unordered_set<std::string>& csv_cols_set, size_t i);
    [[nodiscard]] static std::vector<std::string> get_names(const rapidcsv::Document& doc, size_t i);
};


#endif //POSTGRES_H
