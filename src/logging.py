from uvicorn.config import LOG_LEVELS

import logging
from enum import StrEnum

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d)"

class LogLevels(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"

def configure_logging(log_level: str = LogLevels.error):
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        logging.basicConfig(level=LOG_LEVELS["error"])
        return

    if log_level == LogLevels.debug:
        logging.basicConfig(level=LOG_LEVELS["debug"], format=LOG_FORMAT_DEBUG)
        return
    logging.basicConfig(level=log_level)