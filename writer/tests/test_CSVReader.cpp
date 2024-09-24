#include <iostream>
#include <vector>
#include <gtest/gtest.h>
#include "../src/CSVReader.h"

class CSVReaderTest : public :: testing::Test {
public:
    std::string project_path;
private:
    void SetUp() override {
        this->project_path = "/Users/sihanyu/Documents/Programming/Github/EventManager/writer/tests/test_files";
    }
    void TearDown() override {}
};

TEST_F(CSVReaderTest, successful_test_1) {
    const auto event_key = "test_1";
    const auto [doc, csv_cols, csv_cols_set] {CSVReader::get_doc(this->project_path, event_key)};

    EXPECT_EQ(doc.GetColumnCount(), 3);
    EXPECT_EQ(doc.GetRowCount(), 1);
    EXPECT_EQ(doc.GetCell<std::string>("first_name", 0), "firstname");
    EXPECT_EQ(doc.GetCell<std::string>("last_name", 0), "lastname");
    EXPECT_EQ(doc.GetCell<std::string>("crsid", 0), "abc123");

    const std::vector<std::string> expected_cols_vector = {"first_name", "last_name", "crsid"};
    EXPECT_EQ(csv_cols, expected_cols_vector);

    const std::unordered_set<std::string> expected_cols_set = {"first_name", "last_name", "crsid"};
    EXPECT_EQ(csv_cols_set, expected_cols_set);
}

TEST_F(CSVReaderTest, duplicate_names) {
    const auto event_key = "test_2";
    EXPECT_THROW(CSVReader::get_doc(this->project_path, event_key), std::invalid_argument);
}

TEST_F(CSVReaderTest, duplicate_emails) {
    const auto event_key = "test_3";
    EXPECT_THROW(CSVReader::get_doc(this->project_path, event_key), std::invalid_argument);
}