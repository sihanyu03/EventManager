#ifndef POSTGRES_H
#define POSTGRES_H
#include "Database.h"


class Postgres final : public Database {
public:
    Postgres();
    [[nodiscard]] bool table_exists(const std::string&) const override;
    void create_table(const std::vector<std::string>&, const std::string&) const override;
    [[nodiscard]] std::vector<std::string> retrieve_cols(rapidcsv::Document&, const std::string&) const override;
    void write_rows(const rapidcsv::Document&, const std::vector<std::string>&, const std::string&) const override;
    void commit() const override;
    [[nodiscard]] std::string get_status() const override;

private:
    std::unique_ptr<pqxx::connection> cx;
    std::unique_ptr<pqxx::work> tx;
    std::string db_connection_status;
    void generate_transaction(std::unordered_map<std::string, std::string>&);
};



#endif //POSTGRES_H
