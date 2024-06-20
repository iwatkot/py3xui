import asyncio
from typing import Any

import httpx

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.utils import Logger

logger = Logger(__name__)


class AsyncBaseApi(BaseApi):
    """Base class for the XUI API. Contains async common methods for making requests.

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

    async def _request_with_retry(  # type: ignore
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
            httpx.RequestError: If the request fails.
            httpx.HTTPStatusError: If the maximum number of retries is exceeded."""
        logger.debug("%s request to %s...", method, url)
        for retry in range(1, self.max_retries + 1):
            try:
                skip_check = kwargs.pop("skip_check", False)
                async with httpx.AsyncClient(
                    cookies={"session": self.session}  # type: ignore
                ) as client:
                    if method == ApiFields.GET:
                        response = await client.get(url, headers=headers, **kwargs)
                    elif method == ApiFields.POST:
                        response = await client.post(url, headers=headers, **kwargs)
                response.raise_for_status()
                if skip_check:
                    return response
                await self._check_response(response)
                return response
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if retry == self.max_retries:
                    raise e
                logger.warning(
                    "Request to %s failed: %s, retry %s of %s", url, e, retry, self.max_retries
                )
                await asyncio.sleep(1 * (retry + 1))
            except httpx.HTTPStatusError as e:
                raise e
        raise ConnectionError(f"Max retries exceeded with no successful response to {url}")

    async def login(self) -> None:  # type: ignore
        """Logs into the XUI API and sets the session cookie if successful.

        Raises:
            ValueError: If the login is unsuccessful."""
        endpoint = "login"
        headers: dict[str, str] = {}

        url = self._url(endpoint)
        data = {"username": self.username, "password": self.password}
        logger.info("Logging in with username: %s", self.username)

        response = await self._post(url, headers, data)
        cookie: str | None = response.cookies.get("session")
        if not cookie:
            raise ValueError("No session cookie found, something wrong with the login...")
        logger.info("Session cookie successfully retrieved for username: %s", self.username)
        self.session = cookie

    async def _check_response(self, response: httpx.Response) -> None:  # type: ignore
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

    async def _post(  # type: ignore
        self, url: str, headers: dict[str, str], data: dict[str, Any], **kwargs
    ) -> httpx.Response:
        """Makes a POST request to the XUI API.

        Arguments:
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            data (dict[str, Any]): The data for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Returns:
            httpx.Response: The response from the XUI API."""
        return await self._request_with_retry(ApiFields.POST, url, headers, json=data, **kwargs)

    async def _get(  # type: ignore
        self, url: str, headers: dict[str, str], **kwargs
    ) -> httpx.Response:
        """Makes a GET request to the XUI API.

        Arguments:
            url (str): The URL for the XUI API.
            headers (dict[str, str]): The headers for the request.
            **kwargs (Any): Additional keyword arguments for the request.

        Returns:
            httpx.Response: The response from the XUI API."""
        return await self._request_with_retry(ApiFields.GET, url, headers, **kwargs)
