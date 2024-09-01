#ifndef CSVREADER_H
#define CSVREADER_H
#include <rapidcsv.h>


class CSVReader {
public:
    static rapidcsv::Document get_doc(const std::string& file_name);
};



#endif //CSVREADER_H
