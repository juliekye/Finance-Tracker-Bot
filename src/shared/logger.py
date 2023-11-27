import logging

from logging import Logger, handlers


def get_logger(logger_name: str, log_file_path: str, max_file_size=10000, backupCount=5) -> Logger:
    # Set up a specific logger with our desired output level
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Add the log message handler to the logger for file
    file_handler = handlers.RotatingFileHandler(log_file_path, maxBytes=max_file_size, backupCount=backupCount, encoding='utf-8')

    # Create a log message handler for console
    console_handler = logging.StreamHandler()

    # Set the formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set the formatter for both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
