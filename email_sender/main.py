from recipient import Recipient
from events import emails
from email_sender import EmailSender
from database import Database


event_key = input('Enter the event key identifier of the event: ')
while event_key not in emails:
    print('Invalid input, enter a valid event key, or add the event to the events.py file')
    event_key = input('Enter a valid event key identifier: ')

available_accounts = {'chair', 'colleges'}
account = input('Enter the account from which you want to send (chair, colleges): ')
while account not in available_accounts:
    print('Invalid input, enter an existing account or add the account details as a json file')
    account = input('Enter a valid account: ')

rows = Database.get_rows(emails[event_key]['table_name'])

recipients = []
for row in rows:
    first_name = row[0]
    email = row[1]

    text = emails[event_key]['text'].format(first_name=first_name)

    recipients.append(Recipient(
        email=email,
        text=text
    ))

confirm = input(f'Emails successfully gathered, are you sure you want to send {len(rows)} email(s)? type yes or no: ')
while confirm not in ['yes', 'no']:
    confirm = input(f'Invalid input, please confirm sending {len(rows)} emails by typing yes or no')

if confirm == 'yes':
    EmailSender.send_email(emails[event_key]['name'], emails[event_key]['subject'], recipients, account=account,
                           attachment=emails[event_key]['attachment'])
    print('Emails sent')
else:
    print('Emails not sent')
