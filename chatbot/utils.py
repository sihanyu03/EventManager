import os
import logging


def hamming_distance(a: str, b: str):
    if len(a) == len(b):
        return sum(c1 != c2 for c1, c2 in zip(a, b))
    return float('inf')


def check_sql_variable_validity(variable: str):
    return all(c.isalnum() or c == '_' for c in variable)


def get_logger():
    """
    :return: Logger object that is to be used in the whole program
    """
    logger = logging.getLogger('logger')
    logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), 'chatbot.log'),
        filemode='a',
        format=f'%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )

    return logger

