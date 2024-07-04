"""This module contains dummy logging class if the logger was not set in API."""

# pylint: disable=C0115, C0116


class Logger:
    def __init__(self, name: str):
        pass

    def debug(self, *args, **kwargs) -> None:
        pass

    def info(self, *args, **kwargs) -> None:
        pass

    def warning(self, *args, **kwargs) -> None:
        pass

    def error(self, *args, **kwargs) -> None:
        pass
