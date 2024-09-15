#include "InputReader.h"
#include <iostream>


Input InputReader::get_input() {
    std::string operation_str;
    std::string table_name;
    std::string file_name;

    std::cout << "Enter the operation you want to perform (create or update): ";
    std::cin >> operation_str;
    if (operation_str != "create" && operation_str != "update") {
        throw std::runtime_error("Error: Invalid operation entered, should be 'create' or 'update'");
    }
    std::cout << "Enter the name of the table you want to " + operation_str + ": ";
    std::cin >> table_name;

    std::cout << "Enter the name of the CSV file you want to read from: ";
    std::cin >> file_name;
    std::cout << std::endl;

    auto operation = operation_str == "create" ? Operation::Create : Operation::Update;
    return Input{operation, table_name, file_name};
}