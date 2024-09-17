cmake_minimum_required(VERSION 3.28)
set(CMAKE_CXX_STANDARD 20)

project(tests)

include(FetchContent)

FetchContent_Declare(googletest URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

FetchContent_Declare(
        rapidcsv
        GIT_REPOSITORY "https://github.com/d99kris/rapidcsv.git"
        GIT_TAG        "v8.50"
)
FetchContent_MakeAvailable(rapidcsv)

FetchContent_Declare(
        yaml-cpp
        GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
        GIT_TAG master
)
FetchContent_MakeAvailable(yaml-cpp)

link_directories(/opt/homebrew/lib)
include_directories(/opt/homebrew/include)

enable_testing()

add_executable(
        tests
        test_CSVReader.cpp
        ../src/CSVReader.cpp
        ../src/Database.cpp
)

target_link_libraries(tests GTest::gtest_main)
target_link_libraries(tests rapidcsv)
target_link_libraries(tests pqxx)
target_link_libraries(tests yaml-cpp::yaml-cpp)

include(GoogleTest)
gtest_discover_tests(tests)