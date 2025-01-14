import logging
import os
from typing import Any
import psycopg2
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self, logger: logging.Logger, cols: list[str], table_name: str, grouping_requirement: str):
        """
        :param logger: Reuse the same configured logger
        :param cols: Columns of the SQL table to be used in the emails
        :param table_name: Name of the SQL table, used to retrieve table size
        """

        self.logger = logger
        self.cols = cols
        self.table_name = table_name
        self.grouping_requirement = grouping_requirement
        self.conn = None
        self.cur = None
        self.groups = None
        self.group_idx = 0
        self.idx = 0
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('SQL_HOST'),
                database=os.getenv('SQL_DATABASE'),
                user=os.getenv('SQL_USER'),
                password=os.getenv('SQL_PASSWORD')
            )
        except psycopg2.OperationalError:
            raise RuntimeError('SQL table not found')

        self.cur = self.conn.cursor()
        self.length = self.get_len()

    def execute(self, query: str) -> list[tuple[Any, ...]]:
        """
        :param query: Query to be executed
        :return: Return value of the query as a matrix
        """
        try:
            self.cur.execute(query)
            return self.cur.fetchall()
        except psycopg2.errors.UndefinedTable as e:
            raise RuntimeError(f'SQL query failed: {str(e)}')

    def stop(self):
        """
        Close the database connection
        :return: None
        """
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()

    def get_len(self):
        """
        :return: Number of rows in the table, which is the same as number of emails to be sent
        """
        return self.execute(f'SELECT COUNT(*) FROM {self.table_name}')[0][0]

    def get_data(self, batch_size: int = None) -> tuple[list[tuple[Any, ...]], bool]:
        """
        Reads SQL table for data
        :param batch_size: Length of the batch, or None for no pagination
        :return: A matrix of the data and an index to continue from
        """
        if batch_size is None:  # If no pagination, return the whole table
            return self.execute(f'SELECT {','.join(self.cols)} FROM {self.table_name};'), False

        if self.grouping_requirement is None:  # If pagination and no grouping requirements, return the requested part
            self.idx += batch_size
            return (self.execute(
                f'SELECT {','.join(self.cols)} FROM {self.table_name} LIMIT {batch_size} OFFSET {self.idx - batch_size};'),
                    self.idx < self.length)

        # If pagination and a grouping requirement, ensure that one group isn't split by retrieving group by group
        if self.groups is None:
            groups = self.execute(f'SELECT DISTINCT {self.grouping_requirement} FROM {self.table_name};')
            self.groups = [elem[0] for elem in groups]

        data = []
        for group in self.groups[self.group_idx:]:
            self.group_idx += 1
            data.extend(
                self.execute(f"SELECT {','.join(self.cols)} FROM {self.table_name} WHERE {self.grouping_requirement} = '{group}';"))
            if len(data) >= batch_size:
                break

        return data, self.group_idx < len(self.groups)
