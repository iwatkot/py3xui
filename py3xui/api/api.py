"""This module provides classes to interact with the XUI API."""

# pylint: disable=R0801
from __future__ import annotations

import logging
from typing import Any

from py3xui.api import ClientApi, DatabaseApi, InboundApi, ServerApi
from py3xui.utils import env


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
        username (str | None): The XUI username. Required when token is not provided.
        password (str | None): The XUI password. Required when token is not provided.
        token (str | None): The bearer token for API authentication. When provided,
            login() is not required.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        logger (Any | None): The logger, if not set, default logger is used.

    Attributes and Properties:
        client (ClientApi): The client API.
        inbound (InboundApi): The inbound API.
        database (DatabaseApi): The database API.
        session (str): The session cookie for the XUI API.
        csrf_token (str | None): The CSRF token propagated to the sub-APIs.
        cookie_name (str): The cookie name for the XUI API.

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

        api.login()

        # Some examples of using the API.
        inbounds: list[py3xui.Inbound] = api.inbound.get_list()
        client: py3xui.Client = api.client.get_by_email("email")
        ```
    """

    def __init__(
        self,
        host: str,
        username: str | None = None,
        password: str | None = None,
        use_tls_verify: bool = True,
        custom_certificate_path: str | None = None,
        logger: Any | None = None,
        *,
        token: str | None = None,  # The token is keyword for old version compbality
    ):  # pylint: disable=R0913, R0917
        self.logger = logger or logging.getLogger(__name__)

        self.client = ClientApi(
            host,
            username,
            password,
            token,
            use_tls_verify,
            custom_certificate_path,
            logger,
        )
        self.inbound = InboundApi(
            host,
            username,
            password,
            token,
            use_tls_verify,
            custom_certificate_path,
            logger,
        )
        self.database = DatabaseApi(
            host,
            username,
            password,
            token,
            use_tls_verify,
            custom_certificate_path,
            logger,
        )
        self.server = ServerApi(
            host,
            username,
            password,
            token,
            use_tls_verify,
            custom_certificate_path,
            logger,
        )

        self._csrf_token: str | None = None
        self._session: str | None = None
        self._cookie_name: str | None = None

    @property
    def csrf_token(self) -> str | None:
        """The CSRF token shared by the underlying API clients.

        Returns:
            str | None: The CSRF token for session-authenticated requests."""
        return self._csrf_token

    @csrf_token.setter
    def csrf_token(self, value: str | None) -> None:
        """Sets the CSRF token for all underlying API clients.

        Arguments:
            value (str | None): The CSRF token to propagate."""
        self._csrf_token = value
        self.client.csrf_token = value
        self.inbound.csrf_token = value
        self.database.csrf_token = value
        self.server.csrf_token = value

    @property
    def session(self) -> str | None:
        """The session cookie for the XUI API.

        Returns:
            str: The session cookie for the XUI API.
        """
        return self._session

    @session.setter
    def session(self, value: str) -> None:
        """Sets the session cookie for the XUI API.

        Arguments:
            value (str): The session cookie to set.
        """
        self._session = value
        self.client.session = value
        self.inbound.session = value
        self.database.session = value
        self.server.session = value

    @property
    def cookie_name(self) -> str | None:
        """The cookie name for the XUI API.

        Returns:
            str | None: The cookie name for the XUI API. If not set, it will be None.
        """
        return self._cookie_name

    @cookie_name.setter
    def cookie_name(self, value: str | None) -> None:
        """Sets the cookie name for the XUI API.

        This method is used to set the cookie name for all the APIs.

        Arguments:
            value (str): The cookie name to set.
        """
        self._cookie_name = value
        self.client.cookie_name = value
        self.inbound.cookie_name = value
        self.database.cookie_name = value
        self.server.cookie_name = value

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
        - XUI_USERNAME: The XUI username. Required when XUI_TOKEN is not set.
        - XUI_PASSWORD: The XUI password. Required when XUI_TOKEN is not set.
        - XUI_TOKEN: The bearer token for API authentication (Optional).
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

            api = py3xui.Api.from_env()
            api.login()
            ```
        """
        host = env.xui_host()
        token = env.xui_token()
        is_token_missing: bool = token is None

        username = env.xui_username(raise_if_not_found=is_token_missing)
        password = env.xui_password(raise_if_not_found=is_token_missing)

        if use_tls_verify is None:
            use_tls_verify = env.tls_verify()
            if use_tls_verify is None:
                use_tls_verify = True

        if custom_certificate_path is None:
            custom_certificate_path = env.tls_cert_path()

        return cls(
            host,
            username,
            password,
            token,
            use_tls_verify,
            custom_certificate_path,
            logger,
        )

    def login(self, two_factor_code: str | int | None = None) -> None:
        """Logs into the XUI API and sets the session cookie for the client, inbound, and
        database APIs. Login fetches a CSRF token first and propagates it to all
        sub-APIs. If the API was created with a bearer token, use requests directly
        without calling login().

        Arguments:
            two_factor_code (str | int | None): The two-factor authentication code, if required.


        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login() # If two-factor authentication is not enabled.
            api.login("123456")  # If two-factor authentication is enabled, pass the code.
            ```
        """
        self.client.login(two_factor_code)
        self.session = self.client.session  # type: ignore
        self.cookie_name = self.client.cookie_name
        self.csrf_token = self.client.csrf_token
        self.logger.info("Logged in successfully.")
