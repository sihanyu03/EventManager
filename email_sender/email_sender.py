from recipient import Recipient
import logging
import os
import sys
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from events import emails

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'email_sender.log'),
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


class EmailSender:

    def __init__(self, rows: list[tuple[str, ...]]):
        """
        :param rows: Data from the SQL table
        """
        self.recipients = []
        self.rows = rows
        self.length = len(rows)

    def get_len(self) -> int:
        """
        :return: Number of recipients
        """
        return self.length

    def fill_recipients(self, event_key: str):
        """
        :param event_key: The identifier of the event, the key in the 'events' dictionary
        :return:
        """
        for row in self.rows:
            first_name = row[0]
            email = row[1]

            text = emails[event_key]['text'].format(first_name=first_name)

            self.recipients.append(Recipient(
                email=email,
                text=text
            ))

    def send_email(self, event: str, subject: str, account: str, attachment=None) -> None:
        """
        Sends the personalised emails given the subject and the list of recipients

        :param event: Name of the event, used for logging
        :param subject: Subject of the email
        :param recipients: List of Recipient object instances. Each Recipient instance contains their email address
            and personalised message
        :param account: The account that the emails are sent from, e.g. chair, societies
        :param attachment: Path to the attachment image/logo in the end of the email
        :return:
        """
        logging.info(f'{event}: Starting email sending process')

        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_details',
                                   f'email_details_{account}.json'), 'r') as file:
                email_details = json.load(file)
        except FileNotFoundError:
            logging.error(f'emails_details_{account}.json file not found, emails not sent')
            sys.exit('Error, emails not sent. Check logs for more details')

        if set(email_details.keys()) != {'email', 'password'}:
            logging.error('Emails not sent, email details reading failed due to invalid format')
            return

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        if attachment is not None:
            with open(attachment, 'rb') as file:
                img = MIMEImage(file.read())
                img.add_header('Content-ID', '<image>')
                img.add_header('Content-Disposition', 'inline', filename=os.path.basename(attachment))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_details['email'], email_details['password'])

            for recipient in self.recipients:
                msg = MIMEMultipart()
                msg['From'] = email_details['email']
                msg['To'] = recipient.email
                msg['Subject'] = subject
                msg.attach(MIMEText(recipient.text, 'html'))
                if attachment is not None:
                    msg.attach(img)

                server.sendmail(email_details['email'], recipient.email, msg.as_string())
                logging.info(f'{event}: Email to {recipient.email} sent successfully')

            server.quit()

        except Exception as e:
            logging.error(f'{event}: Failed to send email: {e}')
            sys.exit('Error, emails not sent. Check logs for more details')

        finally:
            logging.info(f'{event}: Finished email sending process')
