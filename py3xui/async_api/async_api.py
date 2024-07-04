"""This module provides classes to interact with the XUI API in an asynchronous manner."""

# pylint: disable=R0801
from __future__ import annotations

from typing import Any

from py3xui.async_api import AsyncClientApi, AsyncDatabaseApi, AsyncInboundApi
from py3xui.utils import Logger, env


class AsyncApi:
    """This class provides a high-level interface to interact with the XUI API.
    Access to the client, inbound, and database APIs is provided through this class.

    Arguments:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        logger (Any | None): The logger, if not set, a dummy logger is used.

    Attributes and Properties:
        client (AsyncClientApi): The client API.
        inbound (AsyncInboundApi): The inbound API.
        database (AsyncDatabaseApi): The database API.
        session (str): The session cookie for the XUI API.

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

        await api.login()

        # Some examples of using the API.
        inbounds: list[py3xui.Inbound] = await api.inbound.get_list()
        client: py3xui.Client = await api.client.get_by_email("email")
        ```
    """

    def __init__(self, host: str, username: str, password: str, logger: Any | None = None):
        self.logger = logger or Logger(__name__)
        self.client = AsyncClientApi(host, username, password, logger)
        self.inbound = AsyncInboundApi(host, username, password, logger)
        self.database = AsyncDatabaseApi(host, username, password, logger)
        self._session: str | None = None

    @property
    def session(self) -> str | None:
        """The session cookie for the XUI API.

        Returns:
            str: The session cookie for the XUI API.
        """
        return self._session

    @session.setter
    def session(self, value: str) -> None:
        self._session = value
        self.client.session = value
        self.inbound.session = value
        self.database.session = value

    @classmethod
    def from_env(cls, logger: Any | None = None) -> AsyncApi:
        """Creates an instance of the API from environment variables.
        Following environment variables should be set:
        - XUI_HOST: The XUI host URL.
        - XUI_USERNAME: The XUI username.
        - XUI_PASSWORD: The XUI password.
        
        Arguments:
            logger (Any | None): The logger, if not set, a dummy logger is used.

        Returns:
            Api: The API instance.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()
            ```
        """
        host = env.xui_host()
        username = env.xui_username()
        password = env.xui_password()
        return cls(host, username, password, logger)

    async def login(self) -> None:
        """Logs into the XUI API and sets the session cookie for the client, inbound, and
        database APIs.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()
            ```
        """
        await self.client.login()
        self._session = self.client.session
        self.inbound.session = self._session
        self.database.session = self._session
        self.logger.info("Logged in successfully.")
