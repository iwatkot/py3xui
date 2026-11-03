"""This module contains the InboundApi class which provides methods to interact with the
clients in the XUI API asynchronously."""

import json
from typing import Any

from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_base import AsyncBaseApi
from py3xui.client import Client
from py3xui.inbound import (
    AmneziaWGReadiness,
    Inbound,
    InboundBulkDeleteResult,
    InboundClientsDeleteResult,
    InboundFallback,
    InboundOption,
)


class AsyncInboundApi(AsyncBaseApi):
    """This class provides methods to interact with the inbounds in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_list: Retrieves a list of inbounds.
        add: Adds a new inbound.
        delete: Deletes an inbound.
        update: Updates an inbound.
        reset_stats: Resets the statistics of all inbounds.
        reset_client_stats: Resets the statistics of a specific inbound.
        get_list_slim: Retrieves a list of inbounds without full client payloads.
        get_options: Retrieves a lightweight projection of the inbounds.
        get_amneziawg_kernel_readiness: Checks whether the host can run kernel AmneziaWG.
        get_all_links: Retrieves the share links of all inbounds.
        bulk_delete: Deletes several inbounds.
        set_enable: Enables or disables an inbound.
        set_sub_sort_index: Sets the subscription sort index of an inbound.
        reset_stats_by_id: Resets the statistics of a specific inbound.
        delete_all_clients: Deletes all clients of an inbound.
        import_inbound: Imports an inbound.
        push_client_traffics: Pushes the aggregated client traffic from a master panel.
        get_fallbacks: Retrieves the fallback rules of an inbound.
        set_fallbacks: Replaces the fallback rules of an inbound.

    Examples:
        ```python
        import py3xui

        api = py3xui.AsyncApi.from_env()
        await api.login()

        inbounds: list[py3xui.Inbound] = await api.inbound.get_list()
        ```
    """

    async def get_list(self) -> list[Inbound]:
        """This route is used to retrieve a comprehensive list of all inbounds along with
        their associated client options and statistics.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#b7c42b67-4362-44d3-bd61-ba7df0721802)

        Returns:
            list[Inbound]: A list of inbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()
            inbounds: list[py3xui.Inbound] = await api.inbound.get_list()
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/list"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting inbounds...")

        response = await self._get(url, headers)

        inbounds_json = response.json().get(ApiFields.OBJ)
        inbounds = [Inbound.model_validate(data) for data in inbounds_json]
        return inbounds

    async def get_by_id(self, inbound_id: int) -> Inbound:
        """This route is used to retrieve statistics and details for a specific inbound connection
        identified by specified ID. This includes information about the inbound itself, its
        statistics, and the clients connected to it.
        If the inbound is not found, the method will raise an exception.

        [Source documentation](https://www.postman.com/hsanaei/3x-ui/request/uu7wm1k/inbound)

        Arguments:
            inbound_id (int): The ID of the inbound to retrieve.

        Returns:
            Inbound | None: The inbound object if found, otherwise None.

        Examples:

            ```python

            import py3xui

            api = py3xui.AsyncApi.from_env()

            await api.login()

            inbound_id = 1

            inbound = await api.inbound.get_by_id(inbound_id)
        """
        endpoint = f"panel/api/inbounds/get/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting inbound by ID: %s", inbound_id)

        response = await self._get(url, headers)

        inbound_json = response.json().get(ApiFields.OBJ)
        inbound = Inbound.model_validate(inbound_json)
        return inbound

    async def add(self, inbound: Inbound) -> None:
        """This route is used to add a new inbound configuration.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#813ac729-5ba6-4314-bc2a-d0d3acc70388)

        Arguments:
            inbound (Inbound): The inbound object to add.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

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
            await api.inbound.add(inbound)
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        self.logger.info("Adding inbound: %s", inbound)

        await self._post(url, headers, data)
        self.logger.info("Inbound added successfully.")

    async def delete(self, inbound_id: int) -> None:
        """This route is used to delete an inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#a655d0e3-7d8c-4331-9061-422fcb515da9)

        Arguments:
            inbound_id (int): The ID of the inbound to delete.

        Examples:

            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()
            inbounds: list[py3xui.Inbound] = await api.inbound.get_list()

            for inbound in inbounds:
                api.inbound.delete(inbound.id)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/del/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}

        self.logger.info("Deleting inbound with ID: %s", inbound_id)
        await self._post(url, headers, data)
        self.logger.info("Inbound deleted successfully.")

    async def update(self, inbound_id: int, inbound: Inbound) -> None:
        """This route is used to update an existing inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#19249b9f-a940-41e2-8bf4-86ff8dde857e)

        Arguments:
            inbound_id (int): The ID of the inbound to update.
            inbound (Inbound): The inbound object to update.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()
            inbounds: list[py3xui.Inbound] = await api.inbound.get_list()
            inbound = inbounds[0]

            inbound.remark = "updated"

            api.inbound.update(inbound.id, inbound)
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/inbounds/update/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        self.logger.info("Updating inbound: %s", inbound)

        await self._post(url, headers, data)
        self.logger.info("Inbound updated successfully.")

    async def reset_stats(self) -> None:
        """This route is used to reset the traffic statistics for all inbounds within the system.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#6749f362-dc81-4769-8f45-37dc9e99f5e9)

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()
            await api.inbound.reset_stats()
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/inbounds/resetAllTraffics"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Resetting inbounds stats...")

        await self._post(url, headers, data)
        self.logger.info("Inbounds stats reset successfully.")

    async def reset_client_stats(self, inbound_id: int) -> None:
        """This route is used to reset the traffic statistics for all clients associated with a
        specific inbound identified by its ID.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9bd93925-12a0-40d8-a390-d4874dea3683)

        Arguments:
            inbound_id (int): The ID of the inbound to reset the client stats.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()
            inbounds: list[py3xui.Inbound] = await api.inbound.get_list()
            inbound = inbounds[0]

            await api.inbound.reset_client_stats(inbound.id)
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/clients/resetAllTraffics"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info(
            "Resetting inbound client stats for ID: %s (global clients reset endpoint)",
            inbound_id,
        )

        await self._post(url, headers, data)
        self.logger.info("Inbound client stats reset successfully.")

    async def get_list_slim(self) -> list[Inbound]:
        """This route is used to retrieve the list of inbounds without full client payloads:
        every client in the inbound settings keeps only the email, enable and comment fields.
        Use `get_by_id` to get the full client data of an inbound.

        Returns:
            list[Inbound]: A list of inbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            inbounds: list[py3xui.Inbound] = await api.inbound.get_list_slim()
            ```
        """
        endpoint = "panel/api/inbounds/list/slim"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting slim inbounds list...")

        response = await self._get(url, headers)

        inbounds_json = response.json().get(ApiFields.OBJ) or []
        return [Inbound.model_validate(data) for data in inbounds_json]

    async def get_options(self) -> list[InboundOption]:
        """This route is used to retrieve a lightweight projection of the inbounds (ID, remark,
        protocol, port and share hints) without client settings and traffic statistics.

        Returns:
            list[InboundOption]: A list of inbound options.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            options: list[py3xui.InboundOption] = await api.inbound.get_options()
            ```
        """
        endpoint = "panel/api/inbounds/options"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting inbound options...")

        response = await self._get(url, headers)

        options_json = response.json().get(ApiFields.OBJ) or []
        return [InboundOption.model_validate(data) for data in options_json]

    async def get_amneziawg_kernel_readiness(self) -> AmneziaWGReadiness:
        """This route is used to check whether the panel host can run kernel-mode AmneziaWG
        inbounds and which requirements are missing.

        Returns:
            AmneziaWGReadiness: The host readiness.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            readiness = await api.inbound.get_amneziawg_kernel_readiness()
            if not readiness.ready:
                print(readiness.install_command)
            ```
        """
        endpoint = "panel/api/inbounds/amneziawgKernelReadiness"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting AmneziaWG kernel readiness...")

        response = await self._get(url, headers)

        readiness_json = response.json().get(ApiFields.OBJ)
        return AmneziaWGReadiness.model_validate(readiness_json)

    async def get_all_links(self) -> list[str]:
        """This route is used to retrieve the share links of every client of every inbound.

        Returns:
            list[str]: A list of share links.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            links: list[str] = await api.inbound.get_all_links()
            ```
        """
        endpoint = "panel/api/inbounds/allLinks"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting share links of all inbounds...")

        response = await self._get(url, headers)

        links: list[str] = response.json().get(ApiFields.OBJ) or []
        return links

    async def bulk_delete(self, inbound_ids: list[int]) -> InboundBulkDeleteResult:
        """This route is used to delete several inbounds in one call. Inbounds that can not be
        deleted are reported in the result, the rest are still deleted.

        Arguments:
            inbound_ids (list[int]): The IDs of the inbounds to delete.

        Returns:
            InboundBulkDeleteResult: The number of deleted inbounds and the skipped ones.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result = await api.inbound.bulk_delete([1, 2, 3])
            print(result.deleted, result.skipped)
            ```
        """
        endpoint = "panel/api/inbounds/bulkDel"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"ids": inbound_ids}
        self.logger.info("Deleting inbounds with IDs: %s", inbound_ids)

        response = await self._post(url, headers, data)

        result_json = response.json().get(ApiFields.OBJ) or {}
        return InboundBulkDeleteResult.model_validate(result_json)

    async def set_enable(self, inbound_id: int, enable: bool) -> None:
        """This route is used to enable or disable an inbound without sending its settings.

        Arguments:
            inbound_id (int): The ID of the inbound.
            enable (bool): Whether the inbound should be enabled.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.inbound.set_enable(1, False)
            ```
        """
        endpoint = f"panel/api/inbounds/setEnable/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"enable": enable}
        self.logger.info("Setting enable=%s for inbound with ID: %s", enable, inbound_id)

        await self._post(url, headers, data)
        self.logger.info("Inbound enable state set successfully.")

    async def set_sub_sort_index(self, inbound_id: int, index: int) -> None:
        """This route is used to change the position of the inbound's links in the subscription
        output (lower first, negative values are allowed). The panel rejects 0: the default
        position is 1.

        Arguments:
            inbound_id (int): The ID of the inbound.
            index (int): The subscription sort index.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.inbound.set_sub_sort_index(1, 2)
            ```
        """
        endpoint = f"panel/api/inbounds/{inbound_id}/subSortIndex"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"subSortIndex": index}
        self.logger.info("Setting sub sort index %s for inbound with ID: %s", index, inbound_id)

        await self._post(url, headers, data)
        self.logger.info("Inbound subscription sort index set successfully.")

    async def reset_stats_by_id(self, inbound_id: int) -> None:
        """This route is used to reset the traffic statistics of a specific inbound.

        Arguments:
            inbound_id (int): The ID of the inbound.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.inbound.reset_stats_by_id(1)
            ```
        """
        endpoint = f"panel/api/inbounds/{inbound_id}/resetTraffic"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Resetting stats for inbound with ID: %s", inbound_id)

        await self._post(url, headers, data)
        self.logger.info("Inbound stats reset successfully.")

    async def delete_all_clients(self, inbound_id: int) -> InboundClientsDeleteResult:
        """This route is used to delete every client of a specific inbound while keeping the
        inbound itself.

        Arguments:
            inbound_id (int): The ID of the inbound.

        Returns:
            InboundClientsDeleteResult: The number of deleted clients and the skipped ones.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result = await api.inbound.delete_all_clients(1)
            print(result.deleted)
            ```
        """
        endpoint = f"panel/api/inbounds/{inbound_id}/delAllClients"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Deleting all clients of inbound with ID: %s", inbound_id)

        response = await self._post(url, headers, data)

        result_json = response.json().get(ApiFields.OBJ) or {}
        return InboundClientsDeleteResult.model_validate(result_json)

    async def import_inbound(self, inbound: Inbound | str) -> Inbound:
        """This route is used to import an inbound. The panel assigns a new ID and returns the
        created inbound.

        An `Inbound` carries only the fields of the model: protocol-specific settings (for example
        the Shadowsocks method or the WireGuard peers) and panel options (for example the traffic
        reset schedule) are not kept. To import an exported inbound as is, pass its raw JSON.

        Arguments:
            inbound (Inbound | str): The inbound to import or its raw JSON string.

        Returns:
            Inbound: The created inbound.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            with open("inbound.json", encoding="utf-8") as file:
                created = await api.inbound.import_inbound(file.read())
            print(created.id)
            ```
        """
        endpoint = "panel/api/inbounds/import"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        if isinstance(inbound, str):
            raw = inbound
        else:
            payload = inbound.to_json()
            payload.update({"up": inbound.up, "down": inbound.down, "total": inbound.total})
            raw = json.dumps(payload)
        data: dict[str, Any] = {"data": raw}
        self.logger.info("Importing inbound...")

        response = await self._post_form(url, headers, data)

        inbound_json = response.json().get(ApiFields.OBJ)
        return Inbound.model_validate(inbound_json)

    async def push_client_traffics(self, master_guid: str, traffics: list[Client]) -> None:
        """This route is used by a master panel to push the aggregated traffic of the clients
        hosted on this panel (node). Only the email, up and down values of each client are
        sent. The panel reports success without storing anything for an empty GUID and skips
        unknown emails.

        Arguments:
            master_guid (str): The stable GUID of the pushing master panel.
            traffics (list[Client]): The clients with their traffic counters.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            client = py3xui.Client(email="alice", enable=True, up=1024, down=2048)
            await api.inbound.push_client_traffics("9f6c2d0e-master-guid", [client])
            ```
        """
        endpoint = "panel/api/inbounds/pushClientTraffics"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {
            "masterGuid": master_guid,
            "traffics": [
                {"email": client.email, "up": client.up, "down": client.down}
                for client in traffics
            ],
        }
        self.logger.info("Pushing traffic of %s clients from master %s", len(traffics), master_guid)

        await self._post(url, headers, data)
        self.logger.info("Client traffics pushed successfully.")

    async def get_fallbacks(self, inbound_id: int) -> list[InboundFallback]:
        """This route is used to retrieve the fallback rules of a master inbound.

        Arguments:
            inbound_id (int): The ID of the master inbound.

        Returns:
            list[InboundFallback]: A list of fallback rules.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            fallbacks: list[py3xui.InboundFallback] = await api.inbound.get_fallbacks(1)
            ```
        """
        endpoint = f"panel/api/inbounds/{inbound_id}/fallbacks"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting fallbacks of inbound with ID: %s", inbound_id)

        response = await self._get(url, headers)

        fallbacks_json = response.json().get(ApiFields.OBJ) or []
        return [InboundFallback.model_validate(data) for data in fallbacks_json]

    async def set_fallbacks(self, inbound_id: int, fallbacks: list[InboundFallback]) -> None:
        """This route is used to replace the whole list of fallback rules of a master inbound.
        Rules without a child inbound and without a destination are dropped by the panel.

        Arguments:
            inbound_id (int): The ID of the master inbound.
            fallbacks (list[InboundFallback]): The new fallback rules.

        Examples:
            ```python
            import py3xui
            from py3xui import InboundFallback

            api = py3xui.AsyncApi.from_env()
            await api.login()

            fallbacks = [
                InboundFallback(child_id=11, path="/vlws", xver=2),
                InboundFallback(child_id=12, alpn="h2", dest="8443"),
            ]
            await api.inbound.set_fallbacks(10, fallbacks)
            ```
        """
        endpoint = f"panel/api/inbounds/{inbound_id}/fallbacks"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {
            "fallbacks": [
                fallback.model_dump(
                    by_alias=True, exclude_defaults=True, exclude={"id", "master_id"}
                )
                for fallback in fallbacks
            ]
        }
        self.logger.info("Setting %s fallbacks for inbound with ID: %s", len(fallbacks), inbound_id)

        await self._post(url, headers, data)
        self.logger.info("Inbound fallbacks set successfully.")
