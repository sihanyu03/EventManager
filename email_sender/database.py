import json
import os
import sys
import logging
import psycopg2

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'email_sender.log'),
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


class Database:
    @staticmethod
    def get_rows(table_name: str, cols: list[str]) -> list[tuple[str, ...]]:
        """
        :param table_name: Name for the table to retrieve the information
        :param cols: List of columns that are extracted from the table, in the same order that is configured in
            email_sender.py
        :return: List of rows, where each row contains the first name and the crsid
        """
        database_details = Database.read_cb_details()

        try:
            connection = psycopg2.connect(
                host=database_details['host'],
                database=database_details['name'],
                user=database_details['user'],
                password=database_details['password']
            )
        except psycopg2.OperationalError:
            logging.error('Connection to database failed, emails not sent')
            sys.exit('Error, emails not sent. Check logs for more details')

        cursor = connection.cursor()

        connection.commit()

        cursor.execute(f'SELECT {', '.join(cols)} FROM {table_name}')

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows

    @staticmethod
    def read_cb_details() -> dict[str, str]:
        """
        :return: A dictionary of the database details of host, name, user, and password that are read from
            database_details.json. If read values are invalid, return False
        """
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_details.json'), 'r') as file:
                try:
                    details = json.load(file)
                except json.decoder.JSONDecodeError:
                    logging.error('Failed to decode database_details.json as a json file, emails not sent')
                    sys.exit('Error, emails not sent. Check logs for more details')
        except FileNotFoundError:
            logging.error("database_details.json file doesn't exist, emails not sent")
            sys.exit('Error, emails not sent. Check logs for more details')
        if set(details.keys()) != {'host', 'name', 'user', 'password'}:
            logging.error('Database reading failed due to invalid format, emails not sent')
            sys.exit('Error, emails not sent. Check logs for more details')
        return details
