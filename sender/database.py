import logging
import os
from typing import Any
import yaml
import psycopg2


class Database:
    def __init__(self, logger: logging.Logger, cols: list[str], project_path: str, table_name: str, grouping_requirement: str):
        """
        :param logger: Reuse the same configured logger
        :param cols: Columns of the SQL table to be used in the emails
        :param project_path: Path of the project directory
        :param table_name: Name of the SQL table, used to retrieve table size
        """
        db_details = self.read_db_details(project_path)

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
                host=db_details['host'],
                database=db_details['name'],
                user=db_details['user'],
                password=db_details['password']
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

    def read_db_details(self, project_path: str) -> dict[str, str]:
        """
        Read the details required from a yaml file to connect to the database: host, name, user, password
        :param project_path: Path of the project directory
        :return: Dictionary containing the details: host, name, user, password
        """
        try:
            with open(os.path.join(project_path, 'database_details', 'database_details.yaml'), 'r') as file:
                db_details = yaml.safe_load(file)
        except FileNotFoundError:
            self.stop()
            raise FileNotFoundError('database_details.yaml file does not exist, emails not sent')
        except yaml.YAMLError:
            self.stop()
            raise ValueError('Failed to decode database_details.yaml as a yaml file, emails not sent')

        if set(db_details.keys()) != {'host', 'name', 'user', 'password'}:
            self.stop()
            raise ValueError('Database reading failed due to invalid format, emails not sent')

        return db_details

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
