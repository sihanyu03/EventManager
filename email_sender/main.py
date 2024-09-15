from events import emails
from email_sender import EmailSender
from families_email_sender import FamiliesEmailSender
from database import Database
from input_reader import InputReader


event_key, account = InputReader.get_input(emails)

email_sender = FamiliesEmailSender(rows=Database.get_rows(emails[event_key]['table_name'],
                                                          cols=emails[event_key]['cols']))
email_sender.fill_recipients(event_key=event_key)

no_rows = email_sender.get_len()
confirm = input(f'Emails successfully gathered, are you sure you want to send {no_rows} email(s)? type yes or no: ')
while confirm not in ['yes', 'no']:
    confirm = input(f'Invalid input, please confirm sending {no_rows} emails by typing yes or no')

if confirm == 'yes':
    email_sender.send_email(event=emails[event_key]['name'], subject=emails[event_key]['subject'], account=account,
                            attachment=emails[event_key]['attachment'])
    print('Emails sent')
else:
    print('Emails not sent')
