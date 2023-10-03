"""Module initializing loggers"""

import logging
import sys

from . import config

_config = config.get_config()


def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, _config.logging_level))
    logger.addHandler(logging.StreamHandler(sys.stdout))
    if _config.logging_file_name:
        file_handler = logging.FileHandler(_config.logging_file_name)
        logger.addHandler(file_handler)
    return logger
