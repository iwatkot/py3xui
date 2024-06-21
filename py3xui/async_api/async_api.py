"""This module provides classes to interact with the XUI API in an asynchronous manner."""

from __future__ import annotations

from py3xui.async_api import AsyncClientApi, AsyncDatabaseApi, AsyncInboundApi
from py3xui.utils import Logger, env

logger = Logger(__name__)


class AsyncApi:
    """This class provides a high-level interface to interact with the XUI API.
    Access to the client, inbound, and database APIs is provided through this class.

    Arguments:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.

    Attributes and Properties:
        client (AsyncClientApi): The client API.
        inbound (AsyncInboundApi): The inbound API.
        database (AsyncDatabaseApi): The database API.

    Public Methods:
        login: Logs into the XUI API.
        from_env: Creates an instance of the API from environment variables.

    Examples:
        ```python
        import py3xui

        # It's recommended to use environment variables for the credentials.
        os.environ["XUI_HOST"] = "https://xui.example.com"
        os.environ["XUI_USERNAME"] = "username"
        os.environ["XUI_PASSWORD"] = "password"

        api = py3xui.AsyncApi.from_env()

        # Alternatively, you can provide the credentials directly.
        api = py3xui.AsyncApi("https://xui.example.com", "username", "password")

        api.login()

        # Some examples of using the API.
        inbounds: list[py3xui.Inbound] = await api.inbound.get_list()
        client: py3xui.Client = await api.client.get_by_email("email")
        ```
    """

    def __init__(self, host: str, username: str, password: str):
        self.client = AsyncClientApi(host, username, password)
        self.inbound = AsyncInboundApi(host, username, password)
        self.database = AsyncDatabaseApi(host, username, password)

    @classmethod
    def from_env(cls) -> AsyncApi:
        """Creates an instance of the API from environment variables.
        Following environment variables should be set:
        - XUI_HOST: The XUI host URL.
        - XUI_USERNAME: The XUI username.
        - XUI_PASSWORD: The XUI password.

        Returns:
            Api: The API instance.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            ```
        """
        host = env.xui_host()
        username = env.xui_username()
        password = env.xui_password()
        return cls(host, username, password)

    async def login(self) -> None:
        """Logs into the XUI API and sets the session cookie for the client, inbound, and
        database APIs.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            await api.login()
            ```
        """
        await self.client.login()
        self.inbound.session = self.client.session
        self.database.session = self.client.session
        logger.info("Logged in successfully.")
