import utils
import psycopg2
from langchain_core.tools import tool


@tool
def check_if_email_exists(email: str, table: str):
    """
    Checks if email exists in a table.

    Args:
        email: the email to check if exists
        table: the name of the table from which to check if the given email exists

    Returns: True if the email exists, False if the email doesn't exist, the error message if there was an error
    """
    logger.info(f'check_if_email_exists - Called with parameters email={email}, table={table}')
    if not utils.check_sql_variable_validity(table):
        logger.error(f'check_if_email_exists - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'
    try:
        sql_cur.execute(
            f"SELECT EXISTS (SELECT 1 FROM {table} WHERE email = %s);",
            (email,)
        )
        if sql_cur.fetchall()[0][0]:
            return_val = f'The email {email} is in the table {table}'
        else:
            return_val = f'The email {email} is not in the table {table}'
        logger.info(f'check_if_email_exists - Returned {return_val}')
        return return_val
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'check_if_email_exists - Error: {str(e)}')
        return str(e)


@tool
def retrieve_non_cam_and_typo_emails(table: str):
    """
    Count how many emails in the given SQL table aren't in the Cambridge University email format,
    i.e. have a domain of @cam.ac.uk, and retrieve those emails. Also count how many emails are typos
    of the Cambridge University domain, i.e. are close to @cam.ac.uk
    """
    logger.info(f'retrieve_non_cam_and_typo_emails - Called with parameters table={table}')
    if not utils.check_sql_variable_validity(table):
        logger.info(f'retrieve_non_cam_and_typo_emails - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'
    try:
        sql_cur.execute(
            f"SELECT email FROM {table} WHERE email NOT LIKE '%cam.ac.uk'"
        )
        non_cam = []
        typos = []
        for elem in sql_cur.fetchall():
            idx = elem[0].index('@')
            domain = elem[0][idx:]
            if utils.hamming_distance(domain, '@cam.ac.uk') <= 2:
                typos.append(elem[0])
            else:
                non_cam.append(elem[0])
        logger.info(f'retrieve_non_cam_and_typo_emails - Returned {len(non_cam)} non-Cambridge emails and {typos} typo emails')
        return f'The number of non-Cambridge domain emails are {len(non_cam)}, Non-Cambridge domain emails are {non_cam}. The number of Cambridge domain emails with typos is {len(typos)}, Cambridge domain emails with typos are {typos}'
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'retrieve_non_cam_and_typo_emails - Error: {str(e)}')
        return str(e)


@tool
def correct_typo_emails(emails: list[str], table: str) -> str:
    """
    Update and correct email address typos in a specified SQL table

    This tool corrects emails in the given SQL table where there are typos,
    based on the provided list of emails. For each email in the list, the function updates the corresponding
    row in the database to reflect the corrected email.

    After this function is over, you should tell the user that the correction is successful

    Args:
        emails: List of emails with typos to be corrected
        table: The name of the SQL table to update
    """
    logger.info(f'correct_typo_emails - Called with parameters emails={emails}, table={table}')
    if not utils.check_sql_variable_validity(table):
        logger.info(f'correct_typo_emails - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'

    successful_emails = []
    failed_emails = []
    try:
        for email in emails:
            idx = email.index('@')
            new_email = email[:idx] + '@cam.ac.uk'
            try:
                sql_cur.execute(
                    f'UPDATE {table} SET email = %s WHERE email = %s',
                    (new_email, email)
                )
                successful_emails.append((email, 'successful'))
            except psycopg2.Error as psycopg2_e:
                failed_emails.append((email, str(psycopg2_e)))
        sql_conn.commit()
        logger.info(f'correct_typo_emails - Returned successful emails={successful_emails}, failed email = {failed_emails}')
        return f'Emails that were successfully fixed: {successful_emails}, emails that failed to be fixed: {failed_emails}'
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'correct_typo_emails - Error: {str(e)}')
        return str(e)


@tool
def create_table(table: str, columns: list[str]):
    """
    Given a table name and columns, create a SQL table using those

    If no error occurred, this the table is now successfully created, tell this to the user

    Args:
          table: Name of the table to be created
          columns: List of the column names
    """
    logger.info(f'create_table - Called with parameters table={table}, columns={columns}')
    if not utils.check_sql_variable_validity(table):
        logger.error(f'create_table - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'
    if not all(utils.check_sql_variable_validity(col) for col in columns):
        logger.error(f'create_table - Error: Column name(s) invalid')
        return 'Invalid column names, all characters must be alphanumeric or the underscore _ character'

    query = [f'CREATE TABLE {table} (id SERIAL PRIMARY KEY,'] + [
        f'{col} VARCHAR(255),' if col != 'email' else 'email VARCHAR(255) UNIQUE,' for col in columns
    ]
    query[-1] = query[-1][:-1]
    query.append(');')
    query = ''.join(query)

    try:
        sql_cur.execute(query)
        sql_conn.commit()
        logger.info(f'create_table - Table {table} successfully created')
        return f'Table {table} creation successful'
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'create_table - Error: {str(e)}')
        return str(e)


