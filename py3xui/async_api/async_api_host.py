"""This module contains the AsyncHostApi class which provides methods to interact with the
subscription hosts in the XUI API asynchronously."""

from typing import Any
from urllib.parse import quote

from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_base import AsyncBaseApi
from py3xui.host import Host, HostGroup


class AsyncHostApi(AsyncBaseApi):
    """This class provides methods to interact with the hosts in the XUI API in an asynchronous
    manner.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (str): The session cookie for the XUI API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_list: Retrieves all host groups.
        get_raw_list: Retrieves all host rows with their numeric IDs.
        get_by_id: Retrieves a host group by its ID.
        get_by_inbound: Retrieves the host groups of an inbound.
        get_tags: Retrieves the tags used across all hosts.
        add: Adds a host group.
        update: Replaces the content of a host group.
        delete: Deletes a host group.
        set_enable: Enables or disables a host group.
        reorder: Sets the order of the host groups.
        bulk_add: Adds a host group to several inbounds.
        bulk_set_enable: Enables or disables several host groups.
        bulk_delete: Deletes several host groups.

    Examples:
        ```python
        import py3xui

        api = py3xui.AsyncApi.from_env()
        await api.login()

        groups: list[py3xui.HostGroup] = await api.host.get_list()
        ```
    """

    async def get_list(self) -> list[HostGroup]:
        """This route is used to retrieve all host groups across all inbounds.

        Returns:
            list[HostGroup]: A list of host groups.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            groups: list[py3xui.HostGroup] = await api.host.get_list()
            ```
        """
        endpoint = "panel/api/hosts/list"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting host groups...")

        response = await self._get(url, headers)

        groups_json = response.json().get(ApiFields.OBJ) or []
        return [HostGroup.model_validate(data) for data in groups_json]

    async def get_raw_list(self) -> list[Host]:
        """This route is used to retrieve all host rows with their numeric IDs, which is what the
        per-client host rules refer to.

        Returns:
            list[Host]: A list of host rows.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            hosts: list[py3xui.Host] = await api.host.get_raw_list()
            ```
        """
        endpoint = "panel/api/hosts/raw"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting host rows...")

        response = await self._get(url, headers)

        hosts_json = response.json().get(ApiFields.OBJ) or []
        return [Host.model_validate(data) for data in hosts_json]

    async def get_by_id(self, group_id: str) -> HostGroup:
        """This route is used to retrieve a host group by its ID.
        If the group is not found, the method will raise an exception.

        Arguments:
            group_id (str): The ID of the host group.

        Returns:
            HostGroup: The host group.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            group: py3xui.HostGroup = await api.host.get_by_id("1234567890123456")
            ```
        """
        endpoint = f"panel/api/hosts/get/{quote(group_id, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting host group by ID: %s", group_id)

        response = await self._get(url, headers)

        group_json = response.json().get(ApiFields.OBJ)
        return HostGroup.model_validate(group_json)

    async def get_by_inbound(self, inbound_id: int) -> list[HostGroup]:
        """This route is used to retrieve the host groups of an inbound.

        Arguments:
            inbound_id (int): The ID of the inbound.

        Returns:
            list[HostGroup]: A list of host groups, empty if the inbound has none.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            groups: list[py3xui.HostGroup] = await api.host.get_by_inbound(1)
            ```
        """
        endpoint = f"panel/api/hosts/byInbound/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting host groups of inbound: %s", inbound_id)

        response = await self._get(url, headers)

        groups_json = response.json().get(ApiFields.OBJ) or []
        return [HostGroup.model_validate(data) for data in groups_json]

    async def get_tags(self) -> list[str]:
        """This route is used to retrieve the distinct sorted tags used across all hosts.

        Returns:
            list[str]: A list of tags.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            tags: list[str] = await api.host.get_tags()
            ```
        """
        endpoint = "panel/api/hosts/tags"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting host tags...")

        response = await self._get(url, headers)

        return response.json().get(ApiFields.OBJ) or []

    async def add(self, host: HostGroup) -> list[Host]:
        """This route is used to add a host group. The panel generates the group ID if the model
        doesn't have one.

        Arguments:
            host (HostGroup): The host group to add.

        Returns:
            list[Host]: The created host rows, one per address and inbound.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            group = py3xui.HostGroup(
                inbound_ids=[1], remark="cdn-front", hosts=["cdn.example.com"], port=8443
            )
            hosts: list[py3xui.Host] = await api.host.add(group)
            ```
        """
        endpoint = "panel/api/hosts/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = host.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Adding host group: %s", host.remark)

        response = await self._post(url, headers, data)

        hosts_json = response.json().get(ApiFields.OBJ) or []
        return [Host.model_validate(row) for row in hosts_json]

    async def update(self, group_id: str, host: HostGroup) -> list[Host]:
        """This route is used to replace the content of a host group. Fields left at their default
        are reset on the panel, so get the group first and change only what is needed.

        Arguments:
            group_id (str): The ID of the host group.
            host (HostGroup): The new content of the host group.

        Returns:
            list[Host]: The host rows of the group after the update.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            group: py3xui.HostGroup = await api.host.get_by_id("1234567890123456")
            group.remark = "cdn-back"
            hosts: list[py3xui.Host] = await api.host.update(group.group_id, group)
            ```
        """
        endpoint = f"panel/api/hosts/update/{quote(group_id, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = host.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Updating host group: %s", group_id)

        response = await self._post(url, headers, data)

        hosts_json = response.json().get(ApiFields.OBJ) or []
        return [Host.model_validate(row) for row in hosts_json]

    async def delete(self, group_id: str) -> None:
        """This route is used to delete a host group.

        Arguments:
            group_id (str): The ID of the host group.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.host.delete("1234567890123456")
            ```
        """
        endpoint = f"panel/api/hosts/del/{quote(group_id, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}

        self.logger.info("Deleting host group: %s", group_id)
        await self._post(url, headers, data)
        self.logger.info("Host group deleted successfully.")

    async def set_enable(self, group_id: str, enable: bool) -> None:
        """This route is used to enable or disable a host group.

        Arguments:
            group_id (str): The ID of the host group.
            enable (bool): Whether the host group should be enabled.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.host.set_enable("1234567890123456", False)
            ```
        """
        endpoint = f"panel/api/hosts/setEnable/{quote(group_id, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"enable": enable}

        self.logger.info("Setting enable of host group %s to %s", group_id, enable)
        await self._post(url, headers, data)

    async def reorder(self, group_ids: list[str]) -> None:
        """This route is used to set the order of the host groups by their position in the list.
        The IDs must be unique, omitted groups follow in their previous order.

        Arguments:
            group_ids (list[str]): The IDs of the host groups in the desired order.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.host.reorder(["1234567890123456", "6543210987654321"])
            ```
        """
        endpoint = "panel/api/hosts/reorder"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"ids": group_ids}

        self.logger.info("Reordering host groups: %s", group_ids)
        await self._post(url, headers, data)

    async def bulk_add(self, host: HostGroup) -> list[Host]:
        """This route is used to add a host group to several inbounds. The panel handles it the
        same way as `add`.

        Arguments:
            host (HostGroup): The host group to add.

        Returns:
            list[Host]: The created host rows, one per address and inbound.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            group = py3xui.HostGroup(
                inbound_ids=[1, 2],
                remark="cdn-front",
                hosts=["cdn.example.com", "cdn2.example.com:443"],
            )
            hosts: list[py3xui.Host] = await api.host.bulk_add(group)
            ```
        """
        endpoint = "panel/api/hosts/bulk/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = host.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Adding host group in bulk: %s", host.remark)

        response = await self._post(url, headers, data)

        hosts_json = response.json().get(ApiFields.OBJ) or []
        return [Host.model_validate(row) for row in hosts_json]

    async def bulk_set_enable(self, group_ids: list[str], enable: bool) -> None:
        """This route is used to enable or disable several host groups in one call.

        Arguments:
            group_ids (list[str]): The IDs of the host groups.
            enable (bool): Whether the host groups should be enabled.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.host.bulk_set_enable(["1234567890123456", "6543210987654321"], False)
            ```
        """
        endpoint = "panel/api/hosts/bulk/setEnable"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"ids": group_ids, "enable": enable}

        self.logger.info("Setting enable of host groups %s to %s", group_ids, enable)
        await self._post(url, headers, data)

    async def bulk_delete(self, group_ids: list[str]) -> None:
        """This route is used to delete several host groups in one call.

        Arguments:
            group_ids (list[str]): The IDs of the host groups.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.host.bulk_delete(["1234567890123456", "6543210987654321"])
            ```
        """
        endpoint = "panel/api/hosts/bulk/del"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"ids": group_ids}

        self.logger.info("Deleting host groups: %s", group_ids)
        await self._post(url, headers, data)
        self.logger.info("Host groups deleted successfully.")
