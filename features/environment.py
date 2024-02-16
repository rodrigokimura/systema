import logging


def before_all(context):
    if not context.config.log_capture:
        logging.basicConfig(level=logging.DEBUG)
