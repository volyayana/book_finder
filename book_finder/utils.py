import logging

from worker import send_error_message


def log_error(error_message: str):
    logging.error('Error occurred: %s' % error_message)
    task = send_error_message.delay(error_message)
    logging.debug('Created task with task_id: %s' % task)
