"""This module contains the AsyncXrayApi class for handling the Xray settings in the XUI API
asynchronously."""

# pylint: disable=R0801, too-many-lines
from typing import Any

from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_base import AsyncBaseApi
from py3xui.xray.diagnostics import (
    BalancerStatus,
    OutboundTestResult,
    RouteTestResult,
)
from py3xui.xray.geodata import (
    GeoCategoryPage,
    GeodataTokenIssue,
    GeoEntryPage,
    GeoFile,
)
from py3xui.xray.outbound_sub import OutboundSub
from py3xui.xray.pia import PiaAccount, PiaCountry, PiaKey, PiaServers
from py3xui.xray.xray import OutboundTraffic, XraySettings, parse_json_obj


class AsyncXrayApi(AsyncBaseApi):  # pylint: disable=too-many-public-methods
    """This class provides methods to interact with the Xray settings in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_settings: Retrieves the Xray configuration template and the related data.
        get_default_config: Retrieves the default Xray configuration.
        get_outbounds_traffic: Retrieves the traffic statistics of the outbounds.
        get_result: Retrieves the latest output of the Xray process.
        update: Updates the Xray configuration template and the outbound test URL.
        reset_outbound_stats: Resets the traffic statistics of an outbound.
        warp_get_data: Retrieves the stored Warp credentials.
        warp_delete: Deletes the stored Warp credentials.
        warp_get_config: Retrieves the Warp device configuration.
        warp_register: Registers a new Warp device.
        warp_register_masque: Registers a new Warp device with a MASQUE key.
        warp_change_ip: Changes the Warp IP address.
        warp_set_license: Applies a Warp+ license key.
        warp_set_interval: Sets the interval of the Warp IP rotation.
        nord_get_countries: Retrieves the NordVPN countries.
        nord_get_servers: Retrieves the NordVPN servers of a country.
        nord_register: Gets the NordLynx key with an access token.
        nord_set_key: Stores a NordLynx private key.
        nord_get_data: Retrieves the stored NordVPN credentials.
        nord_delete: Deletes the stored NordVPN credentials.
        pia_get_countries: Retrieves the PIA countries.
        pia_get_servers: Retrieves the PIA regions and servers of a country.
        pia_register: Signs in to a PIA account.
        pia_get_data: Retrieves the signed in PIA account.
        pia_delete: Deletes the stored PIA account.
        pia_add_key: Registers a WireGuard key on a PIA server.
        test_outbound: Tests an outbound configuration.
        test_outbounds: Tests a batch of outbound configurations.
        get_balancer_status: Retrieves the live state of balancers.
        set_balancer_override: Forces a balancer to an outbound or clears the override.
        test_route: Asks the core which outbound it would pick for a connection.
        get_geodata_files: Retrieves the geo databases of the Xray asset folder.
        get_geodata_categories: Retrieves one page of the categories of a geo database.
        get_geodata_entries: Retrieves one page of the entries of a category.
        validate_geodata: Reports the routing tokens which do not resolve.
        get_outbound_subs: Retrieves the outbound subscriptions.
        add_outbound_sub: Adds a new outbound subscription.
        update_outbound_sub: Updates an outbound subscription.
        delete_outbound_sub: Deletes an outbound subscription.
        refresh_outbound_sub: Fetches an outbound subscription right away.
        move_outbound_sub: Moves an outbound subscription one step in the order.
        parse_outbound_sub: Previews a subscription URL without saving it.

    Examples:
        ```python
        import py3xui

        api = py3xui.AsyncApi.from_env()
        await api.login()

        settings: py3xui.XraySettings = await api.xray.get_settings()
        ```
    """

    async def get_settings(self) -> XraySettings:
        """Retrieves the Xray configuration template and the data the panel returns along
        with it. The panel sends the whole payload as a JSON string, it's parsed here.

        Returns:
            XraySettings: The Xray configuration template and the related data.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            settings: py3xui.XraySettings = await api.xray.get_settings()
            print(settings.xray_setting["outbounds"])
            ```
        """
        endpoint = "panel/api/xray/"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray settings...")

        response = await self._post_form(url, headers, {})
        return XraySettings.model_validate(
            parse_json_obj(response.json().get(ApiFields.OBJ))
        )

    async def get_default_config(self) -> dict:
        """Retrieves the default Xray configuration shipped with the panel.

        Returns:
            dict: The default Xray configuration.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            config: dict = await api.xray.get_default_config()
            ```
        """
        endpoint = "panel/api/xray/getDefaultJsonConfig"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting default Xray config...")

        response = await self._get(url, headers)
        return response.json().get(ApiFields.OBJ)

    async def get_outbounds_traffic(self) -> list[OutboundTraffic]:
        """Retrieves the traffic statistics of the outbounds.

        Returns:
            list[OutboundTraffic]: The traffic statistics of the outbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            traffic: list[py3xui.OutboundTraffic] = await api.xray.get_outbounds_traffic()
            ```
        """
        endpoint = "panel/api/xray/getOutboundsTraffic"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting outbounds traffic...")

        response = await self._get(url, headers)
        traffic_json = response.json().get(ApiFields.OBJ) or []
        return [OutboundTraffic.model_validate(data) for data in traffic_json]

    async def get_result(self) -> str:
        """Retrieves the latest output of the Xray process. It's useful to check for startup
        errors.

        Returns:
            str: The output of the Xray process.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result: str = await api.xray.get_result()
            ```
        """
        endpoint = "panel/api/xray/getXrayResult"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray result...")

        response = await self._get(url, headers)
        return response.json().get(ApiFields.OBJ) or ""

    async def update(self, config: str, outbound_test_url: str | None = None) -> None:
        """Updates the Xray configuration template and the outbound test URL. A running Xray
        core applies the changes right away.

        Note:
            The panel replaces the outbound test URL on every update: when it's not provided,
            the panel resets it to the default one. To keep the current URL, pass it from
            `get_settings()`.

        Arguments:
            config (str): The Xray configuration template as a JSON string.
            outbound_test_url (str | None): The URL used to test the outbounds.

        Examples:
            ```python
            import json
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            settings = await api.xray.get_settings()
            await api.xray.update(json.dumps(settings.xray_setting), settings.outbound_test_url)
            ```
        """
        endpoint = "panel/api/xray/update"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"xraySetting": config, "outboundTestUrl": outbound_test_url}
        self.logger.info("Updating Xray settings...")

        await self._post_form(url, headers, data)
        self.logger.info("Xray settings updated successfully.")

    async def reset_outbound_stats(self, tag: str) -> None:
        """Resets the traffic statistics of an outbound.

        Arguments:
            tag (str): The tag of the outbound. Use "-alltags-" to reset all the outbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.reset_outbound_stats("direct")
            ```
        """
        endpoint = "panel/api/xray/resetOutboundsTraffic"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"tag": tag}
        self.logger.info("Resetting traffic of outbound: %s", tag)

        await self._post_form(url, headers, data)
        self.logger.info("Outbound traffic reset successfully.")

    async def warp_get_data(self) -> dict[str, Any]:
        """Retrieves the stored Warp credentials. The panel returns them as a JSON string, it's
        parsed here.

        Returns:
            dict[str, Any]: The stored credentials, empty if Warp is not registered.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            data = await api.xray.warp_get_data()
            ```
        """
        endpoint = "panel/api/xray/warp/data"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Warp data...")

        response = await self._post_form(url, headers, {})
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def warp_delete(self) -> None:
        """Deletes the stored Warp credentials.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.warp_delete()
            ```
        """
        endpoint = "panel/api/xray/warp/del"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Deleting Warp data...")

        await self._post_form(url, headers, {})

    async def warp_get_config(self) -> dict[str, Any]:
        """Retrieves the Warp device configuration from Cloudflare. The panel returns it as a JSON
        string, it's parsed here.

        Returns:
            dict[str, Any]: The configuration of the registered device.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            config = await api.xray.warp_get_config()
            ```
        """
        endpoint = "panel/api/xray/warp/config"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Warp config...")

        response = await self._post_form(url, headers, {})
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def warp_register(self, private_key: str, public_key: str) -> dict[str, Any]:
        """Registers a new Warp device with the provided WireGuard keys. The panel returns the
        result as a JSON string, it's parsed here.

        Arguments:
            private_key (str): The WireGuard private key.
            public_key (str): The WireGuard public key.

        Returns:
            dict[str, Any]: The stored credentials ("data") and the device configuration ("config").

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result = await api.xray.warp_register("private-key", "public-key")
            ```
        """
        endpoint = "panel/api/xray/warp/reg"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"privateKey": private_key, "publicKey": public_key}
        self.logger.info("Registering Warp...")

        response = await self._post_form(url, headers, data)
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def warp_register_masque(self) -> dict[str, Any]:
        """Registers a new Warp device with a MASQUE key. The panel returns the result as a JSON
        string, it's parsed here.

        Returns:
            dict[str, Any]: The "privateKey", "publicKey", "address" and "endpoint" values.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result = await api.xray.warp_register_masque()
            ```
        """
        endpoint = "panel/api/xray/warp/regMasque"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Registering Warp MASQUE...")

        response = await self._post_form(url, headers, {})
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def warp_change_ip(self) -> dict[str, Any]:
        """Registers a new Warp device to get a new IP address and applies it to the Xray
        configuration. The panel returns the result as a JSON string, it's parsed here.

        Returns:
            dict[str, Any]: The credentials ("data"), the device configuration ("config") and
                an optional "warning".

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result = await api.xray.warp_change_ip()
            ```
        """
        endpoint = "panel/api/xray/warp/changeIp"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Changing Warp IP...")

        response = await self._post_form(url, headers, {})
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def warp_set_license(self, license_key: str) -> dict[str, Any]:
        """Applies a Warp+ license key. The panel returns the result as a JSON string, it's parsed
        here.

        Arguments:
            license_key (str): The license key.

        Returns:
            dict[str, Any]: The updated credentials.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            data = await api.xray.warp_set_license("license-key")
            ```
        """
        endpoint = "panel/api/xray/warp/license"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"license": license_key}
        self.logger.info("Setting Warp license...")

        response = await self._post_form(url, headers, data)
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def warp_set_interval(self, interval: int) -> None:
        """Sets the interval of the automatic Warp IP rotation.

        Arguments:
            interval (int): The number of hours between the rotations, 0 disables the rotation.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.warp_set_interval(24)
            ```
        """
        endpoint = "panel/api/xray/warp/interval"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"interval": interval}
        self.logger.info("Setting Warp update interval: %s", interval)

        await self._post_form(url, headers, data)

    async def nord_get_countries(self) -> list[dict[str, Any]]:
        """Retrieves the NordVPN countries with WireGuard servers. The panel returns them as a JSON
        string, it's parsed here.

        Returns:
            list[dict[str, Any]]: The countries as returned by the NordVPN API.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            countries = await api.xray.nord_get_countries()
            ```
        """
        endpoint = "panel/api/xray/nord/countries"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting NordVPN countries...")

        response = await self._post_form(url, headers, {})
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or []

    async def nord_get_servers(self, country_id: int) -> dict[str, Any]:
        """Retrieves the NordVPN WireGuard servers of a country. The panel returns them as a JSON
        string, it's parsed here.

        Arguments:
            country_id (int): The ID of the country.

        Returns:
            dict[str, Any]: The servers and locations as returned by the NordVPN API.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            servers = await api.xray.nord_get_servers(1)
            ```
        """
        endpoint = "panel/api/xray/nord/servers"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"countryId": country_id}
        self.logger.info("Getting NordVPN servers of country: %s", country_id)

        response = await self._post_form(url, headers, data)
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def nord_register(self, token: str) -> dict[str, Any]:
        """Gets the NordLynx private key with a NordVPN access token and stores it. The panel
        returns the result as a JSON string, it's parsed here.

        Arguments:
            token (str): The NordVPN access token.

        Returns:
            dict[str, Any]: The "private_key" and "token" values.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            data = await api.xray.nord_register("access-token")
            ```
        """
        endpoint = "panel/api/xray/nord/reg"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"token": token}
        self.logger.info("Registering NordVPN...")

        response = await self._post_form(url, headers, data)
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def nord_set_key(self, key: str) -> dict[str, Any]:
        """Stores a NordLynx private key. The panel returns the result as a JSON string, it's
        parsed here.

        Arguments:
            key (str): The NordLynx private key.

        Returns:
            dict[str, Any]: The "private_key" and "token" values.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            data = await api.xray.nord_set_key("private-key")
            ```
        """
        endpoint = "panel/api/xray/nord/setKey"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"key": key}
        self.logger.info("Setting NordVPN key...")

        response = await self._post_form(url, headers, data)
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def nord_get_data(self) -> dict[str, Any]:
        """Retrieves the stored NordVPN credentials. The panel returns them as a JSON string, it's
        parsed here.

        Returns:
            dict[str, Any]: The stored credentials, empty if NordVPN is not registered.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            data = await api.xray.nord_get_data()
            ```
        """
        endpoint = "panel/api/xray/nord/data"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting NordVPN data...")

        response = await self._post_form(url, headers, {})
        return parse_json_obj(response.json().get(ApiFields.OBJ)) or {}

    async def nord_delete(self) -> None:
        """Deletes the stored NordVPN credentials.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.nord_delete()
            ```
        """
        endpoint = "panel/api/xray/nord/del"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Deleting NordVPN data...")

        await self._post_form(url, headers, {})

    async def pia_get_countries(self) -> list[PiaCountry]:
        """Retrieves the countries with PIA WireGuard servers.

        Returns:
            list[PiaCountry]: The countries.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            countries: list[py3xui.PiaCountry] = await api.xray.pia_get_countries()
            ```
        """
        endpoint = "panel/api/xray/pia/countries"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting PIA countries...")

        response = await self._post_form(url, headers, {})
        countries_json = response.json().get(ApiFields.OBJ) or []
        return [PiaCountry.model_validate(data) for data in countries_json]

    async def pia_get_servers(self, country_code: str) -> PiaServers:
        """Retrieves the PIA regions and WireGuard servers of a country.

        Arguments:
            country_code (str): The country code.

        Returns:
            PiaServers: The regions and servers of the country.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            servers: py3xui.PiaServers = await api.xray.pia_get_servers("US")
            ```
        """
        endpoint = "panel/api/xray/pia/servers"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"countryCode": country_code}
        self.logger.info("Getting PIA servers of country: %s", country_code)

        response = await self._post_form(url, headers, data)
        return PiaServers.model_validate(response.json().get(ApiFields.OBJ))

    async def pia_register(self, username: str, password: str) -> PiaAccount:
        """Signs in to a PIA account. The panel stores the token, not the password.

        Arguments:
            username (str): The PIA username.
            password (str): The PIA password.

        Returns:
            PiaAccount: The signed in account.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            account: py3xui.PiaAccount = await api.xray.pia_register("username", "password")
            ```
        """
        endpoint = "panel/api/xray/pia/reg"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"username": username, "password": password}
        self.logger.info("Signing in to PIA...")

        response = await self._post_form(url, headers, data)
        return PiaAccount.model_validate(response.json().get(ApiFields.OBJ))

    async def pia_get_data(self) -> PiaAccount | None:
        """Retrieves the signed in PIA account.

        Returns:
            PiaAccount | None: The signed in account or None if there is no account.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            account: py3xui.PiaAccount | None = await api.xray.pia_get_data()
            ```
        """
        endpoint = "panel/api/xray/pia/data"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting PIA data...")

        response = await self._post_form(url, headers, {})
        account_json = response.json().get(ApiFields.OBJ)
        return PiaAccount.model_validate(account_json) if account_json else None

    async def pia_delete(self) -> None:
        """Deletes the stored PIA account.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.pia_delete()
            ```
        """
        endpoint = "panel/api/xray/pia/del"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Deleting PIA data...")

        await self._post_form(url, headers, {})

    async def pia_add_key(self, hostname: str) -> PiaKey:
        """Generates a WireGuard key and registers it on a PIA server.

        Arguments:
            hostname (str): The hostname of the server.

        Returns:
            PiaKey: The generated key and the connection details.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            key: py3xui.PiaKey = await api.xray.pia_add_key("server.example.com")
            ```
        """
        endpoint = "panel/api/xray/pia/addKey"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"hostname": hostname}
        self.logger.info("Adding PIA key on server: %s", hostname)

        response = await self._post_form(url, headers, data)
        return PiaKey.model_validate(response.json().get(ApiFields.OBJ))

    async def test_outbound(
        self, outbound: str, all_outbounds: str | None = None, mode: str | None = None
    ) -> OutboundTestResult:
        """Tests an outbound configuration.

        Arguments:
            outbound (str): The outbound configuration as a JSON string.
            all_outbounds (str | None): All the outbounds as a JSON array string, used to
                resolve the dialerProxy dependencies.
            mode (str | None): "tcp" for a dial-only probe, "real" for the full request delay,
                by default a full HTTP probe is used.

        Returns:
            OutboundTestResult: The result of the test.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result: py3xui.OutboundTestResult = await api.xray.test_outbound(
                '{"tag": "direct", "protocol": "freedom"}', mode="tcp"
            )
            ```
        """
        endpoint = "panel/api/xray/testOutbound"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"outbound": outbound, "allOutbounds": all_outbounds, "mode": mode}
        self.logger.info("Testing outbound...")

        response = await self._post_form(url, headers, data)
        return OutboundTestResult.model_validate(response.json().get(ApiFields.OBJ))

    async def test_outbounds(
        self, outbounds: str, all_outbounds: str | None = None, mode: str | None = None
    ) -> list[OutboundTestResult]:
        """Tests a batch of outbound configurations (the panel accepts up to 50).

        Arguments:
            outbounds (str): The outbound configurations as a JSON array string.
            all_outbounds (str | None): All the outbounds as a JSON array string, used to
                resolve the dialerProxy dependencies.
            mode (str | None): "tcp" for dial-only probes, "real" for the full request delay,
                by default full HTTP probes are used.

        Returns:
            list[OutboundTestResult]: The results in the order of the input.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            results: list[py3xui.OutboundTestResult] = await api.xray.test_outbounds(
                '[{"tag": "direct", "protocol": "freedom"}]'
            )
            ```
        """
        endpoint = "panel/api/xray/testOutbounds"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        form = {"outbounds": outbounds, "allOutbounds": all_outbounds, "mode": mode}
        self.logger.info("Testing outbounds...")

        response = await self._post_form(url, headers, form)
        results_json = response.json().get(ApiFields.OBJ) or []
        return [OutboundTestResult.model_validate(data) for data in results_json]

    async def get_balancer_status(self, tags: list[str]) -> dict[str, BalancerStatus]:
        """Retrieves the live state of the balancers in the running core.

        Arguments:
            tags (list[str]): The tags of the balancers.

        Returns:
            dict[str, BalancerStatus]: The state of the balancers by their tags.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            statuses = await api.xray.get_balancer_status(["balancer-1"])
            ```
        """
        endpoint = "panel/api/xray/balancerStatus"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"tags": ",".join(tags)}
        self.logger.info("Getting status of balancers: %s", tags)

        response = await self._post_form(url, headers, data)
        statuses_json = response.json().get(ApiFields.OBJ) or {}
        return {
            tag: BalancerStatus.model_validate(data)
            for tag, data in statuses_json.items()
        }

    async def set_balancer_override(self, balancer_tag: str, target: str = "") -> None:
        """Forces a balancer in the running core to always pick one outbound.

        Arguments:
            balancer_tag (str): The tag of the balancer.
            target (str): The tag of the outbound, an empty value clears the override.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.set_balancer_override("balancer-1", "direct")
            ```
        """
        endpoint = "panel/api/xray/balancerOverride"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"tag": balancer_tag, "target": target}
        self.logger.info("Setting override of balancer %s to: %s", balancer_tag, target)

        await self._post_form(url, headers, data)

    async def test_route(  # pylint: disable=R0913, R0917
        self,
        domain: str | None = None,
        ip: str | None = None,
        port: int | None = None,
        network: str | None = None,
        inbound_tag: str | None = None,
        protocol: str | None = None,
        email: str | None = None,
    ) -> RouteTestResult:
        """Asks the running core which outbound its router would pick for a synthetic
        connection. No traffic is sent. Either domain or ip is required.

        Arguments:
            domain (str | None): The target domain.
            ip (str | None): The target IP address.
            port (int | None): The target port.
            network (str | None): "tcp" (default) or "udp".
            inbound_tag (str | None): Simulates the arrival on this inbound.
            protocol (str | None): The sniffed protocol (http, tls, bittorrent etc.).
            email (str | None): The user for the user-based rules.

        Returns:
            RouteTestResult: The routing decision.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result: py3xui.RouteTestResult = await api.xray.test_route(
                domain="example.com", port=443
            )
            ```
        """
        endpoint = "panel/api/xray/routeTest"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {
            "domain": domain,
            "ip": ip,
            "port": port,
            "network": network,
            "inboundTag": inbound_tag,
            "protocol": protocol,
            "email": email,
        }
        self.logger.info("Testing route...")

        response = await self._post_form(url, headers, data)
        return RouteTestResult.model_validate(response.json().get(ApiFields.OBJ))

    async def get_geodata_files(self) -> list[GeoFile]:
        """Retrieves the geo databases of the Xray asset folder. A database which failed to
        parse is listed too, with the reason in the error field.

        Returns:
            list[GeoFile]: The geo databases.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            files: list[py3xui.GeoFile] = await api.xray.get_geodata_files()
            ```
        """
        endpoint = "panel/api/xray/geodata/files"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting geodata files...")

        response = await self._get(url, headers)
        files_json = response.json().get(ApiFields.OBJ) or []
        return [GeoFile.model_validate(data) for data in files_json]

    async def get_geodata_categories(
        self,
        file: str,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> GeoCategoryPage:
        """Retrieves one page of the categories of a geo database.

        Arguments:
            file (str): The name of the database file.
            query (str | None): The filter of the categories.
            offset (int | None): The number of the categories to skip.
            limit (int | None): The size of the page.

        Returns:
            GeoCategoryPage: The page of the categories and the unpaged total.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            page: py3xui.GeoCategoryPage = await api.xray.get_geodata_categories(
                "geosite.dat", limit=10
            )
            ```
        """
        endpoint = "panel/api/xray/geodata/categories"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        params = {
            key: value
            for key, value in {
                "file": file,
                "q": query,
                "offset": offset,
                "limit": limit,
            }.items()
            if value is not None
        }
        self.logger.info("Getting categories of geodata file: %s", file)

        response = await self._get(url, headers, params=params)
        return GeoCategoryPage.model_validate(response.json().get(ApiFields.OBJ))

    async def get_geodata_entries(  # pylint: disable=R0913, R0917
        self,
        file: str,
        code: str,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> GeoEntryPage:
        """Retrieves one page of the entries of a category: domain rules for geosite databases,
        CIDRs for geoip ones.

        Arguments:
            file (str): The name of the database file.
            code (str): The code of the category.
            query (str | None): The filter of the entries.
            offset (int | None): The number of the entries to skip.
            limit (int | None): The size of the page.

        Returns:
            GeoEntryPage: The page of the entries and the unpaged total.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            page: py3xui.GeoEntryPage = await api.xray.get_geodata_entries("geosite.dat", "google")
            ```
        """
        endpoint = "panel/api/xray/geodata/entries"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        params = {
            key: value
            for key, value in {
                "file": file,
                "code": code,
                "q": query,
                "offset": offset,
                "limit": limit,
            }.items()
            if value is not None
        }
        self.logger.info("Getting entries of geodata category %s in file: %s", code, file)

        response = await self._get(url, headers, params=params)
        return GeoEntryPage.model_validate(response.json().get(ApiFields.OBJ))

    async def validate_geodata(
        self, tokens: list[str], kind: str | None = None
    ) -> list[GeodataTokenIssue]:
        """Checks the routing tokens against the databases on disk (the panel accepts up to 500
        tokens).

        Arguments:
            tokens (list[str]): The routing tokens.
            kind (str | None): "ip" parses the tokens as IP rules, anything else as domain rules.

        Returns:
            list[GeodataTokenIssue]: The tokens which do not resolve.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            issues = await api.xray.validate_geodata(["geosite:google", "geosite:missing"])
            ```
        """
        endpoint = "panel/api/xray/geodata/validate"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        form = {"tokens": ",".join(tokens), "kind": kind}
        self.logger.info("Validating geodata tokens...")

        response = await self._post_form(url, headers, form)
        issues_json = response.json().get(ApiFields.OBJ) or []
        return [GeodataTokenIssue.model_validate(data) for data in issues_json]

    async def get_outbound_subs(self) -> list[OutboundSub]:
        """Retrieves the outbound subscriptions in the order of their priority. The panel leaves
        out the fetched outbounds here, see the outbound_count field.

        Returns:
            list[OutboundSub]: The outbound subscriptions.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            subs: list[py3xui.OutboundSub] = await api.xray.get_outbound_subs()
            ```
        """
        endpoint = "panel/api/xray/outbound-subs"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting outbound subscriptions...")

        response = await self._get(url, headers)
        subs_json = response.json().get(ApiFields.OBJ) or []
        return [OutboundSub.model_validate(data) for data in subs_json]

    async def add_outbound_sub(self, sub: OutboundSub) -> OutboundSub:
        """Adds a new outbound subscription. The panel only stores it, use
        `refresh_outbound_sub()` to fetch the outbounds right away.

        Arguments:
            sub (OutboundSub): The subscription to add.

        Returns:
            OutboundSub: The created subscription.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            sub = py3xui.OutboundSub(url="https://example.com/sub", remark="example")
            created: py3xui.OutboundSub = await api.xray.add_outbound_sub(sub)
            ```
        """
        endpoint = "panel/api/xray/outbound-subs"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = sub.to_form_fields()
        self.logger.info("Adding outbound subscription: %s", sub.remark)

        response = await self._post_form(url, headers, data)
        return OutboundSub.model_validate(response.json().get(ApiFields.OBJ))

    async def update_outbound_sub(self, sub_id: int, sub: OutboundSub) -> None:
        """Updates an outbound subscription.

        Note:
            The panel replaces all the editable fields, so the absent ones get their defaults.
            Get the subscription with `get_outbound_subs()` and change the fields you need.

        Arguments:
            sub_id (int): The ID of the subscription.
            sub (OutboundSub): The new values of the subscription.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            subs = await api.xray.get_outbound_subs()
            sub = subs[0]
            sub.remark = "new remark"
            await api.xray.update_outbound_sub(sub.id, sub)
            ```
        """
        endpoint = f"panel/api/xray/outbound-subs/{sub_id}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = sub.to_form_fields()
        self.logger.info("Updating outbound subscription: %s", sub_id)

        await self._post_form(url, headers, data)

    async def delete_outbound_sub(self, sub_id: int) -> None:
        """Deletes an outbound subscription.

        Arguments:
            sub_id (int): The ID of the subscription.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.delete_outbound_sub(1)
            ```
        """
        endpoint = f"panel/api/xray/outbound-subs/{sub_id}/del"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Deleting outbound subscription: %s", sub_id)

        await self._post_form(url, headers, {})

    async def refresh_outbound_sub(self, sub_id: int) -> list[dict[str, Any]]:
        """Fetches an outbound subscription right away.

        Arguments:
            sub_id (int): The ID of the subscription.

        Returns:
            list[dict[str, Any]]: The generated Xray outbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            outbounds = await api.xray.refresh_outbound_sub(1)
            ```
        """
        endpoint = f"panel/api/xray/outbound-subs/{sub_id}/refresh"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Refreshing outbound subscription: %s", sub_id)

        response = await self._post_form(url, headers, {})
        return response.json().get(ApiFields.OBJ) or []

    async def move_outbound_sub(self, sub_id: int, direction: str) -> None:
        """Moves an outbound subscription one step in the order of the merged outbounds.

        Arguments:
            sub_id (int): The ID of the subscription.
            direction (str): "up" raises the priority, anything else lowers it.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.xray.move_outbound_sub(1, "up")
            ```
        """
        endpoint = f"panel/api/xray/outbound-subs/{sub_id}/move"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"dir": direction}
        self.logger.info("Moving outbound subscription %s: %s", sub_id, direction)

        await self._post_form(url, headers, data)

    async def parse_outbound_sub(
        self,
        url: str,
        user_agent: str | None = None,
        allow_private: bool = False,
        allow_insecure: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetches a subscription URL and parses it into outbounds without saving it.

        Arguments:
            url (str): The URL of the subscription.
            user_agent (str | None): The User-Agent used to fetch the URL.
            allow_private (bool): Whether to allow a private or loopback address.
            allow_insecure (bool): Whether to skip the TLS certificate verification.

        Returns:
            list[dict[str, Any]]: The generated Xray outbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            outbounds = await api.xray.parse_outbound_sub("https://example.com/sub")
            ```
        """
        endpoint = "panel/api/xray/outbound-subs/parse"
        headers = {"Accept": "application/json"}
        request_url = self._url(endpoint)
        data = {
            "url": url,
            "userAgent": user_agent,
            "allowPrivate": allow_private,
            "allowInsecure": allow_insecure,
        }
        self.logger.info("Parsing outbound subscription URL...")

        response = await self._post_form(request_url, headers, data)
        return response.json().get(ApiFields.OBJ) or []
