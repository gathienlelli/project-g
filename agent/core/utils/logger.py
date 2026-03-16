import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = r"G:\agent\logs\python"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name="agent"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    log_file = os.path.join(LOG_DIR, f"{name}.log")

    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger
