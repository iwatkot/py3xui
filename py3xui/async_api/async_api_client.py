"""This module contains the ClientApi class which provides methods to interact with the
clients in the XUI API."""

import json
from typing import Any

from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_base import AsyncBaseApi
from py3xui.client.client import Client
from py3xui.utils import Logger

logger = Logger(__name__)


class AsyncClientApi(AsyncBaseApi):
    """This class provides async methods to interact with the clients in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_by_email: Retrieves a client by email.
        get_ips: Retrieves the IPs associated with a client.
        add: Adds clients to an inbound.
        update: Updates a client.
        reset_ips: Resets the IPs associated with a client.
        reset_stats: Resets the statistics of a client.
        delete: Deletes a client.
        delete_depleted: Deletes depleted clients.
        online: Retrieves online clients.

    Examples:
        ```python
        import uuid
        import py3xui

        api = py3xui.AsyncApi.from_env()

        client: py3xui.Client = api.client.get_by_email("email")

        new_client = py3xui.Client(id=new_uuid, email="test", enable=True)
        inbound_id = 1
        api.client.add(inbound_id, [new_client])
        ```
    """

    async def get_by_email(self, email: str) -> Client | None:
        """This route is used to retrieve information about a specific client based on their email.
        This endpoint provides details such as traffic statistics and other relevant information
        related to the client.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9d0e5cd5-e6ac-4d72-abca-76cf75af5f00)

        Arguments:
            email (str): The email of the client to retrieve.

        Returns:
            Client | None: The client object if found, otherwise None.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            client: py3xui.Client = await api.client.get_by_email("email")
            ```
        """  # pylint: disable=line-too-long

        endpoint = f"panel/api/inbounds/getClientTraffics/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Getting client stats for email: %s", email)

        response = await self._get(url, headers)

        client_json = response.json().get(ApiFields.OBJ)
        if not client_json:
            logger.warning("No client found for email: %s", email)
            return None
        return Client.model_validate(client_json)
