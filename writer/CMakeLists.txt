cmake_minimum_required(VERSION 3.28)
project(EventManager)
set(CMAKE_CXX_STANDARD 20)

include(FetchContent)

FetchContent_Declare(
        yaml-cpp
        GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
        GIT_TAG master
)
FetchContent_MakeAvailable(yaml-cpp)

FetchContent_Declare(
        rapidcsv
        GIT_REPOSITORY "https://github.com/d99kris/rapidcsv.git"
        GIT_TAG        "v8.50"
)
FetchContent_MakeAvailable(rapidcsv)

find_package(PostgreSQL REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBPQXX REQUIRED libpqxx)

link_directories(/opt/homebrew/lib)
include_directories(/opt/homebrew/include)

add_executable(EventManager
        src/main.cpp
        src/Database.cpp
        src/CSVReader.cpp
        src/Postgres.cpp
        src/InputReader.cpp
)

target_link_libraries(EventManager PRIVATE rapidcsv)
target_link_libraries(EventManager PRIVATE pqxx)
target_link_libraries(EventManager PRIVATE yaml-cpp::yaml-cpp)

add_subdirectory(tests)