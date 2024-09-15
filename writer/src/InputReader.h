#ifndef INPUTREADER_H
#define INPUTREADER_H
#include <iostream>

enum class Operation {
    Create, Update
};

struct Input {
    Operation operation;
    std::string table_name;
    std::string file_name;
};

class InputReader {
public:
    /**
     * Prompts the user for the necessary inputs of operation type, table name, and CSV file name
     *
     * @return An Input instance containing the user inputs
     */
    [[nodiscard]] static Input get_input();
};


#endif //INPUTREADER_H
