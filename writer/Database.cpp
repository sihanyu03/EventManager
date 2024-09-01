#include <iostream>
#include <sstream>
#include "fstream"
#include <unordered_set>
#include <unordered_map>
#include <nlohmann//json.hpp>
#include "Database.h"

using json = nlohmann::json;

std::unordered_map<std::string, std::string> Database::read_db_details() {
    std::filesystem::path curr_path = std::filesystem::current_path() / ".." / "..";
    std::filesystem::path db_details_path = curr_path / "database_details.json";

    std::ifstream file(db_details_path);
    if (!file) {
        throw std::invalid_argument("Error: failed to read database_details.json. Check that file exists");
    }

    std::stringstream ss;
    ss << file.rdbuf();
    file.close();

    json db_details_json;
    try {
        db_details_json = json::parse(ss.str());
    } catch (const nlohmann::json_abi_v3_11_3::detail::parse_error& e) {
        throw std::invalid_argument("Error: Failed to parse database_details.json: " + std::string(e.what()));
    }

    std::unordered_set<std::string> expected_keys = {"host", "name", "user", "password"};
    std::unordered_set<std::string> db_details_keys;
    std::unordered_map<std::string, std::string> db_details;

    for (auto it = db_details_json.begin(); it != db_details_json.end(); ++it) {
        db_details_keys.insert(it.key());
        db_details[it.key()] = it.value();
    }

    if (db_details_keys != expected_keys) {
        throw std::invalid_argument("Error: database_details.json format incorrect, program not run");
    }

    return db_details;
}
