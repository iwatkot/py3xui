"""This module provides classes to interact with the XUI API."""

from time import sleep
from typing import Any, Callable

import requests

from py3xui.utils import Logger, env

logger = Logger(__name__)

# region debug
from dotenv import load_dotenv

load_dotenv("local.env")
# endregion


# pylint: disable=too-few-public-methods
class ApiFields:
    """Stores the fields returned by the XUI API for parsing."""

    SUCCESS = "success"
    MSG = "msg"


class Api:
    def __init__(self, host: str, username: str, password: str, skip_login: bool = False):
        self._host = host.rstrip("/")
        self._username = username
        self._password = password
        self._max_retries: int = 3

        if not skip_login:
            self.login()

        self._session: str | None = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int) -> None:
        self._max_retries = value

    @property
    def session(self) -> str | None:
        return self._session

    @session.setter
    def session(self, value: str | None) -> None:
        self._session = value

    @classmethod
    def from_env(cls, skip_login: bool = False):
        host = env.xui_host()
        username = env.xui_username()
        password = env.xui_password()
        return cls(host, username, password, skip_login)

    def login(self) -> None:
        endpoint = "login"
        url = self._url(endpoint)
        data = {"username": self.username, "password": self.password}
        logger.info("Logging in with username: %s", self.username)
        response = self._post(url, data)
        cookie = response.cookies.get("session")
        if not cookie:
            raise ValueError("No session cookie found, something wrong with the login...")
        logger.info("Session cookie successfully retrieved for username: %s", self.username)
        self.session = cookie

    def _check_response(self, response: requests.Response) -> None:
        response_json = response.json()

        status = response_json.get(ApiFields.SUCCESS)
        message = response_json.get(ApiFields.MSG)
        if not status:
            raise ValueError(f"Response status is not successful, message: {message}")

    def _url(self, endpoint: str) -> str:
        return f"{self._host}/{endpoint}"

    def _request_with_retry(
        self, method: Callable[..., requests.Response], url: str, **kwargs: Any
    ) -> requests.Response:
        logger.debug("%s request to %s...", method.__name__.upper(), url)
        for retry in range(1, self.max_retries + 1):
            try:
                response = method(url, **kwargs)
                response.raise_for_status()
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

    def _post(self, url: str, data: dict[str, Any]) -> requests.Response:
        return self._request_with_retry(requests.post, url, json=data)

    def _get(self, url: str) -> requests.Response:
        return self._request_with_retry(requests.get, url)


api = Api.from_env()
print(api.host)
