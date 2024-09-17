#include <sstream>
#include <fstream>
#include <unordered_set>
#include <unordered_map>
#include <yaml-cpp/yaml.h>
#include "Database.h"

std::unordered_map<std::string, std::string> Database::read_db_details(const std::string& project_path) {
    const auto db_details_path {std::filesystem::path(project_path) / "database_details.yaml"};

    if (!std::ifstream(db_details_path)) {
        throw std::invalid_argument("Error: Failed to read database_details.yaml. Check that file exists");
    }

    YAML::Node db_details_yaml;
    try {
        db_details_yaml = YAML::LoadFile(db_details_path);
    } catch (const std::runtime_error& e) {
        throw std::invalid_argument("Error: Failed to parse database_details.yaml: " + std::string(e.what()));
    }

    std::unordered_set<std::string> expected_keys = {"host", "name", "user", "password"};
    std::unordered_set<std::string> db_details_keys;
    std::unordered_map<std::string, std::string> db_details;

    for (const auto& v : db_details_yaml) {
        db_details_keys.insert(v.first.as<std::string>());
        db_details[v.first.as<std::string>()] = v.second.as<std::string>();
    }

    if (db_details_keys != expected_keys) {
        throw std::invalid_argument("Error: 'database_details.json' format incorrect, program not run");
    }

    return db_details;
}
