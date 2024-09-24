from logging import Logger
import os
from time import time
import smtplib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pandas as pd
import yaml

from email_content import EmailContent


class EmailSender:
    def __init__(self, logger: Logger, executor: ThreadPoolExecutor, project_path: str, event_details: dict[str],
                 account: str, total_emails: int, progress_bar_len: int):
        """
        :param logger: Reuse the same configured logger
        :param executor: ThreadPoolExecutor to be used to execute threads
        :param project_path: Path of the project directory
        :param event_details: Dictionary of all necessary details of the event
        :param account: Email account where the emails are going to be sent from
        :param total_emails: Total number of emails to be sent, used in progress bar
        :param progress_bar_len: Number of characters in the live progress bar
        """
        self.logger = logger
        self.executor = executor
        self.thread_local = threading.local()
        self.project_path = project_path
        self.event_details = event_details
        self.account = account
        self.emails_sent = 0  # Modified, but is only used by main thread
        self.total_emails = total_emails
        self.batch_no = 0  # Modified, but is only used by main branch
        self.email_details = self.get_email_details()
        self.progress_bar_len = progress_bar_len
        self.start_time = time()

        self.img = None
        self.make_img()

        self.num_emails_attempted = 0  # Modified, but is only used in main thread

        self.successful_emails = []  # Modified, not thread safe
        self.failed_emails = []  # Modified, not thread safe

        self.successful_emails_lock = threading.Lock()
        self.failed_emails_lock = threading.Lock()

        self.active_smtp_conns = set()  # Modified, not thread safe
        self.active_smtp_conns_lock = threading.Lock()

        self.smtp_count = 0  # Modified, not thread safe
        self.smtp_count_lock = threading.Lock()

        self.failed_smtp_count = 0  # Modified, not thread safe
        self.failed_smtp_count_lock = threading.Lock()

    def __enter__(self):
        return self

    def send_emails(self, email_contents: list[EmailContent]) -> None:
        """
        Sends all the emails given a list of EmailContent objects
        :param email_contents: List of EmailContent objects that govern the emails that will be sent
        :return: None
        """
        self.batch_no += 1
        batch_start_time = time()

        futures = [self.executor.submit(self.send_one, email_content) for email_content in email_contents]

        num_successful_emails = 0
        for future in as_completed(futures):
            num_successful_emails += future.result()
            self.num_emails_attempted += 1

            # Update progress bar
            stars = int((self.emails_sent + num_successful_emails) / self.total_emails * self.progress_bar_len)
            dashes = self.progress_bar_len - stars

            prediction_of_remaining = (self.total_emails - self.num_emails_attempted) * (time() - self.start_time) / self.num_emails_attempted
            predicted_mins, predicted_secs = map(int, divmod(prediction_of_remaining, 60))

            print(f"\rBatch number {self.batch_no}, Progress: {'*' * stars}{'-' * dashes} "
                  f"{self.emails_sent + num_successful_emails}/{self.total_emails} emails sent. Time remaining "
                  f"{predicted_mins} minutes and {predicted_secs} seconds", end='')

        mins, secs = divmod(time() - batch_start_time, 60)
        mins, secs = int(mins), round(secs, 2)
        self.logger.info(
            f'Batch number {self.batch_no} sent. {num_successful_emails}/{len(email_contents)} sent successfully in '
            f'{mins} minutes and {secs} seconds')

        self.emails_sent += num_successful_emails

    def get_smtp(self, new_attempt=False) -> smtplib.SMTP:
        """
        Retrieves the SMTP server connection object for the current thread from the thread local storage,
            self.thread_local object. If it's the first time for the thread that this function is called, retrieve the
            server connection object
        :return: SMTP object corresponding to the current thread
        """
        if new_attempt or not hasattr(self.thread_local, 'smtp'):
            if new_attempt and hasattr(self.thread_local, 'smtp'):
                self.thread_local.smtp.quit()
                with self.smtp_count_lock:
                    self.smtp_count -= 1
                    self.logger.info(f'Disconnected SMTP connection with id {id(self.thread_local.smtp)} stopped, remaining: {self.smtp_count}')
                with self.failed_smtp_count_lock:
                    self.failed_smtp_count += 1

            smtp_server = 'smtp.gmail.com'  # Gmail's SMTP server address
            smtp_port = 587

            smtp = smtplib.SMTP(smtp_server, smtp_port)  # Connection to Gmail SMTP server
            smtp.starttls()  # Transport layer security, ensures secure communication
            smtp.login(self.email_details['email'], self.email_details['password'])
            self.thread_local.smtp = smtp

            with self.active_smtp_conns_lock:
                self.active_smtp_conns.add(smtp)

            with self.smtp_count_lock:
                self.smtp_count += 1
                self.logger.info(f'SMTP connection with id {id(smtp)} started, number of live connections: {self.smtp_count}')

        return self.thread_local.smtp

    def send_one(self, email_content: EmailContent) -> int:
        """
        Connect to Gmail SMTP server and send one email
        :param email_content: An EmailContent object containing information about the email, namely address and the body
        :return: 1 if successful, 0 if not successful
        """
        smtp = None
        try:
            smtp = self.get_smtp()

            try:
                smtp.noop()
            except smtplib.SMTPException:
                smtp = self.get_smtp(new_attempt=True)

            msg = MIMEMultipart()
            msg['From'] = self.email_details['email']
            msg['To'] = email_content.email
            msg['Subject'] = self.event_details['subject']
            msg.attach(MIMEText(email_content.body, 'html'))
            if self.img is not None:
                msg.attach(self.img)

            smtp.sendmail(self.email_details['email'], email_content.email, msg.as_string())
            self.logger.info(f'Email to {email_content.email} sent successfully with SMTP id: {id(smtp)}')

            with self.successful_emails_lock:
                self.successful_emails.append(email_content.email)
            return 1

        except Exception as e:
            self.logger.error(f'Failed to send email to {email_content.email} using smtp connection {id(smtp) if smtp is not None else 'None'}: {e}')
            with self.failed_emails_lock:
                self.failed_emails.append(email_content.email)
            return 0

    def make_img(self) -> None:
        """
        Retrieve the attachment as a usable object or None if there is no attachment
        :return: MIMEImage object if the email contains an attachment
        """
        if self.event_details['attachment'] is not None:
            with open(os.path.join(self.project_path, 'attachments', self.event_details['attachment']), 'rb') as file:
                # Use MIMEImage to ensure the image isn't an attachment but is embedded inline
                img = MIMEImage(file.read())

                # Define the content-id of the image (cid:image)
                img.add_header('Content-ID', '<image>')

                # Display it inline
                img.add_header('Content-Disposition', 'inline', filename=self.event_details['attachment'])
            self.img = img

    def __exit__(self, exc_type, exc_val, exc_tb):
        for smtp in self.active_smtp_conns:
            try:
                smtp.quit()
                with self.smtp_count_lock:
                    self.smtp_count -= 1
                    self.logger.info(f'SMTP connection with id {id(smtp)} stopped, remaining: {self.smtp_count}')
            except smtplib.SMTPServerDisconnected:
                self.logger.error(f"A thread's SMTP server connection with id {id(smtp)} doesn't exist when trying to stop the connection")
        self.logger.info(f'Number of failed and restarted SMTP connections: {self.failed_smtp_count}')
        self.write_excel_report()

    def get_email_details(self) -> dict[str]:
        """
        Retrieve the details of the email where emails are sent from
        :return: Dictionary of the email's address and password
        """
        try:
            with open(os.path.join(self.project_path, 'email_details',
                                   f'email_details_{self.account}.yaml'), 'r') as file:
                email_details = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f'emails_details_{self.account}.yaml file not found, emails not sent')

        if set(email_details.keys()) != {'email', 'password'}:
            raise ValueError('Emails not sent, email details reading failed due to invalid format')

        return email_details

    def write_excel_report(self):
        """
        Writes 2 Excel files, one containing all successful emails, and one all failed emails
        :return: None
        """
        try:
            series_successful = pd.Series(self.successful_emails, name='successful_emails')
            series_successful.index = range(1, len(self.successful_emails) + 1)
            series_successful.index.name = 'num'
            series_successful.to_excel('successful_emails.xlsx')

            series_failed = pd.Series(self.failed_emails, name='failed_emails')
            series_failed.index = range(1, len(self.failed_emails) + 1)
            series_failed.index.name = 'num'
            series_failed.to_excel('failed_emails.xlsx')

            self.logger.info('Successfully written Excel email reports')
        except Exception as e:
            raise RuntimeError(f'Error: Excel report writing unsuccessful: {e}')
