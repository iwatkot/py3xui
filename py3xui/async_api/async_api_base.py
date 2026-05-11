"""This module contains the async base class for the XUI API."""

# pylint: disable=R0801

import asyncio
import logging
from typing import Any

import httpx

from py3xui.api.api_base import ApiFields
from py3xui.utils import COOKIE_NAMES


# pylint: disable=R0902
class AsyncBaseApi:
    """Base class for the XUI API. Contains async common methods for making requests.

    Arguments:
        host (str): The host of the XUI API.
        username (str): The username for the XUI API.
        password (str): The password for the XUI API.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        logger (Any | None): The logger, if not set, default logger is used.

    Attributes and Properties:
        host (str): The host of the XUI API.
        username (str): The username for the XUI API.
        password (str): The password for the XUI API.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        max_retries (int): The maximum number of retries for a request.
        session (str): The session cookie for the XUI API.
        cookie_name (str): The name of the cookie for the XUI API.

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
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        use_tls_verify: bool = True,
        custom_certificate_path: str | None = None,
        logger: Any | None = None,
    ):  # pylint: disable=R0913, R0917
        self._host: str = host.rstrip("/")
        self._username: str | None = username
        self._password: str | None = password
        self._token: str | None = token
        self._use_tls_verify = use_tls_verify
        self._custom_certificate_path = custom_certificate_path
        self._csrf_token: str | None = None
        self._max_retries: int = 3
        self._session: str | None = None
        self._cookie_name: str | None = None
        self.logger = logger or logging.getLogger(__name__)

        self._check_token_or_password()

    @property
    def host(self) -> str:
        """The host of the XUI API.

        Returns:
            str: The host of the XUI API."""
        return self._host

    @property
    def username(self) -> str | None:
        """The username for the XUI API.

        Returns:
            str: The username for the XUI API."""
        return self._username

    @property
    def password(self) -> str | None:
        """The password for the XUI API.

        Returns:
            str: The password for the XUI API."""
        return self._password

    @property
    def csrf_token(self) -> str | None:
        """The CSRF token for session-authenticated requests.

        Returns:
            str | None: The CSRF token for the XUI API."""
        return self._csrf_token

    @csrf_token.setter
    def csrf_token(self, value: str | None) -> None:
        """Sets the CSRF token for session-authenticated requests.

        Arguments:
            value (str | None): The CSRF token for the XUI API."""
        self._csrf_token = value

    @property
    def token(self) -> str | None:
        """The token for the XUI API.

        Returns:
            str: The token for the XUI API."""
        return self._token

    @token.setter
    def token(self, value: str | None) -> None:
        self._token = value

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

    @property
    def cookie_name(self) -> str | None:
        """The name of the cookie for the XUI API.

        Returns:
            str | None: The name of the cookie for the XUI API."""
        return self._cookie_name

    @cookie_name.setter
    def cookie_name(self, value: str | None) -> None:
        """Sets the name of the cookie for the XUI API.

        Arguments:
            value (str | None): The name of the cookie for the XUI API."""
        self._cookie_name = value

    def _url(self, endpoint: str) -> str:
        """Returns the URL for the XUI API (adds the endpoint to the host URL).

        Arguments:
            endpoint (str): The endpoint for the XUI API.

        Returns:
            str: The URL for the XUI API."""
        return f"{self._host}/{endpoint}"

    def _generate_headers(self, headers: dict[str, str]) -> dict[str, str]:
        if self._token is not None:
            headers.update(
                {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}
            )
        elif self._csrf_token is not None:
            headers.update({"X-CSRF-Token": self._csrf_token})

        return headers

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> httpx.Response:
        """Makes a request to the XUI API with retries.

        Arguments:
            method (str): The method for the request.
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Returns:
            httpx.Response: The response from the XUI API.

        Raises:
            ValueError: If the invalid method is provided.
            httpx.RequestError: If the request fails.
            httpx.HTTPStatusError: If the maximum number of retries is exceeded."""
        self.logger.debug("%s request to %s...", method, url)

        if not kwargs.pop("is_csrf_request", False):
            headers: dict[str, str] = self._generate_headers(headers)

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

                async with httpx.AsyncClient(
                    cookies=self.cookies, verify=verify, follow_redirects=True
                ) as client:
                    if method == ApiFields.GET:
                        response = await client.get(url, headers=headers, **kwargs)
                    elif method == ApiFields.POST:
                        response = await client.post(url, headers=headers, **kwargs)
                    else:
                        raise ValueError(f"Invalid method: {method}")
                response.raise_for_status()
                if skip_check:
                    return response
                await self._check_response(response)
                return response
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if retry == self.max_retries:
                    raise e
                self.logger.warning(
                    "Request to %s failed: %s, retry %s of %s",
                    url,
                    e,
                    retry,
                    self.max_retries,
                )
                await asyncio.sleep(1 * (retry + 1))
            except httpx.HTTPStatusError as e:
                raise e
        raise ConnectionError(
            f"Max retries exceeded with no successful response to {url}"
        )

    def _check_token_or_password(self) -> None:
        if self.token:
            return
        if self.username and self.password:
            return
        raise ValueError("There must be either token or username and password.")

    async def _get_csrf_token(self) -> str:
        endpoint: str = "csrf-token"
        headers: dict[str, str] = {}

        url = self._url(endpoint)
        response = await self._get(
            url,
            headers,
            is_login=True,
            is_csrf_request=True,
            skip_check=True,
        )
        self.session = await self._get_cookie(response)

        response_json = response.json()
        csrf_token = response_json.get(ApiFields.OBJ)
        if not isinstance(csrf_token, str) or not csrf_token:
            raise ValueError("No CSRF token found, something wrong with the login...")
        self.csrf_token = csrf_token

        return csrf_token

    async def login(self, two_factor_code: str | int | None = None) -> None:
        """Logs into the XUI API and sets the session cookie if successful.

        The login flow reads a CSRF token from the panel login page, then sends that
        token with the username/password login request.

        Arguments:
            two_factor_code (str | int | None): The two-factor authentication code, if required.

        Raises:
            ValueError: If the login is unsuccessful."""

        if self._token is not None:
            raise RuntimeError("No need to login if using the token already.")

        if None in (self._username, self._password):
            raise ValueError("No username or password entered.")

        # Clear the session before new login
        self.session = None
        self.cookie_name = None
        self.csrf_token = None

        headers: dict[str, str] = {"X-CSRF-Token": await self._get_csrf_token()}

        endpoint = "login"
        url = self._url(endpoint)

        data: dict[str, str] = {  # pyright: ignore[reportAssignmentType]
            "username": self.username,
            "password": self.password,
        }

        if two_factor_code is not None:
            data["twoFactorCode"] = str(two_factor_code)

        self.logger.info("Logging in with username: %s", self.username)

        response = await self._post(url, headers, data, is_login=True)
        cookie = await self._get_cookie(response)
        if not cookie:
            raise ValueError(
                "No session cookie found, something wrong with the login..."
            )
        self.logger.info(
            "Session cookie successfully retrieved for username: %s", self.username
        )
        self.session = cookie

    async def _get_cookie(self, response: httpx.Response) -> str | None:
        """Returns the session cookie from the response.

        Arguments:
            response (httpx.Response): The response from the XUI API.

        Returns:
            str: The session cookie from the response or None if not found."""
        for cookie_name in COOKIE_NAMES:
            cookie = response.cookies.get(cookie_name)
            if cookie:
                self.logger.debug("Session cookie found: %s", cookie_name)
                self.cookie_name = cookie_name
                return cookie
        return None

    @property
    def cookies(self) -> dict[str, str]:
        """Returns the cookies for the XUI API. If session is not set yet, returns an empty dict.

        Returns:
            dict[str, str]: The cookies for the XUI API."""
        if not self.session or not self.cookie_name:
            return {}

        return {self.cookie_name: self.session}

    async def _check_response(self, response: httpx.Response) -> None:
        """Checks the response from the XUI API using the success field.

        Arguments:
            response (httpx.Response): The response from the XUI API.

        Raises:
            ValueError: If the response status is not successful.
        """
        response_json = response.json()

        status = response_json.get(ApiFields.SUCCESS)
        message = response_json.get(ApiFields.MSG)
        if not status:
            raise ValueError(f"Response status is not successful, message: {message}")

    async def _post(
        self, url: str, headers: dict[str, str], data: dict[str, Any], **kwargs
    ) -> httpx.Response:
        """Makes a POST request to the XUI API.

        Arguments:
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            data (dict[str, Any]): The data for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Raises:
            ValueError: If the session cookie is not set and it's not a login request.

        Returns:
            httpx.Response: The response from the XUI API."""
        if (
            not kwargs.pop("is_login", False)
            and not self.session
            and self.token is None
        ):
            raise ValueError(
                "Before making a POST request, you must use the login() method."
            )
        return await self._request_with_retry(
            ApiFields.POST, url, headers, json=data, **kwargs
        )

    async def _get(self, url: str, headers: dict[str, str], **kwargs) -> httpx.Response:
        """Makes a GET request to the XUI API.

        Arguments:
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            **kwargs (Any): Additional keyword arguments for the request.
        Raises:
            ValueError: If the session cookie is not set and it's not a login request.

        Returns:
            httpx.Response: The response from the XUI API."""
        if (
            not kwargs.pop("is_login", False)
            and not self.session
            and self.token is None
        ):
            raise ValueError(
                "Before making a POST request, you must use the login() method."
            )
        return await self._request_with_retry(ApiFields.GET, url, headers, **kwargs)
