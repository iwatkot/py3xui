"""This module contains the base class for the XUI API."""

from time import sleep
from typing import Any, Callable

import requests

from py3xui.utils import Logger

logger = Logger(__name__)


# pylint: disable=too-few-public-methods
class ApiFields:
    """Stores the fields returned by the XUI API for parsing."""

    SUCCESS = "success"
    MSG = "msg"
    OBJ = "obj"
    CLIENT_STATS = "clientStats"
    NO_IP_RECORD = "No IP Record"


class BaseApi:
    """Base class for the XUI API. Contains common methods for making requests.

    Arguments:
        host (str): The host of the XUI API.
        username (str): The username for the XUI API.
        password (str): The password for the XUI API.

    Attributes and Properties:
        host (str): The host of the XUI API.
        username (str): The username for the XUI API.
        password (str): The password for the XUI API.
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

    def __init__(self, host: str, username: str, password: str):
        self._host = host.rstrip("/")
        self._username = username
        self._password = password
        self._max_retries: int = 3
        self._session: str | None = None

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
        logger.info("Logging in with username: %s", self.username)

        response = self._post(url, headers, data)
        cookie: str | None = response.cookies.get("session")
        if not cookie:
            raise ValueError("No session cookie found, something wrong with the login...")
        logger.info("Session cookie successfully retrieved for username: %s", self.username)
        self.session = cookie

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
        logger.debug("%s request to %s...", method.__name__.upper(), url)
        for retry in range(1, self.max_retries + 1):
            try:
                skip_check = kwargs.pop("skip_check", False)
                response = method(url, cookies={"session": self.session}, headers=headers, **kwargs)
                response.raise_for_status()
                if skip_check:
                    return response
                self._check_response(response)
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if retry == self.max_retries:
                    raise e
                logger.warning(
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

        Returns:
            requests.Response: The response from the XUI API."""
        return self._request_with_retry(requests.post, url, headers, json=data, **kwargs)

    def _get(self, url: str, headers: dict[str, str], **kwargs) -> requests.Response:
        """Makes a GET request to the XUI API.

        Arguments:
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Returns:
            requests.Response: The response from the XUI API."""
        return self._request_with_retry(requests.get, url, headers, **kwargs)
