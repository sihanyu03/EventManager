import os


class InputReader:
    @staticmethod
    def get_input(emails: dict) -> tuple[str, str]:
        """
        Reads user inputs on the event and email to send from

        :param emails: Dictionary of the details of the email
        :return: event_key, the string key of the event, and account, the email account to send from
        """
        event_key = input('Enter the event key identifier of the event: ')
        while event_key not in emails:
            print('Invalid input, enter a valid event key, or add the event to the events.py file')
            event_key = input('Enter a valid event key identifier: ')

        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        available_accounts = set(file[14:-5] for file in os.listdir(os.path.join(parent_dir, 'email_details')) if
                                 file.startswith('email_details_'))

        account = input(f'Enter the account from which you want to send {available_accounts}: ')
        while account not in available_accounts:
            print('Invalid input, enter an existing account or add the account details as a yaml file')
            account = input('Enter a valid account: ')

        return event_key, account
