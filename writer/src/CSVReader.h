#ifndef CSVREADER_H
#define CSVREADER_H
#include <rapidcsv.h>
#include <unordered_set>


struct CSV_data {
    rapidcsv::Document doc;
    std::vector<std::string> csv_cols;
    std::unordered_set<std::string> csv_cols_set;
};


class CSVReader {
public:
    /**
     * Given a file name, read it as CSV and return the document, vector of columns, and a set of columns, in the format of a CSV_data struct
     *
     * @param project_path Path of the overall project
     * @param event_key Name of the event, which will be the same as the CSV file and SQL table
     * @return The CSV file as a rapidcsv::Document, its columns, and its columns as a set
     */
    static CSV_data get_doc(const std::string& project_path, const std::string& event_key);
};


#endif //CSVREADER_H
