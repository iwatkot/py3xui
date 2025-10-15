"""This module contains the ServerApi class for handling server in the XUI API."""

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.server.server import Server


class ServerApi(BaseApi):
    """This class provides methods to interact with the server in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_db: Retrieves a database backup file and saves it to a specified path.
        get_status: Retrieves the current status of the server.

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()
        api.login()

        db_save_path = "db_backup.db"
        api.server.get_db(db_save_path)
        ```
    """

    def get_db(self, save_path: str) -> None:
        """This route is used to retrieve a database backup file and save it to a specified path.

        Arguments:
            save_path (str): The path to save the database backup file.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            db_save_path = "db_backup.db"
            api.server.get_db(db_save_path)
            ```
        """
        endpoint = "server/getDb"
        headers = {"Accept": "application/octet-stream"}
        url = self._url(endpoint)
        self.logger.info("Getting DB backup...")

        response = self._get(url, headers, skip_check=True)

        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            self.logger.info("DB backup saved to %s", save_path)
        else:
            self.logger.error("Failed to get DB backup: %s", response.text)
            response.raise_for_status()

    def get_status(self) -> Server:
        """Gets the current server status.

        Returns:
            Server: Object containing server status information

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            status = api.server.get_status()
            print(f"CPU Load: {status.cpu}%")
            print(f"Memory Used: {status.mem.current}/{status.mem.total} bytes")
            ```
        """
        endpoint = "panel/api/server/status"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting server status...")

        response = self._get(url, headers)
        server_json = response.json().get(ApiFields.OBJ)

        self.logger.debug("Server status: %s", server_json)
        server = Server.model_validate(server_json)
        return server
