import os
import yaml


class InputReader:
    @staticmethod
    def get_events(events_path: str) -> set[str]:
        """
        :param events_path: Path of the events folder where all events should be defined
        :return: A set of all defined events
        """
        return set(file for file in os.listdir(events_path) if not file.startswith('.') and file != 'example')

    @staticmethod
    def get_accounts(emails_path: str) -> set[str]:
        """
        :param emails_path: Path of the email_details folder where all emails should be defined
        :return: A set of all defined emails
        """
        return set(file[14:-5] for file in os.listdir(emails_path) if
                   file.startswith('email_details_') and file != 'email_details_example.yaml')

    @staticmethod
    def get_input(project_path: str) -> tuple[dict[str], str]:
        """
        Reads user inputs on the event and email to send from
        :param project_path: Path of the project directory
        :return: event_details: dictionary containing all the necessary details of the event, as defined in the event's
            yaml file, account: the email account where the emails are going to be sent from
        """
        events_path = os.path.join(project_path, 'events')
        emails_path = os.path.join(project_path, 'email_details')

        available_events = InputReader.get_events(events_path)
        event_key = input('Enter the event key identifier of the event: ')
        while event_key not in available_events:
            print('Invalid input, event key not found')
            print(f'\tAvailable event keys: {', '.join(available_events)}')
            event_key = input('Enter a valid event key identifier: ')

        with open(os.path.join(events_path, event_key, event_key + '.yaml')) as file:
            event_details = yaml.safe_load(file)

        available_accounts = InputReader.get_accounts(emails_path)
        account = input(f'Enter the account from which you want to send: {', '.join(available_accounts)}: ')
        while account not in available_accounts:
            print('Invalid input, account not found')
            print(f'\tAvailable accounts: {', '.join(available_accounts)}')
            account = input('Enter a valid account: ')

        event_details['table_name'] = event_key
        return event_details, account
