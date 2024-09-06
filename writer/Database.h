#ifndef DATABASE_H
#define DATABASE_H
#include <pqxx/pqxx>
#include <rapidcsv.h>

class Database {
public:
    virtual ~Database() = default;
    [[nodiscard]] virtual bool table_exists(const std::string&) const = 0;
    [[nodiscard]] virtual std::string create_table(const std::vector<std::string>&, const std::string&) const = 0;
    [[nodiscard]] virtual std::vector<std::string> retrieve_cols(rapidcsv::Document&, const std::string&) const = 0;
    virtual void write_rows(const rapidcsv::Document&, const std::vector<std::string>&, const std::string&, const std::string&) const = 0;
    virtual void commit() const = 0;
    [[nodiscard]] virtual std::string get_status() const = 0;

protected:
    [[nodiscard]] static std::unordered_map<std::string, std::string> read_db_details();
};



#endif //DATABASE_H
