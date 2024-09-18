#ifndef INPUTREADER_H
#define INPUTREADER_H
#include <iostream>

enum class Operation {
    Create, Update
};

class InputReader {
public:
    /**
     * Prompts the user for the necessary inputs of operation type, table name, and CSV file name
     *
     * @return A pair containing the operation type and event name
     */
    [[nodiscard]] static std::pair<Operation, std::string> get_input();
};


#endif //INPUTREADER_H
