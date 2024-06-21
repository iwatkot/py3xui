"""This module contains the ClientApi class which provides methods to interact with the
clients in the XUI API."""

import json
from typing import Any

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.client import Client
from py3xui.utils import Logger

logger = Logger(__name__)


class ClientApi(BaseApi):
    """This class provides methods to interact with the clients in the XUI API.

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

        api = py3xui.Api.from_env()

        client: py3xui.Client = api.client.get_by_email("email")

        new_client = py3xui.Client(id=new_uuid, email="test", enable=True)
        inbound_id = 1
        api.client.add(inbound_id, [new_client])
        ```
    """

    def get_by_email(self, email: str) -> Client | None:
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

            api = py3xui.Api.from_env()
            client: py3xui.Client = api.client.get_by_email("email")
            ```
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

    def get_ips(self, email: str) -> list[str]:
        """This route is used to retrieve the IP records associated with a specific client
        identified by their email.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#06f1214c-dbb0-49f2-81b5-8e924abd19a9)

        Arguments:
            email (str): The email of the client to retrieve.

        Returns:
            list[str]: The list of IP records associated with the client.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            ips = api.client.get_ips("email")
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/clientIps/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Getting client IPs for email: %s", email)

        response = self._post(url, headers, {})

        ips_json = response.json().get(ApiFields.OBJ)
        return ips_json if ips_json != ApiFields.NO_IP_RECORD else []

    def add(self, inbound_id: int, clients: list[Client]):
        """This route is used to add a new clients to a specific inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#c4d325ae-fbb4-44e9-bd2e-29eebb7fbc52)

        Arguments:
            inbound_id (int): The ID of the inbound to add the clients to.
            clients (list[Client]): The list of clients to add.

        Examples:
            ```python
            import uuid
            import py3xui

            api = py3xui.Api.from_env()

            new_client = py3xui.Client(id=str(uuid.uuid4()), email="test", enable=True)
            inbound_id = 1

            api.client.add(inbound_id, [new_client])
        """  # pylint: disable=line-too-long
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

    def update(self, client_uuid: str, client: Client) -> None:
        """This route is used to update an existing client identified by its UUID within a specific
        inbound.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#af1bee51-199c-4176-b3ab-d325ba2fae19)

        Arguments:
            client_uuid (str): The UUID of the client to update.
            client (Client): The client object with updated information.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            client = api.client.get_by_email("email")
            client.email = "newemail"
            api.client.update(client.id, client)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/updateClient/{client_uuid}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        settings = {"clients": [client.model_dump(by_alias=True, exclude_defaults=True)]}
        data = {"id": client.inbound_id, "settings": json.dumps(settings)}

        logger.info("Updating client: %s", client)
        self._post(url, headers, data)
        logger.info("Client updated successfully.")

    def reset_ips(self, email: str) -> None:
        """This route is used to reset or clear the IP records associated with a specific client
        identified by their email address.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#7af93bc4-693a-4fa4-8560-0642783af6f3)

        Arguments:
            email (str): The email of the client to reset the IPs for.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()

            api.client.reset_ips("email")
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/clearClientIps/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Resetting client IPs for email: %s", email)

        self._post(url, headers, data)
        logger.info("Client IPs reset successfully.")

    def reset_stats(self, inbound_id: int, email: str) -> None:
        """This route is used to reset the traffic statistics for a specific client identified by
        their email address  within a particular inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#52081826-8e06-4dc1-9bad-8a95f1cd8a96)

        Arguments:
            inbound_id (int): The ID of the inbound to reset the client stats.
            email (str): The email of the client to reset the stats for.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            inbound_id = 1

            api.client.reset_stats(inbound_id, "test")
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Resetting client stats for inbound ID: %s, email: %s", inbound_id, email)

        self._post(url, headers, data)
        logger.info("Client stats reset successfully.")

    def delete(self, inbound_id: int, client_uuid: str) -> None:
        """This route is used to delete a client identified by its UUID within a specific inbound
        identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#97aa9d0e-9cc3-46db-a364-c2fda39586bd)

        Arguments:
            inbound_id (int): The ID of the inbound to delete the client from.
            client_uuid (str): The UUID of the client to delete.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            client = api.client.get_by_email("email")
            inbound_id = 1

            api.client.delete(inbound_id, client.id)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/{inbound_id}/delClient/{client_uuid}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Deleting client with ID: %s", client_uuid)

        self._post(url, headers, data)
        logger.info("Client deleted successfully.")

    def delete_depleted(self, inbound_id: int) -> None:
        """This route is used to delete all depleted clients associated with a specific inbound
        identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#8f4975c9-1051-43cb-afa7-c42ca2542c6b)

        Arguments:
            inbound_id (int): The ID of the inbound to delete the depleted clients from.

        Examples:

            ```python
            import py3xui

            api = py3xui.Api.from_env()

            inbounds: list[py3xui.Inbound] = api.inbound.get_list()

            for inbound in inbounds:
                api.client.delete_depleted(inbound.id)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/delDepletedClients/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Deleting depleted clients for inbound ID: %s", inbound_id)

        self._post(url, headers, data)
        logger.info("Depleted clients deleted successfully.")

    def online(self) -> list[str]:
        """Returns a list of email addresses of online clients.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9cac8101-017e-4415-94e2-d30f4dcf49de)

        Returns:
            list[str]: The list of email addresses of online clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            res = api.client.online()
            print(res)
            ```

        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/onlines"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Getting online clients")

        response = self._post(url, headers, data)
        online = response.json().get(ApiFields.OBJ)
        return online or []
