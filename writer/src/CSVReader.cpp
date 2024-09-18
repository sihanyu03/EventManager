#include "CSVReader.h"
#include <filesystem>
#include <rapidcsv.h>


CSV_data CSVReader::get_doc(const std::string& project_path, const std::string& event_key) {
    const auto file_path {std::filesystem::path(project_path) / "events" / event_key / (event_key + ".csv")};

    if (!exists(file_path)) {
        throw std::invalid_argument("Error: CSV file not found. Ensure that a corresponding CSV file named event_key.csv exists in the folder of the event");
    }

    rapidcsv::Document doc;
    try {
        doc = rapidcsv::Document(file_path.string());
    } catch (const std::__1::ios_base::failure& e) {
        throw std::runtime_error("Error: Failed to read the csv file: " + std::string(e.what()));
    }

    std::vector<std::string> csv_cols;
    try {
        csv_cols = doc.GetColumnNames();
    } catch (const std::out_of_range&) {
        throw std::invalid_argument("Error: Empty CSV file");
    }
    const std::unordered_set csv_cols_set(csv_cols.begin(), csv_cols.end());

    // Check if CSV contains email, and it's defined only once
    if (!(csv_cols_set.contains("email") ^ csv_cols_set.contains("crsid"))) {
        throw std::invalid_argument("Error: CSV file missing email or crsid, or contains both");
    }

    // Check if CSV contains name, and it's defined only once
    if (!(csv_cols_set.contains("first_name") ^ csv_cols_set.contains("name")) ||
        !(csv_cols_set.contains("last_name") ^ csv_cols_set.contains("name"))) {
        throw std::invalid_argument("Error: CSV file either missing names or has duplicates");
    }

    return CSV_data{doc, csv_cols, csv_cols_set};
}