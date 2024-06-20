"""This module contains the InboundApi class for handling inbounds in the XUI API."""

from typing import Any

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.inbound import Inbound
from py3xui.utils import Logger

logger = Logger(__name__)


class InboundApi(BaseApi):
    """This class provides methods to interact with the inbounds in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_list: Retrieves a list of inbounds.
        add: Adds a new inbound.
        delete: Deletes an inbound.
        update: Updates an inbound.
        reset_stats: Resets the statistics of all inbounds.
        reset_client_stats: Resets the statistics of a specific inbound.

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()

        inbounds: list[py3xui.Inbound] = api.inbound.get_list()
        ```
    """

    def get_list(self) -> list[Inbound]:
        """This route is used to retrieve a comprehensive list of all inbounds along with
        their associated client options and statistics.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#b7c42b67-4362-44d3-bd61-ba7df0721802)

        Returns:
            list[Inbound]: A list of inbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()

            inbounds: list[py3xui.Inbound] = api.inbound.get_list()
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/list"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Getting inbounds...")

        response = self._get(url, headers)

        inbounds_json = response.json().get(ApiFields.OBJ)
        inbounds = [Inbound.model_validate(data) for data in inbounds_json]
        return inbounds

    def add(self, inbound: Inbound) -> None:
        """This route is used to add a new inbound configuration.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#813ac729-5ba6-4314-bc2a-d0d3acc70388)

        Arguments:
            inbound (Inbound): The inbound object to add.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()

            settings = Settings()
            sniffing = Sniffing(enabled=True)

            tcp_settings = {
                "acceptProxyProtocol": False,
                "header": {"type": "none"},
            }
            stream_settings = StreamSettings(security="reality", network="tcp", tcp_settings=tcp_settings)

            inbound = Inbound(
                enable=True,
                port=443,
                protocol="vless",
                settings=settings,
                stream_settings=stream_settings,
                sniffing=sniffing,
                remark="test3",
            )
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        logger.info("Adding inbound: %s", inbound)

        self._post(url, headers, data)
        logger.info("Inbound added successfully.")

    def delete(self, inbound_id: int) -> None:
        """This route is used to delete an inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#a655d0e3-7d8c-4331-9061-422fcb515da9)

        Arguments:
            inbound_id (int): The ID of the inbound to delete.

        Examples:

            ```python
            import py3xui

            api = py3xui.Api.from_env()
            inbounds: list[py3xui.Inbound] = api.inbound.get_list()

            for inbound in inbounds:
                api.inbound.delete(inbound.id)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/del/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}

        logger.info("Deleting inbound with ID: %s", inbound_id)
        self._post(url, headers, data)
        logger.info("Inbound deleted successfully.")

    def update(self, inbound_id: int, inbound: Inbound) -> None:
        """This route is used to update an existing inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#19249b9f-a940-41e2-8bf4-86ff8dde857e)

        Arguments:
            inbound_id (int): The ID of the inbound to update.
            inbound (Inbound): The inbound object to update.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            inbounds: list[py3xui.Inbound] = api.inbound.get_list()
            inbound = inbounds[0]

            inbound.remark = "updated"

            api.inbound.update(inbound.id, inbound)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/update/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        logger.info("Updating inbound: %s", inbound)

        self._post(url, headers, data)
        logger.info("Inbound updated successfully.")

    def reset_stats(self) -> None:
        """This route is used to reset the traffic statistics for all inbounds within the system.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#6749f362-dc81-4769-8f45-37dc9e99f5e9)

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.inbound.reset_stats()
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/resetAllTraffics"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Resetting inbounds stats...")

        self._post(url, headers, data)
        logger.info("Inbounds stats reset successfully.")

    def reset_client_stats(self, inbound_id: int) -> None:
        """This route is used to reset the traffic statistics for all clients associated with a
        specific inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9bd93925-12a0-40d8-a390-d4874dea3683)

        Arguments:
            inbound_id (int): The ID of the inbound to reset the client stats.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            inbounds: list[py3xui.Inbound] = api.inbound.get_list()
            inbound = inbounds[0]

            api.inbound.reset_client_stats(inbound.id)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/resetAllClientTraffics/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Resetting inbound client stats for ID: %s", inbound_id)

        self._post(url, headers, data)
        logger.info("Inbound client stats reset successfully.")
