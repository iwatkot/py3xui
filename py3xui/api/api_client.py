"""This module contains the ClientApi class which provides methods to interact with the
clients in the XUI API."""

# pylint: disable=R0801,too-many-lines

import json
from typing import Any, cast
from urllib.parse import quote

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.client import (
    BulkAttachResult,
    BulkDetachResult,
    BulkResult,
    Client,
    ClientDetails,
    ClientEntry,
    ClientExternalLink,
    ClientGroup,
    ClientHwid,
    ClientIpEntry,
    ClientPage,
    ClientRenewalPreview,
    ClientTraffic,
)


class ClientApi(BaseApi):  # pylint: disable=too-many-public-methods
    """This class provides methods to interact with the clients in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_by_email: Retrieves a client by email.
        get_details: Retrieves full client details by email.
        get_ips: Retrieves the IPs associated with a client.
        add: Adds clients to an inbound.
        update: Updates a client.
        reset_ips: Resets the IPs associated with a client.
        reset_stats: Resets the statistics of a client.
        delete: Deletes a client.
        delete_depleted: Deletes depleted clients.
        online: Retrieves online clients.
        get_list_paged: Retrieves one page of clients, filtered and sorted.
        get_details_by_sub_id: Retrieves full client details by subscription ID.
        get_details_by_tg_id: Retrieves full client details by Telegram ID.
        get_renewal_preview: Previews the auto-renewal dates of a client.
        get_traffic: Retrieves the traffic counters of a client.
        get_sub_links: Retrieves the share links of a subscription.
        get_links: Retrieves the share links of a client.
        get_happ_link: Generates an encrypted Happ link for a client.
        attach: Attaches a client to inbounds.
        detach: Detaches a client from inbounds.
        set_external_links: Replaces the external links of a client.
        delete_orphans: Deletes clients without inbounds.
        export_clients: Exports all clients.
        import_clients: Imports clients.
        bulk_adjust: Shifts the expiry and traffic limit of many clients.
        bulk_enable: Enables many clients.
        bulk_disable: Disables many clients.
        bulk_delete: Deletes many clients.
        bulk_add: Creates many clients.
        bulk_attach: Attaches many clients to inbounds.
        bulk_detach: Detaches many clients from inbounds.
        bulk_reset_stats: Resets the traffic counters of many clients.
        get_groups: Retrieves all client groups.
        get_group_emails: Retrieves the emails of a client group.
        add_group: Creates a client group.
        rename_group: Renames a client group.
        delete_group: Deletes a client group.
        reset_group_stats: Resets the traffic counter of a client group.
        bulk_add_to_group: Adds many clients to a group.
        bulk_remove_from_group: Clears the group of many clients.
        update_traffic: Sets the traffic counters of a client.
        get_hwids: Retrieves the devices of a client.
        delete_hwids: Deletes all devices of a client.
        delete_hwid: Deletes one device of a client.
        online_by_guid: Retrieves online clients by panel GUID.
        get_ips_by_guid: Retrieves client IPs by panel GUID.
        get_active_inbounds: Retrieves active inbound tags by panel GUID.
        get_last_online: Retrieves the last online time of clients.

    Examples:
        ```python
        import uuid
        import py3xui

        api = py3xui.Api.from_env()
        api.login()

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
            api.login()
            client: py3xui.Client = api.client.get_by_email("email")
            ```
        """  # pylint: disable=line-too-long

        endpoint = f"panel/api/clients/get/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client stats for email: %s", email)

        response = self._get(url, headers)

        client_json = response.json().get(ApiFields.OBJ)
        if not client_json:
            self.logger.warning("No client found for email: %s", email)
            return None

        if isinstance(client_json, dict) and isinstance(client_json.get("client"), dict):
            client_payload = dict(client_json["client"])
            inbound_ids = client_json.get("inboundIds")
            if isinstance(inbound_ids, list) and inbound_ids:
                client_payload.setdefault("inboundId", inbound_ids[0])
            return Client.model_validate(client_payload)

        return Client.model_validate(client_json)

    def get_details(self, email: str) -> ClientDetails | None:
        """This route is used to retrieve the full information about a specific client based on
        their email: the client itself, all inbounds it is attached to, its external links, used
        traffic and tunnel addresses.

        Unlike `get_by_email`, the result keeps every inbound ID and the tunnel allowed IPs, and
        `details.client` can be passed to `update` without losing any client field.

        Arguments:
            email (str): The email of the client to retrieve.

        Returns:
            ClientDetails | None: The client details if found, otherwise None.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            details = api.client.get_details("email")
            details.client.total_gb = 50 * 1024**3
            api.client.update(details.client.uuid, details.client)
            ```
        """
        endpoint = f"panel/api/clients/get/{quote(email, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client details for email: %s", email)

        response = self._get(url, headers)

        details_json = response.json().get(ApiFields.OBJ)
        if not details_json:
            self.logger.warning("No client found for email: %s", email)
            return None

        return ClientDetails.model_validate(details_json)

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
            api.login()
            ips = api.client.get_ips("email")
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/clients/ips/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client IPs for email: %s", email)

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
            api.login()
            new_client = py3xui.Client(id=str(uuid.uuid4()), email="test", enable=True)
            inbound_id = 1

            api.client.add(inbound_id, [new_client])
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/clients/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Adding %s clients to inbound with ID: %s", len(clients), inbound_id)

        for client in clients:
            data = {
                "client": client.model_dump(by_alias=True, exclude_defaults=True),
                "inboundIds": [inbound_id],
            }
            self._post(url, headers, data)
        self.logger.info("Client added successfully.")

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
            api.login()
            client = api.client.get_by_email("email")
            client.email = "newemail"
            api.client.update(client.id, client)
            ```
        """  # pylint: disable=line-too-long
        target_email = client.email or str(client_uuid)
        endpoint = f"panel/api/clients/update/{target_email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = client.model_dump(by_alias=True, exclude_defaults=True)
        if isinstance(data.get("uuid"), str) and not isinstance(data.get("id"), str):
            data["id"] = data["uuid"]

        self.logger.info("Updating client: %s", client)
        self._post(url, headers, data)
        self.logger.info("Client updated successfully.")

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
            api.login()
            api.client.reset_ips("email")
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/clients/clearIps/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Resetting client IPs for email: %s", email)

        self._post(url, headers, data)
        self.logger.info("Client IPs reset successfully.")

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
            api.login()
            inbound_id = 1

            api.client.reset_stats(inbound_id, "test")
            ```
        """  # pylint: disable=line-too-long
        endpoint = f"panel/api/clients/resetTraffic/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info(
            "Resetting client stats for inbound ID: %s, email: %s", inbound_id, email
        )

        self._post(url, headers, data)
        self.logger.info("Client stats reset successfully.")

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
            api.login()
            client = api.client.get_by_email("email")
            inbound_id = 1

            api.client.delete(inbound_id, client.id)
            ```
        """  # pylint: disable=line-too-long
        email = self._resolve_client_email(inbound_id=inbound_id, client_identifier=client_uuid)
        endpoint = f"panel/api/clients/del/{email}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Deleting client by email: %s", email)

        self._post(url, headers, data)
        self.logger.info("Client deleted successfully.")

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
            api.login()
            inbounds: list[py3xui.Inbound] = api.inbound.get_list()

            for inbound in inbounds:
                api.client.delete_depleted(inbound.id)
            ```
        """  # pylint: disable=line-too-long
        endpoint = "panel/api/clients/delDepleted"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info(
            "Deleting depleted clients for inbound ID: %s", inbound_id
        )

        self._post(url, headers, data)
        self.logger.info("Depleted clients deleted successfully.")

    def online(self) -> list[str]:
        """Returns a list of email addresses of online clients.

        [Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9cac8101-017e-4415-94e2-d30f4dcf49de)

        Returns:
            list[str]: The list of email addresses of online clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            res = api.client.online()
            print(res)
            ```

        """  # pylint: disable=line-too-long
        endpoint = "panel/api/clients/onlines"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Getting online clients")

        response = self._post(url, headers, data)
        online = response.json().get(ApiFields.OBJ)
        return online or []

    def get_traffic_by_id(self, client_uuid: int | str) -> list[Client]:
        """This route is used to retrieve information about a specific client based on their UUID.

        NOTE: At the moment of writing this, the API documentation does not exist for this route.

        Arguments:
            client_uuid (int): The UUID of the client to retrieve.

        Returns:
            list[Client]: The list of clients.

        Examples:

            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            clients = api.client.get_traffic_by_id("239708ef-487e-4945-829d-ad79a0ce067e")
            print(clients)
            ```
        """
        endpoint = "panel/api/clients/list"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client stats for ID: %s", client_uuid)

        response = self._get(url, headers)
        clients_json: list[dict[str, int | bool | str]] = response.json().get(ApiFields.OBJ)
        clients = []
        for client_json in clients_json:
            try:
                client_id = client_json.get("id")
                client_uuid_value = client_json.get("uuid")
                if str(client_uuid) not in {str(client_id), str(client_uuid_value)}:
                    continue
                client = Client.model_validate(client_json)
                clients.append(client)
            except TypeError:
                self.logger.error("Error parsing client: %s", client_json)
                continue
        return clients

    def get_list_paged(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        page: int = 1,
        page_size: int = 25,
        *,
        search: str | None = None,
        statuses: list[str] | None = None,
        protocols: list[str] | None = None,
        inbound_ids: list[int] | None = None,
        groups: list[str] | None = None,
        sort: str | None = None,
        order: str | None = None,
        expiry_from: int | None = None,
        expiry_to: int | None = None,
        usage_from: int | None = None,
        usage_to: int | None = None,
        auto_renew: bool | None = None,
        has_tg_id: bool | None = None,
        has_comment: bool | None = None,
    ) -> ClientPage:
        """This route is used to retrieve one page of clients, filtered and sorted on the panel
        side. The items are compact rows without credentials; use `get_details` for the full
        client. Filters that are left as None are not applied.

        Arguments:
            page (int): The page number, starting from 1. Defaults to 1.
            page_size (int): The number of clients per page, at most 200. Defaults to 25.
            search (str | None): A case-insensitive substring of the email, sub ID, comment, UUID,
                password, auth or Telegram ID.
            statuses (list[str] | None): The status buckets: "online", "active", "deactive",
                "depleted", "expiring".
            protocols (list[str] | None): The inbound protocols, e.g. "vless", "trojan".
            inbound_ids (list[int] | None): The IDs of the inbounds.
            groups (list[str] | None): The group names.
            sort (str | None): The sort key: "enable", "email", "inboundIds", "traffic",
                "remaining", "expiryTime", "createdAt", "updatedAt" or "lastOnline".
            order (str | None): The sort order: "ascend" or "descend".
            expiry_from (int | None): The minimum expiry time in milliseconds.
            expiry_to (int | None): The maximum expiry time in milliseconds.
            usage_from (int | None): The minimum used traffic (up + down) in bytes.
            usage_to (int | None): The maximum used traffic (up + down) in bytes.
            auto_renew (bool | None): Only clients with (True) or without (False) auto-renew.
            has_tg_id (bool | None): Only clients with (True) or without (False) a Telegram ID.
            has_comment (bool | None): Only clients with (True) or without (False) a comment.

        Returns:
            ClientPage: The page of clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            page = api.client.get_list_paged(page=1, page_size=50, statuses=["depleted"])
            print(page.filtered, [item.email for item in page.items])
            ```
        """
        endpoint = "panel/api/clients/list/paged"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        flags = {True: "yes", False: "no"}
        params: dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "filter": ",".join(statuses) if statuses else None,
            "protocol": ",".join(protocols) if protocols else None,
            "inbound": ",".join(str(inbound_id) for inbound_id in inbound_ids)
            if inbound_ids
            else None,
            "group": ",".join(groups) if groups else None,
            "sort": sort,
            "order": order,
            "expiryFrom": expiry_from,
            "expiryTo": expiry_to,
            "usageFrom": usage_from,
            "usageTo": usage_to,
            "autoRenew": None if auto_renew is None else ("on" if auto_renew else "off"),
            "hasTgId": None if has_tg_id is None else flags[has_tg_id],
            "hasComment": None if has_comment is None else flags[has_comment],
        }
        params = {key: value for key, value in params.items() if value is not None}
        self.logger.info("Getting clients page %s (page size %s)", page, page_size)

        response = self._get(url, headers, params=params)
        return ClientPage.model_validate(response.json().get(ApiFields.OBJ) or {})

    def get_details_by_sub_id(self, sub_id: str) -> list[ClientDetails]:
        """This route is used to retrieve the full information about all clients that share the
        given subscription ID, in the same shape as `get_details`.

        Arguments:
            sub_id (str): The subscription ID.

        Returns:
            list[ClientDetails]: The details of the clients, ordered by client ID.

        Raises:
            ValueError: If no client has this subscription ID.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            details = api.client.get_details_by_sub_id("k2v9xq7m1p4r8s3t")
            ```
        """
        endpoint = f"panel/api/clients/get/subId/{quote(sub_id, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client details for sub ID: %s", sub_id)

        response = self._get(url, headers)
        details_json = response.json().get(ApiFields.OBJ) or []
        return [ClientDetails.model_validate(details) for details in details_json]

    def get_details_by_tg_id(self, tg_id: int) -> list[ClientDetails]:
        """This route is used to retrieve the full information about all clients bound to the
        given Telegram user ID, in the same shape as `get_details`.

        Arguments:
            tg_id (int): The Telegram user ID.

        Returns:
            list[ClientDetails]: The details of the clients, empty if there are none.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            details = api.client.get_details_by_tg_id(123456789)
            ```
        """
        endpoint = f"panel/api/clients/get/tgId/{tg_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client details for Telegram ID: %s", tg_id)

        response = self._get(url, headers)
        details_json = response.json().get(ApiFields.OBJ) or []
        return [ClientDetails.model_validate(details) for details in details_json]

    def get_renewal_preview(  # pylint: disable=too-many-arguments
        self,
        expiry_time: int,
        *,
        reset: int = 0,
        reset_day: int = 0,
        reset_weekday: int = 0,
        reset_max: int = 0,
        reset_count: int = 0,
    ) -> ClientRenewalPreview:
        """This route is used to preview the auto-renewal dates of a client without saving
        anything. Only one renewal mode (reset, reset_day or reset_weekday) can be set.

        Arguments:
            expiry_time (int): The current expiry time in milliseconds; 0 means unlimited, a
                negative value is a duration that starts on first use.
            reset (int): The renewal interval in days, 0 disables it. Defaults to 0.
            reset_day (int): The monthly renewal day 1-31, 0 disables it. Defaults to 0.
            reset_weekday (int): The weekly renewal day 1-7 (Monday-Sunday), 0 disables it.
                Defaults to 0.
            reset_max (int): The maximum number of renewals, 0 means unlimited. Defaults to 0.
            reset_count (int): The number of renewals already done. Defaults to 0.

        Returns:
            ClientRenewalPreview: The renewal preview.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            preview = api.client.get_renewal_preview(1893456000000, reset_day=1)
            print(preview.renew_at, preview.next_expiry)
            ```
        """
        endpoint = "panel/api/clients/renewalPreview"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {
            "expiryTime": expiry_time,
            "reset": reset,
            "resetDay": reset_day,
            "resetWeekday": reset_weekday,
            "resetMax": reset_max,
            "resetCount": reset_count,
        }
        self.logger.info("Getting renewal preview for expiry time: %s", expiry_time)

        response = self._post(url, headers, data)
        return ClientRenewalPreview.model_validate(response.json().get(ApiFields.OBJ) or {})

    def get_traffic(self, email: str) -> ClientTraffic | None:
        """This route is used to retrieve the traffic counters of a client identified by email.

        Arguments:
            email (str): The email of the client.

        Returns:
            ClientTraffic | None: The traffic counters if found, otherwise None.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            traffic = api.client.get_traffic("email")
            print(traffic.up, traffic.down)
            ```
        """
        endpoint = f"panel/api/clients/traffic/{quote(email, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client traffic for email: %s", email)

        response = self._get(url, headers)
        traffic_json = response.json().get(ApiFields.OBJ)
        if not traffic_json:
            self.logger.warning("No traffic found for email: %s", email)
            return None
        return ClientTraffic.model_validate(traffic_json)

    def get_sub_links(self, sub_id: str) -> list[str]:
        """This route is used to retrieve the share links (vless://, vmess://, ...) of all
        enabled clients with the given subscription ID, as plain strings.

        Arguments:
            sub_id (str): The subscription ID.

        Returns:
            list[str]: The share links, empty if there are none.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            links = api.client.get_sub_links("k2v9xq7m1p4r8s3t")
            ```
        """
        endpoint = f"panel/api/clients/subLinks/{quote(sub_id, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting subscription links for sub ID: %s", sub_id)

        response = self._get(url, headers)
        return response.json().get(ApiFields.OBJ) or []

    def get_links(self, email: str) -> list[str]:
        """This route is used to retrieve the share links of a client across all inbounds it is
        attached to, one per advertised endpoint.

        Arguments:
            email (str): The email of the client.

        Returns:
            list[str]: The share links, empty if there are none.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            links = api.client.get_links("email")
            ```
        """
        endpoint = f"panel/api/clients/links/{quote(email, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client links for email: %s", email)

        response = self._get(url, headers)
        return response.json().get(ApiFields.OBJ) or []

    def get_happ_link(self, client_id: int) -> str:
        """This route is used to generate a fresh encrypted Happ link (happ://crypt5/...) for the
        subscription of a client. Happ link generation must be enabled in the panel settings.

        Arguments:
            client_id (int): The client record ID (`ClientDetails.client.id`), not the UUID.

        Returns:
            str: The encrypted Happ link.

        Raises:
            ValueError: If the link can not be generated, e.g. the feature is disabled or the
                subscription URL is longer than 8192 bytes (message "happ_source_too_long").

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            details = api.client.get_details("email")
            link = api.client.get_happ_link(details.client.id)
            ```
        """
        endpoint = f"panel/api/clients/happLink/{client_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Generating Happ link for client ID: %s", client_id)

        response = self._post(url, headers, data)
        result = response.json().get(ApiFields.OBJ) or {}
        return result.get("encryptedLink", "")

    def attach(self, email: str, inbound_ids: list[int]) -> None:
        """This route is used to attach an existing client to one or more additional inbounds.

        Arguments:
            email (str): The email of the client.
            inbound_ids (list[int]): The IDs of the inbounds to attach the client to.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.client.attach("email", [7, 9])
            ```
        """
        endpoint = f"panel/api/clients/{quote(email, safe='')}/attach"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"inboundIds": inbound_ids}
        self.logger.info("Attaching client %s to inbounds: %s", email, inbound_ids)

        self._post(url, headers, data)
        self.logger.info("Client attached successfully.")

    def detach(self, email: str, inbound_ids: list[int]) -> None:
        """This route is used to detach a client from one or more inbounds without deleting the
        client. If the call fails for one inbound, the other inbounds are still processed.

        Arguments:
            email (str): The email of the client.
            inbound_ids (list[int]): The IDs of the inbounds to detach the client from.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.client.detach("email", [5])
            ```
        """
        endpoint = f"panel/api/clients/{quote(email, safe='')}/detach"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"inboundIds": inbound_ids}
        self.logger.info("Detaching client %s from inbounds: %s", email, inbound_ids)

        self._post(url, headers, data)
        self.logger.info("Client detached successfully.")

    def set_external_links(self, email: str, links: list[ClientExternalLink]) -> None:
        """This route is used to replace the external links and subscriptions of a client. The
        panel replaces all stored rows with the given list, an empty list removes them all.

        Arguments:
            email (str): The email of the client.
            links (list[ClientExternalLink]): The full list of external links.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            link = py3xui.ClientExternalLink(kind="link", value="vless://...", remark="DE")
            api.client.set_external_links("email", [link])
            ```
        """
        endpoint = f"panel/api/clients/{quote(email, safe='')}/externalLinks"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {
            "externalLinks": [
                link.model_dump(by_alias=True, exclude_defaults=True) for link in links
            ]
        }
        self.logger.info("Setting %s external links for client: %s", len(links), email)

        self._post(url, headers, data)
        self.logger.info("External links set successfully.")

    def delete_orphans(self) -> int:
        """This route is used to delete every client that is not attached to any inbound, with
        its traffic record, IP log, devices and external links. This can not be undone.

        Returns:
            int: The number of deleted clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            deleted = api.client.delete_orphans()
            ```
        """
        endpoint = "panel/api/clients/delOrphans"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Deleting orphan clients")

        response = self._post(url, headers, data)
        result = response.json().get(ApiFields.OBJ) or {}
        return result.get("deleted", 0)

    def export_clients(self) -> list[ClientEntry]:
        """This route is used to export every client with its inbounds and usage counters. The
        result can be passed straight to `import_clients`.

        Returns:
            list[ClientEntry]: The exported clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            entries = api.client.export_clients()
            ```
        """
        endpoint = "panel/api/clients/export"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Exporting clients")

        response = self._get(url, headers)
        entries_json = response.json().get(ApiFields.OBJ) or []
        return [ClientEntry.model_validate(entry) for entry in entries_json]

    def import_clients(self, entries: list[ClientEntry]) -> BulkResult:
        """This route is used to import clients, usually the result of `export_clients`. Entries
        with empty `inbound_ids` are restored as unattached clients. Existing emails are never
        overwritten: they are returned in `skipped`.

        Arguments:
            entries (list[ClientEntry]): The clients to import.

        Returns:
            BulkResult: The number of created clients and the skipped ones.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            entries = api.client.export_clients()
            result = api.client.import_clients(entries)
            print(result.count, result.skipped)
            ```
        """
        endpoint = "panel/api/clients/import"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        items = [entry.model_dump(by_alias=True, exclude_defaults=True) for entry in entries]
        data = {"data": json.dumps(items)}
        self.logger.info("Importing %s clients", len(entries))

        response = self._post(url, headers, data)
        return BulkResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_adjust(  # pylint: disable=too-many-arguments
        self,
        emails: list[str],
        add_days: int = 0,
        add_bytes: int = 0,
        *,
        flow: str | None = None,
        limit_hwid: int | None = None,
        ad_tag: str | None = None,
    ) -> BulkResult:
        """This route is used to shift the expiry and the traffic limit of many clients in one
        call. Clients with an unlimited expiry or traffic limit are skipped for that field. At
        least one adjustment must be given.

        Arguments:
            emails (list[str]): The emails of the clients.
            add_days (int): The days to add to the expiry time, can be negative. Defaults to 0.
            add_bytes (int): The bytes to add to the traffic limit, can be negative. Defaults
                to 0.
            flow (str | None): The XTLS flow to set: "xtls-rprx-vision",
                "xtls-rprx-vision-udp443", or "none" to clear it. None leaves it unchanged.
            limit_hwid (int | None): The limit of devices to set, 0 means unlimited. None leaves
                it unchanged.
            ad_tag (str | None): The MTProto ad tag (32 hex characters) to set, or "none" to clear
                it. None leaves it unchanged.

        Returns:
            BulkResult: The number of adjusted clients and the skipped ones.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            result = api.client.bulk_adjust(["alice", "bob"], add_days=30)
            print(result.count, result.skipped)
            ```
        """
        endpoint = "panel/api/clients/bulkAdjust"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {"emails": emails, "addDays": add_days, "addBytes": add_bytes}
        if flow is not None:
            data["flow"] = flow
        if limit_hwid is not None:
            data["limitHwid"] = limit_hwid
        if ad_tag is not None:
            data["adTag"] = ad_tag
        self.logger.info("Adjusting %s clients", len(emails))

        response = self._post(url, headers, data)
        return BulkResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_enable(self, emails: list[str]) -> BulkResult:
        """This route is used to enable many clients in one call. A client with exhausted traffic
        or a passed expiry is disabled again by the panel on the next traffic check.

        Arguments:
            emails (list[str]): The emails of the clients.

        Returns:
            BulkResult: The number of changed clients and the skipped ones.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            result = api.client.bulk_enable(["alice", "bob"])
            ```
        """
        endpoint = "panel/api/clients/bulkEnable"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails}
        self.logger.info("Enabling %s clients", len(emails))

        response = self._post(url, headers, data)
        return BulkResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_disable(self, emails: list[str]) -> BulkResult:
        """This route is used to disable many clients in one call.

        Arguments:
            emails (list[str]): The emails of the clients.

        Returns:
            BulkResult: The number of changed clients and the skipped ones.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            result = api.client.bulk_disable(["alice", "bob"])
            ```
        """
        endpoint = "panel/api/clients/bulkDisable"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails}
        self.logger.info("Disabling %s clients", len(emails))

        response = self._post(url, headers, data)
        return BulkResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_delete(self, emails: list[str], keep_traffic: bool = False) -> BulkResult:
        """This route is used to delete many clients in one call.

        Arguments:
            emails (list[str]): The emails of the clients.
            keep_traffic (bool): Whether to keep the traffic records of the clients. Defaults to
                False.

        Returns:
            BulkResult: The number of deleted clients and the skipped ones.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            result = api.client.bulk_delete(["alice", "bob"])
            ```
        """
        endpoint = "panel/api/clients/bulkDel"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails, "keepTraffic": keep_traffic}
        self.logger.info("Deleting %s clients", len(emails))

        response = self._post(url, headers, data)
        return BulkResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_add(self, entries: list[ClientEntry]) -> BulkResult:
        """This route is used to create many clients in one call, each on its own set of inbounds.
        Clients that can not be created, e.g. with a duplicate email, are returned in `skipped`.

        Arguments:
            entries (list[ClientEntry]): The clients to create with their inbound IDs.

        Returns:
            BulkResult: The number of created clients and the skipped ones.

        Examples:
            ```python
            import uuid
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            client = py3xui.Client(id=str(uuid.uuid4()), email="test", enable=True)
            entry = py3xui.ClientEntry(client=client, inbound_ids=[7])
            result = api.client.bulk_add([entry])
            ```
        """
        endpoint = "panel/api/clients/bulkCreate"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        # This endpoint takes a JSON array, not an object.
        data = [entry.model_dump(by_alias=True, exclude_defaults=True) for entry in entries]
        self.logger.info("Adding %s clients", len(entries))

        response = self._post(url, headers, cast(Any, data))
        return BulkResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_attach(self, emails: list[str], inbound_ids: list[int]) -> BulkAttachResult:
        """This route is used to attach many existing clients to many inbounds in one call.

        Arguments:
            emails (list[str]): The emails of the clients.
            inbound_ids (list[int]): The IDs of the inbounds to attach every client to.

        Returns:
            BulkAttachResult: The attached and skipped emails and the errors.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            result = api.client.bulk_attach(["alice", "bob"], [7, 9])
            print(result.attached, result.skipped, result.errors)
            ```
        """
        endpoint = "panel/api/clients/bulkAttach"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails, "inboundIds": inbound_ids}
        self.logger.info("Attaching %s clients to inbounds: %s", len(emails), inbound_ids)

        response = self._post(url, headers, data)
        return BulkAttachResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_detach(self, emails: list[str], inbound_ids: list[int]) -> BulkDetachResult:
        """This route is used to detach many existing clients from many inbounds in one call. The
        clients are kept even if they end up without inbounds.

        Arguments:
            emails (list[str]): The emails of the clients.
            inbound_ids (list[int]): The IDs of the inbounds to detach the clients from.

        Returns:
            BulkDetachResult: The detached and skipped emails and the errors.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            result = api.client.bulk_detach(["alice", "bob"], [7, 9])
            print(result.detached, result.skipped, result.errors)
            ```
        """
        endpoint = "panel/api/clients/bulkDetach"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails, "inboundIds": inbound_ids}
        self.logger.info("Detaching %s clients from inbounds: %s", len(emails), inbound_ids)

        response = self._post(url, headers, data)
        return BulkDetachResult.model_validate(response.json().get(ApiFields.OBJ) or {})

    def bulk_reset_stats(self, emails: list[str]) -> int:
        """This route is used to reset the traffic counters of many clients in one call.

        Arguments:
            emails (list[str]): The emails of the clients.

        Returns:
            int: The number of clients that were reset.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            affected = api.client.bulk_reset_stats(["alice", "bob"])
            ```
        """
        endpoint = "panel/api/clients/bulkResetTraffic"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails}
        self.logger.info("Resetting stats of %s clients", len(emails))

        response = self._post(url, headers, data)
        result = response.json().get(ApiFields.OBJ) or {}
        return result.get("affected", 0)

    def get_groups(self) -> list[ClientGroup]:
        """This route is used to retrieve all client groups with their member counts and traffic,
        including empty groups.

        Returns:
            list[ClientGroup]: The client groups, sorted by name.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            groups = api.client.get_groups()
            ```
        """
        endpoint = "panel/api/clients/groups"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting client groups")

        response = self._get(url, headers)
        groups_json = response.json().get(ApiFields.OBJ) or []
        return [ClientGroup.model_validate(group) for group in groups_json]

    def get_group_emails(self, name: str) -> list[str]:
        """This route is used to retrieve the emails of the clients that belong to a group.

        Arguments:
            name (str): The name of the group.

        Returns:
            list[str]: The emails of the clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            emails = api.client.get_group_emails("customer-a")
            ```
        """
        endpoint = f"panel/api/clients/groups/{quote(name, safe='')}/emails"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting emails of client group: %s", name)

        response = self._get(url, headers)
        return response.json().get(ApiFields.OBJ) or []

    def add_group(self, name: str) -> None:
        """This route is used to create a new empty client group.

        Arguments:
            name (str): The name of the group.

        Raises:
            ValueError: If a group with this name already exists.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.client.add_group("customer-a")
            ```
        """
        endpoint = "panel/api/clients/groups/create"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"name": name}
        self.logger.info("Adding client group: %s", name)

        self._post(url, headers, data)
        self.logger.info("Client group added successfully.")

    def rename_group(self, old_name: str, new_name: str) -> int:
        """This route is used to rename a client group, the new name is applied to all its
        clients.

        Arguments:
            old_name (str): The current name of the group.
            new_name (str): The new name of the group.

        Returns:
            int: The number of clients whose group was changed.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            affected = api.client.rename_group("customer-a", "tier-1")
            ```
        """
        endpoint = "panel/api/clients/groups/rename"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"oldName": old_name, "newName": new_name}
        self.logger.info("Renaming client group %s to %s", old_name, new_name)

        response = self._post(url, headers, data)
        result = response.json().get(ApiFields.OBJ) or {}
        return result.get("affected", 0)

    def delete_group(self, name: str) -> int:
        """This route is used to delete a client group. The clients are not deleted, only their
        group is cleared.

        Arguments:
            name (str): The name of the group.

        Returns:
            int: The number of clients whose group was cleared.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            affected = api.client.delete_group("customer-a")
            ```
        """
        endpoint = "panel/api/clients/groups/delete"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"name": name}
        self.logger.info("Deleting client group: %s", name)

        response = self._post(url, headers, data)
        result = response.json().get(ApiFields.OBJ) or {}
        return result.get("affected", 0)

    def reset_group_stats(self, name: str) -> None:
        """This route is used to reset the traffic counter of a client group. The counters of the
        clients themselves are not changed.

        Arguments:
            name (str): The name of the group.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.client.reset_group_stats("customer-a")
            ```
        """
        endpoint = "panel/api/clients/groups/resetTraffic"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"name": name}
        self.logger.info("Resetting stats of client group: %s", name)

        self._post(url, headers, data)
        self.logger.info("Client group stats reset successfully.")

    def bulk_add_to_group(self, group: str, emails: list[str]) -> int:
        """This route is used to add many clients to a group in one call. The group is created if
        it does not exist.

        Arguments:
            group (str): The name of the group, must not be blank.
            emails (list[str]): The emails of the clients.

        Returns:
            int: The number of affected clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            affected = api.client.bulk_add_to_group("customer-a", ["alice", "bob"])
            ```
        """
        endpoint = "panel/api/clients/groups/bulkAdd"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails, "group": group}
        self.logger.info("Adding %s clients to group: %s", len(emails), group)

        response = self._post(url, headers, data)
        result = response.json().get(ApiFields.OBJ) or {}
        return result.get("affected", 0)

    def bulk_remove_from_group(self, emails: list[str]) -> int:
        """This route is used to clear the group of many clients in one call. The clients are
        kept.

        Arguments:
            emails (list[str]): The emails of the clients.

        Returns:
            int: The number of affected clients.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            affected = api.client.bulk_remove_from_group(["alice", "bob"])
            ```
        """
        endpoint = "panel/api/clients/groups/bulkRemove"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"emails": emails}
        self.logger.info("Removing %s clients from their group", len(emails))

        response = self._post(url, headers, data)
        result = response.json().get(ApiFields.OBJ) or {}
        return result.get("affected", 0)

    def update_traffic(self, email: str, up: int, down: int) -> None:
        """This route is used to set the traffic counters of a client. The given values replace
        the stored ones, they are not added to them.

        Arguments:
            email (str): The email of the client.
            up (int): The new uploaded traffic in bytes.
            down (int): The new downloaded traffic in bytes.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.client.update_traffic("email", 1073741824, 5368709120)
            ```
        """
        endpoint = f"panel/api/clients/updateTraffic/{quote(email, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {"upload": up, "download": down}
        self.logger.info("Updating client traffic for email: %s", email)

        self._post(url, headers, data)
        self.logger.info("Client traffic updated successfully.")

    def get_hwids(self, email: str) -> list[ClientHwid]:
        """This route is used to retrieve the devices (HWIDs) registered for a client.

        Arguments:
            email (str): The email of the client.

        Returns:
            list[ClientHwid]: The devices, most recently seen first.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            devices = api.client.get_hwids("email")
            ```
        """
        endpoint = f"panel/api/clients/hwids/{quote(email, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Getting devices of client: %s", email)

        response = self._post(url, headers, data)
        hwids_json = response.json().get(ApiFields.OBJ) or []
        return [ClientHwid.model_validate(hwid) for hwid in hwids_json]

    def delete_hwids(self, email: str) -> None:
        """This route is used to delete all devices (HWIDs) registered for a client, so new
        devices can register again.

        Arguments:
            email (str): The email of the client.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.client.delete_hwids("email")
            ```
        """
        endpoint = f"panel/api/clients/hwids/{quote(email, safe='')}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Deleting devices of client: %s", email)

        self._delete(url, headers)
        self.logger.info("Client devices deleted successfully.")

    def delete_hwid(self, email: str, hwid_id: int) -> None:
        """This route is used to delete one device (HWID) of a client, freeing one slot under the
        device limit.

        Arguments:
            email (str): The email of the client.
            hwid_id (int): The ID of the device, `ClientHwid.id`.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            api.client.delete_hwid("email", 1)
            ```
        """
        endpoint = f"panel/api/clients/hwids/{quote(email, safe='')}/{hwid_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Deleting device %s of client: %s", hwid_id, email)

        self._delete(url, headers)
        self.logger.info("Client device deleted successfully.")

    def online_by_guid(self) -> dict[str, list[str]]:
        """This route is used to retrieve the emails of online clients, grouped by the panel GUID
        of the node that hosts them.

        Returns:
            dict[str, list[str]]: The online emails by panel GUID.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            online = api.client.online_by_guid()
            ```
        """
        endpoint = "panel/api/clients/onlinesByGuid"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Getting online clients by panel GUID")

        response = self._post(url, headers, data)
        return response.json().get(ApiFields.OBJ) or {}

    def get_ips_by_guid(self) -> dict[str, dict[str, list[ClientIpEntry]]]:
        """This route is used to retrieve the recent source IPs of clients, grouped by the panel
        GUID of the node that observed them and by client email.

        Returns:
            dict[str, dict[str, list[ClientIpEntry]]]: The IPs by panel GUID and email.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            ips = api.client.get_ips_by_guid()
            ```
        """
        endpoint = "panel/api/clients/clientIpsByGuid"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Getting client IPs by panel GUID")

        response = self._post(url, headers, data)
        ips_json = response.json().get(ApiFields.OBJ) or {}
        return {
            guid: {
                email: [ClientIpEntry.model_validate(entry) for entry in entries or []]
                for email, entries in per_email.items()
            }
            for guid, per_email in ips_json.items()
        }

    def get_active_inbounds(self) -> dict[str, list[str]]:
        """This route is used to retrieve the tags of the inbounds that recently carried traffic,
        grouped by the panel GUID of the node that hosts them. Nodes that do not report this are
        absent.

        Returns:
            dict[str, list[str]]: The inbound tags by panel GUID.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            active = api.client.get_active_inbounds()
            ```
        """
        endpoint = "panel/api/clients/activeInbounds"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Getting active inbounds by panel GUID")

        response = self._post(url, headers, data)
        return response.json().get(ApiFields.OBJ) or {}

    def get_last_online(self) -> dict[str, int]:
        """This route is used to retrieve the last time each client was online.

        Returns:
            dict[str, int]: The last online time in milliseconds by client email, 0 means never.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()
            last_online = api.client.get_last_online()
            ```
        """
        endpoint = "panel/api/clients/lastOnline"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Getting last online time of clients")

        response = self._post(url, headers, data)
        return response.json().get(ApiFields.OBJ) or {}

    def _resolve_client_email(self, inbound_id: int, client_identifier: str) -> str:
        """Resolves legacy client IDs/UUIDs to client email for delete endpoint."""
        if "@" in client_identifier:
            return client_identifier

        endpoint = "panel/api/clients/list"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        response = self._get(url, headers)
        clients_json = response.json().get(ApiFields.OBJ) or []

        for client_json in clients_json:
            client_id = client_json.get("id")
            client_uuid = client_json.get("uuid")
            if str(client_identifier) in {str(client_id), str(client_uuid)}:
                email = client_json.get("email")
                if isinstance(email, str) and email:
                    return email

        raise ValueError(
            "Cannot resolve client email from identifier "
            f"'{client_identifier}' in inbound {inbound_id}."
        )
