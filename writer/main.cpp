#include <iostream>
#include "fstream"
#include <nlohmann//json.hpp>
#include <rapidcsv.h>
#include "CSVReader.h"
#include "Database.h"

using json = nlohmann::json;

int main() {
    Database db;

    if (const std::string db_status = db.get_status(); db_status != "OK") {
        std::cout << db_status << std::endl;
        return 1;
    }

    std::string operation;
    std::string table_name;
    std::string file_name;

    std::cout << "Enter the operation you want to perform (create or update): ";
    std::cin >> operation;
    if (operation != "create" && operation != "update") {
        std::cout << "Error: invalid operation entered, should be 'create' or 'update'" << std::endl;
        return 1;
    }
    std::cout << "Enter the name of the table you want to " + operation + ": ";
    std::cin >> table_name;
    std::cout << "Enter the name of the file you want to read from: ";
    std::cin >> file_name;
    std::cout << std::endl;

    bool exists;
    try {
        exists = db.table_exists(table_name);
    } catch (const std::runtime_error& e) {
        std::cout << e.what() << std::endl;
        return 1;
    }

    rapidcsv::Document doc;
    try {
        doc = CSVReader::get_doc(file_name);
    } catch (const std::__1::ios_base::failure& e) {
        std::cout << e.what() << std::endl;
        return 1;
    }

    std::vector<std::string> cols;
    if (operation == "create") {
        if (exists) {
            std::cout << "Error: tried to create a table that already exists" << std::endl;
            return 1;
        }
        try {
            db.create_table(doc.GetColumnNames(), table_name);
        } catch (const std::runtime_error& e) {
            std::cout << e.what() << std::endl;
            return 1;
        }
        cols = doc.GetColumnNames();
    } else {
        if (!exists) {
            std::cout << "Error: tried to update table that doesn't exist" << std::endl;
            return 1;
        }

        try {
            cols = db.retrieve_cols(doc, table_name);
        } catch (const std::runtime_error& e) {
            std::cout << e.what() << std::endl;
            return 1;
        }
    }

    try {
        db.write_rows(doc, cols, table_name);
    } catch (const std::runtime_error& e) {
        std::cout << e.what() << std::endl;
    }

    db.commit();

    std::cout << "Database operation successful" << std::endl;

    return 0;
}
