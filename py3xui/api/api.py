"""This module provides classes to interact with the XUI API."""

from __future__ import annotations

from py3xui.api import ClientApi, DatabaseApi, InboundApi
from py3xui.utils import Logger, env

logger = Logger(__name__)


class Api:
    """This class provides a high-level interface to interact with the XUI API.
    Access to the client, inbound, and database APIs is provided through this class.

    Arguments:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        skip_login (bool): Skip the login process. Default is False.

    Attributes and Properties:
        client (ClientApi): The client API.
        inbound (InboundApi): The inbound API.
        database (DatabaseApi): The database API.

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

        api = py3xui.Api.from_env()

        # Alternatively, you can provide the credentials directly.
        api = py3xui.Api("https://xui.example.com", "username", "password")

        # Some examples of using the API.
        inbounds: list[py3xui.Inbound] = api.inbound.get_list()
        client: py3xui.Client = api.client.get_by_email("email")
        ```
    """

    def __init__(self, host: str, username: str, password: str, skip_login: bool = False):
        self.client = ClientApi(host, username, password)
        self.inbound = InboundApi(host, username, password)
        self.database = DatabaseApi(host, username, password)
        if not skip_login:
            self.login()

    @classmethod
    def from_env(cls, skip_login: bool = False) -> Api:
        """Creates an instance of the API from environment variables.
        Following environment variables should be set:
        - XUI_HOST: The XUI host URL.
        - XUI_USERNAME: The XUI username.
        - XUI_PASSWORD: The XUI password.

        Arguments:
            skip_login (bool): Skip the login process. Default is False.

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
        return cls(host, username, password, skip_login)

    def login(self) -> None:
        """Logs into the XUI API and sets the session cookie for the client, inbound, and
        database APIs.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env(skip_login=True)
            api.login()
            ```
        """
        self.client.login()
        self.inbound.session = self.client.session
        self.database.session = self.client.session
        logger.info("Logged in successfully.")
