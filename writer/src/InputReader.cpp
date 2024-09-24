#include <iostream>
#include "InputReader.h"


std::pair<Operation, std::string> InputReader::get_input() {
    std::string operation_str;
    std::string event_name;

    std::cout << "Enter the operation you want to perform (create or update): ";
    std::cin >> operation_str;
    if (operation_str != "create" && operation_str != "update") {
        throw std::invalid_argument("Error: Invalid operation entered, should be 'create' or 'update'");
    }
    std::cout << "Enter the name of the event: ";
    std::cin >> event_name;

    const auto operation = operation_str == "create" ? Operation::Create : Operation::Update;
    return {operation, event_name};
}
