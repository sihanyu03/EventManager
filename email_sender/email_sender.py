from recipient import Recipient
import logging
import os
import sys
import yaml
import smtplib
import threading
from concurrent.futures import ThreadPoolExecutor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from events import emails


class EmailSender:
    def __init__(self, logger: logging.Logger, rows: list[tuple[str, ...]]):
        """
        :param rows: Data from the SQL table
        """
        self.logger = logger
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

    def send_email(self, project_path: str, event: str, subject: str, account: str, attachment=None) -> None:
        """
        Sends the personalised emails given the subject and the list of recipients

        :param project_path: Path of the project directory
        :param event: Name of the event, used for logging
        :param subject: Subject of the email
        :param account: The account that the emails are sent from, e.g. chair, societies
        :param attachment: Path to the attachment image/logo in the end of the email
        :return:
        """
        self.logger.info(f'{event}: Starting email sending process')

        try:
            with open(os.path.join(project_path, 'email_details',
                                   f'email_details_{account}.yaml'), 'r') as file:
                email_details = yaml.safe_load(file)
        except FileNotFoundError:
            error_msg = f'emails_details_{account}.yaml file not found, emails not sent'
            self.logger.error(error_msg)
            sys.exit(f'Error: {error_msg}')

        if set(email_details.keys()) != {'email', 'password'}:
            self.logger.error('Emails not sent, email details reading failed due to invalid format')
            return

        def send_one(sender_email, recipient_email, text):
            server = None
            try:
                smtp_server = 'smtp.gmail.com'  # Gmail's SMTP server address
                smtp_port = 587

                server = smtplib.SMTP(smtp_server, smtp_port)  # Connection to Gmail SMTP server
                server.starttls()  # Transport layer security, ensures secure communication
                server.login(email_details['email'], email_details['password'])

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(text, 'html'))
                if attachment is not None:
                    msg.attach(img)

                server.sendmail(email_details['email'], recipient_email, msg.as_string())
                self.logger.info(f'{event}: Email to {recipient_email} sent successfully')
            except Exception as e:
                self.logger.error(f'{event}: Failed to send email: {e}')
                with failed_emails_lock:
                    failed_emails.append(recipient_email)
            finally:
                if server is not None:
                    server.quit()

        if attachment:
            with open(os.path.join(project_path, attachment), 'rb') as file:
                img = MIMEImage(
                    file.read())  # Use MIMEImage to ensure the image isn't an attachment but is embedded inline
                img.add_header('Content-ID', '<image>')  # Define the content-id of the image (cid:image)
                img.add_header('Content-Disposition', 'inline', filename=attachment)  # Display it inline

        max_workers = 30  # Specify maximum number of threads to prevent thread number becoming too high
        failed_emails = []  # List of emails that sending failed
        failed_emails_lock = threading.Lock()  # Create lock to prevent multiple threads accessing failed_emails list at
        # once
        with ThreadPoolExecutor(max_workers=max_workers) as executor:  # With block automatically shuts it down after
            futures = []
            for recipient in self.recipients:
                # Execute all emails by adding them to the queue, and adding the returned Future object into 'futures'
                futures.append(executor.submit(send_one, email_details['email'], recipient.email, recipient.text))

            for future in futures:
                future.result()  # Wait until all threads are finished

        # Log failed emails
        if failed_emails:
            error_msg = ['Failed to send these emails:']
            for failed_email in failed_emails:
                error_msg.append('\t' * 12 + failed_email)
            self.logger.error('\n'.join(error_msg))
