"""This module contains the DatabaseApi class, which is responsible handling database operations
in the XUI API."""

from py3xui.api.api_base import BaseApi


class DatabaseApi(BaseApi):
    """This class provides methods to interact with the database in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        token (str): The XUI secret token.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        export: Exports the database.

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()
        api.login()
        api.database.export()
        ```
    """

    def export(self) -> None:
        """This endpoint triggers the creation of a system backup and initiates the delivery of
        the backup file to designated administrators via a configured Telegram bot. The server
        verifies the Telegram bot's activation status within the system settings and checks for
        the presence of admin IDs specified in the settings before sending the backup.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#5368cbc0-7c84-4b8c-aa54-d9fffb24d1f2)

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.database.export()
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/createbackup"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Exporting database...")

        self._get(url, headers, skip_check=True)
        self.logger.info("Database exported successfully.")
