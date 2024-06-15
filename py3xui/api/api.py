from time import sleep
from typing import Any

import requests
from requests.exceptions import ConnectionError, Timeout

from py3xui.utils import Logger

logger = Logger(__name__)


class ApiFields:
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

    @property
    def session(self) -> str | None:
        return self._session

    @session.setter
    def session(self, value: str | None):
        self._session = value

    def login(self) -> None:
        endpoint = "login"
        url = self._url(endpoint)
        data = {"username": self.username, "password": self.password}
        logger.info(f"Logging in with username: {self.username}...")
        response = self._post(url, data)
        cookie = response.cookies.get("session")
        if not cookie:
            raise ValueError("No session cookie found, something wrong with the login...")
        logger.info(f"Session cookie successfully retrieved for username: {self.username}")
        self.session = cookie

    def _check_response(self, response: requests.Response) -> None:
        try:
            response_json = response.json()
        except ValueError as e:
            raise ValueError(f"Response is not in JSON format: {e}")
        status = response_json.get(ApiFields.SUCCESS)
        message = response_json.get(ApiFields.MSG)
        if not status:
            raise ValueError(f"Response status is not successful, message: {message}")

    def _url(self, endpoint: str) -> str:
        return f"{self._host}/{endpoint}"

    def _post(self, url: str, data: dict[str, Any]) -> requests.Response:
        logger.debug(f"POST request to {url}...")
        for retry in range(1, self.max_retries + 1):
            try:
                response = requests.post(url, json=data)
                response.raise_for_status()
                self._check_response(response)
                return response
            except (ConnectionError, Timeout) as e:
                if retry == self.max_retries:
                    raise e
                logger.warning(f"Request to {url} failed: {e}, retry {retry} of {self.max_retries}")
                sleep(1 * (retry + 1))
            except requests.exceptions.RequestException as e:
                raise e
        raise Exception(f"Max retries exceeded with no successful response to {url}")
