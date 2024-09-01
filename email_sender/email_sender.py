from recipient import Recipient
import logging
import os
import sys
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'email_sender.log'),
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


class EmailSender:
    @staticmethod
    def send_email(event: str, subject: str, recipients: list[Recipient]) -> None:
        """
        Sends the personalised emails given the subject and the list of recipients
        :param event: Name of the event, used for logging
        :param subject: Subject of the email
        :param recipients: List of Recipient object instances. Each Recipient instance contains their email address
            and personalised message
        :return:
        """
        logging.info(f'{event}: Starting email sending process')

        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_details.json'), 'r') as file:
                email_details = json.load(file)
        except FileNotFoundError:
            logging.error('emails_details.json file not found, emails not sent')
            sys.exit('Error, emails not sent. Check logs for more details')

        if set(email_details.keys()) != {'email', 'password'}:
            logging.error('Emails not sent, email details reading failed due to invalid format')
            return

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_details['email'], email_details['password'])

            for recipient in recipients:
                msg = MIMEMultipart()
                msg['From'] = email_details['email']
                msg['To'] = recipient.email
                msg['Subject'] = subject
                msg.attach(MIMEText(recipient.text, 'html'))

                server.sendmail(email_details['email'], recipient.email, msg.as_string())
                logging.info(f'{event}: Email to {recipient.email} sent successfully')

            server.quit()

        except Exception as e:
            logging.error(f'{event}: Failed to send email: {e}')

        finally:
            logging.info(f'{event}: Finished email sending process')
