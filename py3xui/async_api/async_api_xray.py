"""This module contains the AsyncXrayApi class for handling the Xray settings in the XUI API
asynchronously."""

# pylint: disable=R0801
from typing import Any

from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_base import AsyncBaseApi
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
