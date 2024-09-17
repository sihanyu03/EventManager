import logging

import yaml
import os
import sys
import psycopg2


class Database:
    @staticmethod
    def get_rows(logger: logging.Logger, project_path: str, table_name: str, cols: list[str]) -> list[tuple[str, ...]]:
        """
        :param logger: Logger
        :param project_path: Path of the project directory
        :param table_name: Name for the table to retrieve the information
        :param cols: List of columns that are extracted from the table, in the same order that is configured in
            email_sender.py
        :return: List of rows, where each row contains the first name and the crsid
        """
        database_details = Database.read_db_details(logger, project_path)

        try:
            connection = psycopg2.connect(
                host=database_details['host'],
                database=database_details['name'],
                user=database_details['user'],
                password=database_details['password']
            )
        except psycopg2.OperationalError:
            error_msg = 'SQL table not found'
            logger.error(error_msg)
            sys.exit(f'Error: {error_msg}')

        cursor = connection.cursor()
        try:
            cursor.execute(f'SELECT {', '.join(cols)} FROM {table_name}')
            return cursor.fetchall()
        except psycopg2.errors.UndefinedTable:
            error_msg = 'Failed to read from database table'
            logger.error(error_msg)
            sys.exit(f'Error: {error_msg}')
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def read_db_details(logger, project_path: str) -> dict[str, str]:
        """
        :param logger: Logger
        :param project_path: Path of the project directory
        :return: A dictionary of the database details of host, name, user, and password that are read from
            database_details.yaml. If read values are invalid, return False
        """
        try:
            with open(os.path.join(project_path, 'database_details.yaml'), 'r') as file:
                try:
                    details = yaml.safe_load(file)
                except yaml.YAMLError:
                    logger.error('Failed to decode database_details.yaml as a yaml file, emails not sent')
                    sys.exit('Error: Failed to decode database_details.yaml as a yaml file, emails not sent')
        except FileNotFoundError:
            error_msg = "database_details.yaml file doesn't exist, emails not sent"
            logger.error(error_msg)
            sys.exit(f'Error: {error_msg}')
        if set(details.keys()) != {'host', 'name', 'user', 'password'}:
            error_msg = 'Database reading failed due to invalid format, emails not sent'
            logger.error(error_msg)
            sys.exit(f'Error: {error_msg}')

        return details
