from recipient import Recipient
from events import emails
from email_sender import EmailSender
from database import Database


event_key = input('Enter the event key identifier of the event: ')
while event_key not in emails:
    print('Invalid input, enter a valid event key, or add the event to the events.py file')
    event_key = input('Enter a valid event key identifier: ')

rows = Database.get_rows(emails[event_key]['table_name'])

recipients = []
for row in rows:
    first_name = row[0]
    crsid = row[1]

    text = emails[event_key]['text'].format(first_name=first_name)

    recipients.append(Recipient(
        email=f'{crsid}@cam.ac.uk',
        text=text
    ))

confirm = input(f'Emails successfully gathered, are you sure you want to send {len(rows)} emails? type yes or no: ')
while confirm not in ['yes', 'no']:
    confirm = input(f'Invalid input, please confirm sending {len(rows)} emails by typign yes or no')

if confirm == 'yes':
    EmailSender.send_email(emails[event_key]['name'], emails[event_key]['subject'], recipients)
    print('Emails sent')
else:
    print('Emails not sent')
