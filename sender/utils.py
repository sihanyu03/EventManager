import logging
import os
import sys
from typing import Callable, Any

import email_contents_getters


def get_logger(event_name: str):
    """
    Initialise logger
    :param event_name:
    :return: Logger object that is to be used in the whole program
    """
    logger = logging.getLogger('logger')
    logging.basicConfig(
        filename=os.path.join(os.path.dirname(__file__), 'email_sender.log'),
        filemode='a',
        format=f'%(asctime)s - %(levelname)s - {event_name} - %(message)s',
        level=logging.DEBUG
    )
    return logger


def terminate(logger: logging.Logger, error_msg: str):
    logger.error(error_msg)
    sys.exit('\n' + error_msg)


def check_event_details_validity(event_details: dict[str]) -> None:
    """
    Exists the program if the event details read from yaml file are invalid
    :param event_details: Dictionary of all necessary details of the event
    :return: None
    """
    required_keys = {'name', 'table_name', 'email_sender', 'subject', 'attachment', 'cols', 'grouping_requirement',
                     'body'}
    if set(event_details.keys()) != required_keys or len(event_details.keys()) != len(required_keys):
        sys.exit('Error: Format of event yaml file not correct')


def select_function(email_sender_type: str) -> Callable[[list[tuple[Any, ...]], list[str], str], Any] | Any:
    """
    :param email_sender_type: The 'get_email_contents' function type defined in the event's yaml file
    :return: The corresponding 'get_email_contents' function associated with this specific event
    """
    if email_sender_type in [None, 'default']:
        return email_contents_getters.default_getter

    try:
        return getattr(email_contents_getters, email_sender_type)
    except AttributeError:
        raise AttributeError(f'Error: Invalid email_sender type {email_sender_type}')


def get_confirmation(number_of_emails: int, suffix: str) -> str:
    """
    Asks for confirmation to send 'number_of_emails' emails
    :param number_of_emails: Number of emails to be sent
    :param suffix: Prefix 's' if number of emails is greater than 1
    :return: 'yes' or 'no' depending on the users input
    """
    confirm = input(f'Email{suffix} successfully gathered, are you sure you want to send {number_of_emails}'
                    f' email{suffix}? type yes or no: ')
    while confirm not in ['yes', 'no']:
        confirm = input(f'Invalid input, please confirm sending {number_of_emails} email{suffix} by typing yes or no: ')

    return confirm
