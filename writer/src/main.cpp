#include <iostream>
#include <fstream>
#include "CSVReader.h"
#include "Database.h"
#include "Postgres.h"
#include "InputReader.h"


int main() {
    // Defining the path of the project where all the required files (CSV files, email details etc.) are located
    const std::string project_path {"/Users/sihanyu/Documents/Programming/Github/EventManager"};

    try {
        // Initialise SQL connection
        std::unique_ptr<Database> db {std::make_unique<Postgres>(project_path)};
        if (const std::string db_status = db->get_status(); db_status != "OK") {
            throw std::runtime_error(db_status);
        }

        // Get user input
        const auto [operation, event_key] {InputReader::get_input()};

        bool exists {db->table_exists(event_key)};

        // Get CSV data
        const auto [doc, csv_cols, csv_cols_set] {CSVReader::get_doc(project_path, event_key)};

        if (operation == Operation::Create) {
            if (exists) {
                throw std::runtime_error("Error: Tried to create a table that already exists");
            }
            db->create_table(csv_cols, event_key);
        } else {  // operation == Operation::Update
            if (!exists) {
                throw std::runtime_error("Error: Tried to update table that doesn't exist");
            }
        }

        // Write to database
        const auto cols = db->retrieve_cols(event_key);
        db->write_rows(doc, cols, csv_cols_set, event_key);

        std::cout << "Database operation successful" << std::endl;

        return 0;
    } catch (const std::runtime_error& e) {
        std::cout << e.what() << std::endl;
        return 1;
    } catch (const std::invalid_argument& e) {
        std::cout << e.what() << std::endl;
        return 1;
    }
}