@tool
def delete_table(table: str):
    """Given the name of the SQL database table, delete the whole table."""
    logger.info(f'delete_table - Called with parameter table={table}')
    if not utils.check_sql_variable_validity(table):
        logger.info('delete_table - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'

    try:
        sql_cur.execute(
            f'DROP TABLE {table}'
        )
        sql_conn.commit()
        logger.info(f'delete_table - Table {table} successfully deleted')
        return f'Table {table} deletion successful'
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'delete_table - Error: {str(e)}')
        return str(e)


@tool
def insert_into_sql_table(table: str, cols):
    """
    Given a SQL table and the values associated with each column, insert a row using the values

    After this is done, tell the user that the row was successfully added, if no error occurred

    Args:
         table: Name of the table
         cols: A dictionary containing column-value pairs, where the key is the column, and the value is the value for
         that column to be inserted into the SQL table
    """
    logger.info(f'insert_into_sql_table - Called with parameters table={table}, cols={cols}')
    if not cols:
        logger.error('insert_into_sql_table - Error: No column value pairs were provided')
        return 'Error, no column value pairs provided.'
    if not utils.check_sql_variable_validity(table):
        logger.error('insert_into_sql_table - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'

    columns = ','.join(cols.keys())
    placeholders = ','.join(['%s'] * len(cols))
    values = tuple(cols.values())
    query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'

    try:
        sql_cur.execute(query, values)
        sql_conn.commit()
        logger.info('insert_into_sql_table - Inserting row was successful')
        return f'Inserting the row was successful'
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'insert_into_sql_table - Error: {str(e)}')
        return str(e)


@tool
def retrieve_table_length(table: str):
    """Given the name of a SQL table, retrieve the length of the table"""
    logger.info(f'retrieve_table_length - Called with parameter table={table}')
    if not utils.check_sql_variable_validity(table):
        logger.error(f'retrieve_table_length - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'

    try:
        sql_cur.execute(f'SELECT COUNT(*) FROM {table}')
        result = sql_cur.fetchone()[0]
        logger.info(f'retrieve_table_length - Returned {result} as the length of the table {table}')
        return f'The query gave the length of {table} as {result}'
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'retrieve_table_length - Error: {str(e)}')
        return str(e)


@tool
def modify_element(table: str, identifier_column_name: str, identifier_value: str , column_to_be_modified: str, new_value: str):
    """
    Given a table, an identifier column and its value, modify a cell in that row with a new value given by new_value,
        on the column column_to_be_modified. After its finished, tell the user that the row was successfully modified if no error occurred

    Args:
        table: The name of the SQL table that the modification should occur
        identifier_column_name: The column that will be used to identify the row that will be modified
        identifier_value: The value that the identifier_column_name has to equal to, to find the row to be modified
        column_to_be_modified: The column that will be modified
        new_value: The new value that will be put into the column_to_be_modified column
    """
    logger.info(f'modify_element - Called with parameters table={table}, identifier_column_name={identifier_column_name}, identifier_value={identifier_value}, column_to_be_modified={column_to_be_modified}, new_value={new_value}')
    if not utils.check_sql_variable_validity(table):
        logger.error('modify_element - Error: Table name invalid')
        return 'Invalid table name, all characters in the table have to be alphanumeric or the underscore _ character'
    if not utils.check_sql_variable_validity(identifier_column_name) or not utils.check_sql_variable_validity(column_to_be_modified):
        logger.error('modify_element - Error: Column name(s) invalid')
        return 'Invalid column names, all characters in the table have to be alphanumeric or underscode _ character'

    try:
        sql_cur.execute(
            f'UPDATE {table} SET {column_to_be_modified} = %s WHERE {identifier_column_name} = %s RETURNING {column_to_be_modified}',
            (new_value, identifier_value)
        )
        prev_value = sql_cur.fetchone()[0]
        sql_conn.commit()
        logger.info(f'modify_element - Row successfully updated, value {prev_value} updated to {new_value}')
        return f'Row updated, value {prev_value} successfully updated to {new_value}'
    except Exception as e:
        sql_conn.rollback()
        logger.error(f'modify_element - Error: {str(e)}')
        return str(e)


tools = [
    check_if_email_exists,
    retrieve_non_cam_and_typo_emails,
    correct_typo_emails,
    create_table,
    delete_table,
    insert_into_sql_table,
    retrieve_table_length,
    modify_element
]
sql_conn = psycopg2.connect(
    host='localhost',
    database='postgres',
    user='sihanyu',
    password='password'
)
sql_cur = sql_conn.cursor()

logger = utils.get_logger()