from time import time
import sys
from concurrent.futures import ThreadPoolExecutor

from email_sender import EmailSender
from database import Database
from input_reader import InputReader
import utils

project_path = '/Users/sihanyu/Documents/Programming/Github/EventManager'


def main():
    try:
        event_details, account = InputReader.get_input(project_path)
    except FileNotFoundError as e:
        sys.exit(str(e))

    utils.check_event_details_validity(event_details)

    logger = utils.get_logger(event_details['name'])
    db = None

    try:
        # Initialise database connection
        db = Database(
            logger=logger,
            cols=event_details['cols'],
            project_path=project_path,
            table_name=event_details['table_name'],
            grouping_requirement=event_details['grouping_requirement']
        )

        no_of_emails = db.length
        if no_of_emails == 0:
            raise AttributeError('Error: No emails found, table is empty')

        suffix = 's' if no_of_emails != 1 else ''
        confirm = utils.get_confirmation(no_of_emails, suffix)
        if confirm == 'yes':
            # Use the corresponding email sender function
            get_email_contents = utils.select_function(event_details['email_sender'])

            print('Sending emails...')
            logger.info('Starting email sending process')
            start_time = time()

            max_workers = 5
            batch_size = 40

            # Generate a live progress bar that shows the progress as a loading bar and the number of emails sent
            progress_bar_len = 30
            print(f'\rBatch number 1, Progress: {'-' * progress_bar_len} 0/{no_of_emails} emails sent', end='')

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                with EmailSender(
                    logger=logger,
                    executor=executor,
                    project_path=project_path,
                    event_details=event_details,
                    account=account,
                    total_emails=no_of_emails,
                    progress_bar_len=progress_bar_len
                ) as email_sender:
                    has_next = True
                    while has_next:
                        data, has_next = db.get_data(batch_size=batch_size)

                        email_contents = get_email_contents(data, event_details['cols'], event_details['body'])

                        email_sender.send_emails(email_contents=email_contents)

                    num_batches = email_sender.batch_no
                    num_successful_emails = email_sender.emails_sent

            mins, secs = divmod(time() - start_time, 60)
            mins, secs = int(mins), round(secs, 2)
            batch_suffix = '' if num_batches == 1 else 'es'
            print(f'\nEmails sent in {num_batches} batch{batch_suffix}, time taken: {mins} minutes and {secs} seconds')
            logger.info(f'{num_successful_emails}/{no_of_emails} emails sent successfully in {num_batches} batch{batch_suffix}, time '
                        f'taken: {mins} minutes and {secs} seconds')

        else:
            print('Emails not sent')
            logger.info(f'Email sending terminated, emails not sent')

    except Exception as e:
        utils.terminate(logger, f'Error: {str(e)}')

    finally:
        if db is not None:
            db.stop()
            logger.info('Database connection closed')
        else:
            logger.info("Database connection not disconnected as it didn't exist")
        logger.info('Finished email sending process')


if __name__ == '__main__':
    main()
