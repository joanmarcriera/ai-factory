import logging
import os
from pathlib import Path

def setup_logger(name, log_level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create logs directory if it does not exist
    logs_dir = Path('logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create console handler and set level to log_level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create file handler and set level to log_level
    file_handler = logging.FileHandler(logs_dir / 'monitor.log')
    file_handler.setLevel(log_level)

    # Create formatter and set format to include timestamp, logger name, level, and message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

default_logger = setup_logger('monitor')
