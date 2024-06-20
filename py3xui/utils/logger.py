"""Logging module for the application."""

import logging
import os
import sys

# region constants
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMATTER = "%(name)s | %(asctime)s | %(levelname)s | %(message)s"
# endregion


class Logger(logging.Logger):
    """Handles logging to the file and stdout with timestamps.

    Arguments:
        name (str): Logger name.
        level (str): Log level.
        log_dir (str): Log directory.
    """

    def __init__(
        self,
        name: str,
    ):
        super().__init__(name)
        self.setLevel(LOG_LEVEL)
        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.fmt = LOG_FORMATTER
        self.stdout_handler.setFormatter(logging.Formatter(LOG_FORMATTER))
        self.addHandler(self.stdout_handler)
