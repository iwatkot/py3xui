"""This module provides classes to interact with the XUI API."""

# pylint: disable=R0801
from __future__ import annotations

from typing import Any

from py3xui.api import ClientApi, DatabaseApi, InboundApi
from py3xui.utils import Logger, env


class Api:
    """This class provides a high-level interface to interact with the XUI API.
    Access to the client, inbound, and database APIs is provided through this class.

    The `custom_certificate_path` allows specifying a custom certificate file for TLS verification.
    When this path is provided and `use_tls_verify` is set to `True` (default), the API uses this
    certificate for TLS verification instead of the system's default CA bundle.
    If `use_tls_verify` is set to `False`, TLS verification is disabled,
    which can be useful for development environments.

    **Security Warning**: Never disable TLS verification (use_tls_verify = False) in production.
    It significantly increases the risk of security threats like man-in-the-middle attacks.

    Arguments:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        token (str | None): The XUI secret token.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
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

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        token: str | None = None,
        use_tls_verify: bool = True,
        custom_certificate_path: str | None = None,
        logger: Any | None = None,
    ):  # pylint: disable=R0913
        self.logger = logger or Logger(__name__)
        self.client = ClientApi(
            host, username, password, token, use_tls_verify, custom_certificate_path, logger
        )
        self.inbound = InboundApi(
            host, username, password, token, use_tls_verify, custom_certificate_path, logger
        )
        self.database = DatabaseApi(
            host, username, password, token, use_tls_verify, custom_certificate_path, logger
        )
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
    def from_env(
        cls,
        use_tls_verify: bool | None = None,
        custom_certificate_path: str | None = None,
        logger: Any | None = None,
    ) -> Api:
        """Creates an instance of the API from environment variables. Optional parameters
        for SSL/TLS verification can be passed directly or read from environment variables.

        Following environment variables should be set:
        - XUI_HOST: The XUI host URL.
        - XUI_USERNAME: The XUI username.
        - XUI_PASSWORD: The XUI password.
        - XUI_TOKEN: The XUI secret token (Optional).
        - TLS_VERIFY: Whether to verify the server TLS certificate (Optional).
        - TLS_CERT_PATH: Path to a custom certificate file (Optional).


        Arguments:
            use_tls_verify (bool | None): Whether to verify the server TLS certificate.
                If not provided, it will try to read from environment variable.
            custom_certificate_path (str | None): The path to a custom certificate file.
                If not provided, it will try to read from environment variable.
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
        token = env.xui_token()

        if use_tls_verify is None:
            use_tls_verify = env.tls_verify()
            if use_tls_verify is None:
                use_tls_verify = True

        if custom_certificate_path is None:
            custom_certificate_path = env.tls_cert_path()

        return cls(host, username, password, token, use_tls_verify, custom_certificate_path, logger)

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
