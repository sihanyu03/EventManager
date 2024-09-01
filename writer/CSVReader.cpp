#include "CSVReader.h"
#include <rapidcsv.h>


rapidcsv::Document CSVReader::get_doc(const std::string& file_name) {
    const std::filesystem::path curr_path = std::filesystem::current_path() / ".." / "..";
    const std::filesystem::path file_path = curr_path / file_name;

    try {
        rapidcsv::Document doc(file_path.string());
        return doc;
    } catch (const std::__1::ios_base::failure& e) {
        throw std::ios_base::failure("Error: Failed to read the csv file " + std::string(e.what()));
    }
}