"""This module contains the base class for the XUI API."""

# pylint: disable=R0801

from time import sleep
from typing import Any, Callable

import requests

from py3xui.utils import COOKIE_NAMES, Logger


# pylint: disable=too-few-public-methods
class ApiFields:
    """Stores the fields returned by the XUI API for parsing."""

    SUCCESS = "success"
    MSG = "msg"
    OBJ = "obj"
    CLIENT_STATS = "clientStats"
    NO_IP_RECORD = "No IP Record"
    GET = "GET"
    POST = "POST"


# pylint: disable=R0902
class BaseApi:
    """Base class for the XUI API. Contains common methods for making requests.

    Arguments:
        host (str): The host of the XUI API.
        username (str): The username for the XUI API.
        password (str): The password for the XUI API.
        token (str | None): The secret token for the XUI API.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        logger (Any | None): The logger, if not set, a dummy logger is used.

    Attributes and Properties:
        host (str): The host of the XUI API.
        username (str): The username for the XUI API.
        password (str): The password for the XUI API.
        token (str | None): The secret token for the XUI API.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        max_retries (int): The maximum number of retries for a request.
        session (str): The session cookie for the XUI API.

    Public Methods:
        login: Logs into the XUI API.

    Private Methods:
        _check_response: Checks the response from the XUI API.
        _url: Returns the URL for the XUI API.
        _request_with_retry: Makes a request to the XUI API with retries.
        _post: Makes a POST request to the XUI API.
        _get: Makes a GET request to the XUI API.

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
    ):  # pylint: disable=R0913, R0917
        self._host = host.rstrip("/")
        self._username = username
        self._password = password
        self._token = token
        self._use_tls_verify = use_tls_verify
        self._custom_certificate_path = custom_certificate_path
        self._max_retries: int = 3
        self._session: str | None = None
        self.logger = logger or Logger(__name__)

    @property
    def host(self) -> str:
        """The host of the XUI API.

        Returns:
            str: The host of the XUI API."""
        return self._host

    @property
    def username(self) -> str:
        """The username for the XUI API.

        Returns:
            str: The username for the XUI API."""
        return self._username

    @property
    def password(self) -> str:
        """The password for the XUI API.

        Returns:
            str: The password for the XUI API."""
        return self._password

    @property
    def token(self) -> str | None:
        """The secret token for the XUI API.

        Returns:
            str | None: The secret token for the XUI API."""
        return self._token

    @property
    def use_tls_verify(self) -> bool:
        """Whether to verify the server TLS certificate.

        Returns:
            bool: Whether to verify the TLS certificate for a request."""
        return self._use_tls_verify

    @property
    def custom_certificate_path(self) -> str | None:
        """The path to a custom certificate file.

        Returns:
            str | None: The path to a custom certificate file."""
        return self._custom_certificate_path

    @property
    def max_retries(self) -> int:
        """The maximum number of retries for a request.

        Returns:
            int: The maximum number of retries for a request."""
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int) -> None:
        """Sets the maximum number of retries for a request.

        Arguments:
            value (int): The maximum number of retries for a request."""
        self._max_retries = value

    @property
    def session(self) -> str | None:
        """The session cookie for the XUI API.

        Returns:
            str | None: The session cookie for the XUI API."""
        return self._session

    @session.setter
    def session(self, value: str | None) -> None:
        """Sets the session cookie for the XUI API.

        Arguments:
            value (str | None): The session cookie for the XUI API."""
        self._session = value

    def login(self) -> None:
        """Logs into the XUI API and sets the session cookie if successful.

        Raises:
            ValueError: If the login is unsuccessful."""
        endpoint = "login"
        headers: dict[str, str] = {}

        url = self._url(endpoint)
        data = {"username": self.username, "password": self.password}
        if self.token is not None:
            data.update({"loginSecret": self.token})
        self.logger.info("Logging in with username: %s", self.username)

        response = self._post(url, headers, data, is_login=True)
        cookie = self._get_cookie(response)
        if not cookie:
            raise ValueError("No session cookie found, something wrong with the login...")
        self.logger.info("Session cookie successfully retrieved for username: %s", self.username)
        self.session = cookie

    def _get_cookie(self, response: requests.Response) -> str | None:
        """Returns the session cookie from the response.

        Arguments:
            response (requests.Response): The response from the XUI API.

        Returns:
            str: The session cookie from the response or None if not found."""
        for cookie_name in COOKIE_NAMES:
            cookie = response.cookies.get(cookie_name)
            if cookie:
                return cookie
        return None

    def _check_response(self, response: requests.Response) -> None:
        """Checks the response from the XUI API using the success field.

        Arguments:
            response (requests.Response): The response from the XUI API.

        Raises:
            ValueError: If the response status is not successful.
        """
        response_json = response.json()

        status = response_json.get(ApiFields.SUCCESS)
        message = response_json.get(ApiFields.MSG)
        if not status:
            raise ValueError(f"Response status is not successful, message: {message}")

    def _url(self, endpoint: str) -> str:
        """Returns the URL for the XUI API (adds the endpoint to the host URL).

        Arguments:
            endpoint (str): The endpoint for the XUI API.

        Returns:
            str: The URL for the XUI API."""
        return f"{self._host}/{endpoint}"

    def _request_with_retry(
        self,
        method: Callable[..., requests.Response],
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> requests.Response:
        """Makes a request to the XUI API with retries.

        Arguments:
            method (Callable[..., requests.Response]): The request method to use.
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Returns:
            requests.Response: The response from the XUI API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
            requests.exceptions.RetryError: If the maximum number of retries is exceeded."""
        self.logger.debug("%s request to %s...", method.__name__.upper(), url)
        for retry in range(1, self.max_retries + 1):
            try:
                skip_check = kwargs.pop("skip_check", False)

                # 'verify' is a variable controlling the server TLS certificate verification.
                # When set to True, it commands the requests library to verify the server's
                # certificate against a list of trusted CAs (Certificate Authorities). If it
                # points to a string path, that path is used to load a custom CA certificate
                # file for verification, which is beneficial for environments using custom
                # certificates. Setting 'verify' to False disables TLS certificate verification,
                # a practice that should be used with caution as it exposes the connection to
                # security risks like man-in-the-middle attacks. This setting ensures the client
                # can establish a secure and trusted connection with the server.
                verify: bool | str
                if not self._use_tls_verify:
                    # If TLS verification is disabled, 'verify' is set to False
                    verify = False
                elif self._custom_certificate_path:
                    # If a path to a custom certificate is provided, it will be used
                    # to verify the TLS connection instead of the default CA bundle.
                    verify = self._custom_certificate_path
                else:
                    # Otherwise, the default CA bundle will be used for verification.
                    verify = True

                kwargs.update({"verify": verify})
                response = method(url, cookies={"3x-ui": self.session}, headers=headers, **kwargs)
                response.raise_for_status()
                if skip_check:
                    return response
                self._check_response(response)
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if retry == self.max_retries:
                    raise e
                self.logger.warning(
                    "Request to %s failed: %s, retry %s of %s", url, e, retry, self.max_retries
                )
                sleep(1 * (retry + 1))
            except requests.exceptions.RequestException as e:
                raise e
        raise requests.exceptions.RetryError(
            f"Max retries exceeded with no successful response to {url}"
        )

    def _post(
        self, url: str, headers: dict[str, str], data: dict[str, Any], **kwargs
    ) -> requests.Response:
        """Makes a POST request to the XUI API.

        Arguments:
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            data (dict[str, Any]): The data for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Raises:
            ValueError: If the session cookie is not set and it's not a login request.

        Returns:
            requests.Response: The response from the XUI API."""
        if not kwargs.pop("is_login", False) and not self.session:
            raise ValueError("Before making a POST request, you must use the login() method.")
        return self._request_with_retry(requests.post, url, headers, json=data, **kwargs)

    def _get(self, url: str, headers: dict[str, str], **kwargs) -> requests.Response:
        """Makes a GET request to the XUI API.

        Arguments:
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Raises:
            ValueError: If the session cookie is not set and it's not a login request.

        Returns:
            requests.Response: The response from the XUI API."""
        if not kwargs.pop("is_login", False) and not self.session:
            raise ValueError("Before making a GET request, you must use the login() method.")
        return self._request_with_retry(requests.get, url, headers, **kwargs)
