"""This module provides classes to interact with the XUI API."""

# pylint: disable=R0801
from __future__ import annotations

from typing import Any

from py3xui.api import ClientApi, DatabaseApi, InboundApi
from py3xui.utils import Logger, env


class Api:
    """This class provides a high-level interface to interact with the XUI API.
    Access to the client, inbound, and database APIs is provided through this class.

    Arguments:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        token (str): The XUI secret token.
        tls_verify (bool | str): Whether to verify the server's TLS certificate. 
                                 Can be a boolean or a path to a certificate file.
        logger (Any | None): The logger, if not set, a dummy logger is used.

    Attributes and Properties:
        client (ClientApi): The client API.
        inbound (InboundApi): The inbound API.
        database (DatabaseApi): The database API.
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
        os.environ["XUI_TOKEN"] = "token"

        api = py3xui.Api.from_env()

        # Alternatively, you can provide the credentials directly.
        api = py3xui.Api("https://xui.example.com", "username", "password", "token")

        api.login()

        # Some examples of using the API.
        inbounds: list[py3xui.Inbound] = api.inbound.get_list()
        client: py3xui.Client = api.client.get_by_email("email")
        ```
    """

    def __init__(self, host: str, username: str, password: str, token: str = None, tls_verify: bool | str = True, logger: Any | None = None):
        self.logger = logger or Logger(__name__)
        self.client = ClientApi(host, username, password, token, tls_verify, logger)
        self.inbound = InboundApi(host, username, password, token, tls_verify, logger)
        self.database = DatabaseApi(host, username, password, token, tls_verify, logger)
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
    def from_env(cls, logger: Any | None = None) -> Api:
        """Creates an instance of the API from environment variables.
        Following environment variables should be set:
        - XUI_HOST: The XUI host URL.
        - XUI_USERNAME: The XUI username.
        - XUI_PASSWORD: The XUI password.
        - XUI_TOKEN: The XUI secret token.

        Arguments:
            logger (Any | None): The logger, if not set, a dummy logger is used.

        Returns:
            Api: The API instance.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            ```
        """
        host = env.xui_host()
        username = env.xui_username()
        password = env.xui_password()
        token = env.xui_token()
        return cls(host, username, password, token, logger)

    def login(self) -> None:
        """Logs into the XUI API and sets the session cookie for the client, inbound, and
        database APIs.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            ```
        """
        self.client.login()
        self._session = self.client.session
        self.inbound.session = self._session
        self.database.session = self._session
        self.logger.info("Logged in successfully.")
