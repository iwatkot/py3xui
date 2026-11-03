"""This module contains the XrayApi class for handling the Xray settings in the XUI API."""

# pylint: disable=R0801
from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.xray.xray import OutboundTraffic, XraySettings, parse_json_obj


class XrayApi(BaseApi):
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

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()
        api.login()

        settings: py3xui.XraySettings = api.xray.get_settings()
        ```
    """

    def get_settings(self) -> XraySettings:
        """Retrieves the Xray configuration template and the data the panel returns along
        with it. The panel sends the whole payload as a JSON string, it's parsed here.

        Returns:
            XraySettings: The Xray configuration template and the related data.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            settings: py3xui.XraySettings = api.xray.get_settings()
            print(settings.xray_setting["outbounds"])
            ```
        """
        endpoint = "panel/api/xray/"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray settings...")

        response = self._post_form(url, headers, {})
        return XraySettings.model_validate(
            parse_json_obj(response.json().get(ApiFields.OBJ))
        )

    def get_default_config(self) -> dict:
        """Retrieves the default Xray configuration shipped with the panel.

        Returns:
            dict: The default Xray configuration.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            config: dict = api.xray.get_default_config()
            ```
        """
        endpoint = "panel/api/xray/getDefaultJsonConfig"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting default Xray config...")

        response = self._get(url, headers)
        return response.json().get(ApiFields.OBJ)

    def get_outbounds_traffic(self) -> list[OutboundTraffic]:
        """Retrieves the traffic statistics of the outbounds.

        Returns:
            list[OutboundTraffic]: The traffic statistics of the outbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            traffic: list[py3xui.OutboundTraffic] = api.xray.get_outbounds_traffic()
            ```
        """
        endpoint = "panel/api/xray/getOutboundsTraffic"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting outbounds traffic...")

        response = self._get(url, headers)
        traffic_json = response.json().get(ApiFields.OBJ) or []
        return [OutboundTraffic.model_validate(data) for data in traffic_json]

    def get_result(self) -> str:
        """Retrieves the latest output of the Xray process. It's useful to check for startup
        errors.

        Returns:
            str: The output of the Xray process.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            result: str = api.xray.get_result()
            ```
        """
        endpoint = "panel/api/xray/getXrayResult"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray result...")

        response = self._get(url, headers)
        return response.json().get(ApiFields.OBJ) or ""

    def update(self, config: str, outbound_test_url: str | None = None) -> None:
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

            api = py3xui.Api.from_env()
            api.login()

            settings = api.xray.get_settings()
            api.xray.update(json.dumps(settings.xray_setting), settings.outbound_test_url)
            ```
        """
        endpoint = "panel/api/xray/update"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"xraySetting": config, "outboundTestUrl": outbound_test_url}
        self.logger.info("Updating Xray settings...")

        self._post_form(url, headers, data)
        self.logger.info("Xray settings updated successfully.")

    def reset_outbound_stats(self, tag: str) -> None:
        """Resets the traffic statistics of an outbound.

        Arguments:
            tag (str): The tag of the outbound. Use "-alltags-" to reset all the outbounds.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.xray.reset_outbound_stats("direct")
            ```
        """
        endpoint = "panel/api/xray/resetOutboundsTraffic"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"tag": tag}
        self.logger.info("Resetting traffic of outbound: %s", tag)

        self._post_form(url, headers, data)
        self.logger.info("Outbound traffic reset successfully.")
