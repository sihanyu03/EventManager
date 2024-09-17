from events import emails
from email_sender import EmailSender
from families_email_sender import FamiliesEmailSender
from database import Database
from input_reader import InputReader


project_path = '/Users/sihanyu/Documents/Programming/Github/EventManager'

event_key, account = InputReader.get_input(emails)

# Initialise email_sender. Use the corresponding email sender child class required by the event
rows = Database.get_rows(emails[event_key]['table_name'], cols=emails[event_key]['cols'])
if emails[event_key]['email_sender'] == 'FamiliesEmailSender':
    email_sender = FamiliesEmailSender(rows=rows)
else:
    email_sender = EmailSender(rows=rows)

# Calculate the personalised email for each recipient
email_sender.fill_recipients(event_key=event_key)

# Confirmation from user
no_rows = email_sender.get_len()
confirm = input(f'Emails successfully gathered, are you sure you want to send {no_rows} email(s)? type yes or no: ')
while confirm not in ['yes', 'no']:
    confirm = input(f'Invalid input, please confirm sending {no_rows} emails by typing yes or no')

if confirm == 'yes':
    import time
    start = time.time()
    email_sender.send_email(project_path=project_path, event=emails[event_key]['name'],
                            subject=emails[event_key]['subject'], account=account,
                            attachment=emails[event_key]['attachment'])
    print(f'Emails sent, time taken: {round(time.time() - start, 2)} seconds')
else:
    print('Emails not sent')
