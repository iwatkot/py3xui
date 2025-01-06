"""This module contains the ServerApi class for handling server in the XUI API."""

from py3xui.async_api.async_api_base import AsyncBaseApi


class AsyncServerApi(AsyncBaseApi):
    """This class provides methods to interact with the server in the XUI API in an asynchronous
    manner.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        token (str | None): The XUI secret token.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_db: Retrieves a database backup file and saves it to a specified path.

    Examples:
        ```python
        import py3xui

        api = py3xui.AsyncApi.from_env()
        await api.login()

        db_save_path = "db_backup.db"
        await api.server.get_db(db_save_path)
        ```
    """

    async def get_db(self, save_path: str) -> None:
        """This route is used to retrieve a database backup file and save it to a specified path.

        Arguments:
            save_path (str): The path to save the database backup file.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            db_save_path = "db_backup.db"
            await api.server.get_db(db_save_path)
            ```
        """
        endpoint = "server/getDb"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting DB backup...")

        response = await self._get(url, headers, skip_check=True)

        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            self.logger.info(f"DB backup saved to {save_path}")
        else:
            self.logger.error(f"Failed to get DB backup: {response.text}")
            response.raise_for_status()
