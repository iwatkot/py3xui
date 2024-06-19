"""This module provides classes to interact with the XUI API."""

import json
from time import sleep
from typing import Any, Callable

import requests

from py3xui.client.client import Client
from py3xui.inbound.inbound import Inbound
from py3xui.utils import Logger, env

logger = Logger(__name__)


# pylint: disable=too-few-public-methods
class ApiFields:
    """Stores the fields returned by the XUI API for parsing."""

    SUCCESS = "success"
    MSG = "msg"
    OBJ = "obj"
    CLIENT_STATS = "clientStats"
    NO_IP_RECORD = "No IP Record"


class Api:
    def __init__(self, host: str, username: str, password: str, skip_login: bool = False):
        self._host = host.rstrip("/")
        self._username = username
        self._password = password
        self._max_retries: int = 3
        self._session: dict[str, str] | None = None
        if not skip_login:
            self.login()

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
    def session(self) -> dict[str, str] | None:
        return self._session

    @session.setter
    def session(self, value: dict[str, str] | None) -> None:
        self._session = value

    @classmethod
    def from_env(cls, skip_login: bool = False):
        host = env.xui_host()
        username = env.xui_username()
        password = env.xui_password()
        return cls(host, username, password, skip_login)

    def login(self) -> None:
        endpoint = "login"
        headers: dict[str, str] = {}

        url = self._url(endpoint)
        data = {"username": self.username, "password": self.password}
        logger.info("Logging in with username: %s", self.username)

        response = self._post(url, headers, data)
        cookie = response.cookies.get("session")
        if not cookie:
            raise ValueError("No session cookie found, something wrong with the login...")
        logger.info("Session cookie successfully retrieved for username: %s", self.username)
        self.session = {"session": cookie}

    def get_inbounds(self) -> list[Inbound]:
        endpoint = "panel/api/inbounds/list"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Getting inbounds...")

        response = self._get(url, headers)

        inbounds_json = response.json().get(ApiFields.OBJ)
        inbounds = [Inbound.model_validate(data) for data in inbounds_json]
        return inbounds

    def get_client(self, email: str) -> Client | None:
        """This route is used to retrieve information about a specific client based on their email.
        This endpoint provides details such as traffic statistics and other relevant information
        related to the client.

        `Source documentation <https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9d0e5cd5-e6ac-4d72-abca-76cf75af5f00>`_

        Args:
            email (str): The email of the client to retrieve.

        Returns:
            Client | None: The client object if found, otherwise None.

        Examples::
            import py3xui

            api = py3xui.Api.from_env()
            client: py3xui.Client = api.get_client("email")
        """  # pylint: disable=line-too-long

        endpoint = f"panel/api/inbounds/getClientTraffics/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Getting client stats for email: %s", email)

        response = self._get(url, headers)

        client_json = response.json().get(ApiFields.OBJ)
        if not client_json:
            logger.warning("No client found for email: %s", email)
            return None
        return Client.model_validate(client_json)

    def get_client_ips(self, email: str) -> str | None:
        """This route is used to retrieve the IP records associated with a specific client
        identified by their email.

        `Source documentation <https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#06f1214c-dbb0-49f2-81b5-8e924abd19a9>`_

        Args:
            email (str): The email of the client to retrieve.

        Returns:
            str | None: The client IPs if found, otherwise None.

        Examples::
            import py3xui

            api = py3xui.Api.from_env()
            ips = api.get_client_ips("email")

        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/clientIps/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Getting client IPs for email: %s", email)

        response = self._post(url, headers, {})

        ips_json = response.json().get(ApiFields.OBJ)
        return ips_json if ips_json != ApiFields.NO_IP_RECORD else None

    def add_inbound(self, inbound: Inbound) -> None:
        endpoint = "panel/api/inbounds/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        logger.info("Adding inbound: %s", inbound)

        self._post(url, headers, data)
        logger.info("Inbound added successfully.")

    def add_clients(self, inbound_id: int, clients: list[Client]):
        endpoint = "panel/api/inbounds/addClient"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        settings = {
            "clients": [
                client.model_dump(by_alias=True, exclude_defaults=True) for client in clients
            ]
        }
        data = {"id": inbound_id, "settings": json.dumps(settings)}
        logger.info("Adding %s clients to inbound with ID: %s", len(clients), inbound_id)

        self._post(url, headers, data)
        logger.info("Client added successfully.")

    def update_client(self, client_uuid: str, client: Client) -> None:
        endpoint = f"panel/api/inbounds/updateClient/{client_uuid}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        settings = {"clients": [client.model_dump(by_alias=True, exclude_defaults=True)]}
        data = {"id": client.inbound_id, "settings": json.dumps(settings)}

        logger.info("Updating client: %s", client)
        self._post(url, headers, data)
        logger.info("Client updated successfully.")

    def reset_client_ips(self, email: str) -> None:
        endpoint = f"panel/api/inbounds/clearClientIps/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {}
        logger.info("Resetting client IPs for email: %s", email)

        self._post(url, headers, data)
        logger.info("Client IPs reset successfully.")

    def delete_inbound(self, inbound_id: int) -> None:
        endpoint = f"panel/api/inbounds/del/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {}

        logger.info("Deleting inbound with ID: %s", inbound_id)
        self._post(url, headers, data)
        logger.info("Inbound deleted successfully.")

    def update_inbound(self, inbound_id: int, inbound: Inbound) -> None:
        endpoint = f"panel/api/inbounds/update/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        logger.info("Updating inbound: %s", inbound)

        self._post(url, headers, data)
        logger.info("Inbound updated successfully.")

    def reset_inbounds_stats(self) -> None:
        endpoint = "panel/api/inbounds/resetAllTraffics"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {}
        logger.info("Resetting inbounds stats...")

        self._post(url, headers, data)
        logger.info("Inbounds stats reset successfully.")

    def reset_inbound_client_stats(self, inbound_id: int) -> None:
        endpoint = f"panel/api/inbounds/resetAllClientTraffics/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {}
        logger.info("Resetting inbound client stats for ID: %s", inbound_id)

        self._post(url, headers, data)
        logger.info("Inbound client stats reset successfully.")

    def reset_client_stats(self, inbound_id: int, email: str) -> None:
        endpoint = f"panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {}
        logger.info("Resetting client stats for inbound ID: %s, email: %s", inbound_id, email)

        self._post(url, headers, data)
        logger.info("Client stats reset successfully.")

    def _check_response(self, response: requests.Response) -> None:
        response_json = response.json()

        status = response_json.get(ApiFields.SUCCESS)
        message = response_json.get(ApiFields.MSG)
        if not status:
            raise ValueError(f"Response status is not successful, message: {message}")

    def _url(self, endpoint: str) -> str:
        return f"{self._host}/{endpoint}"

    def _request_with_retry(
        self,
        method: Callable[..., requests.Response],
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> requests.Response:
        logger.debug("%s request to %s...", method.__name__.upper(), url)
        for retry in range(1, self.max_retries + 1):
            try:
                response = method(url, cookies=self.session, headers=headers, **kwargs)
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

    def _post(self, url: str, headers: dict[str, str], data: dict[str, Any]) -> requests.Response:
        return self._request_with_retry(requests.post, url, headers, json=data)

    def _get(self, url: str, headers: dict[str, str]) -> requests.Response:
        return self._request_with_retry(requests.get, url, headers)
