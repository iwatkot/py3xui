"""This module contains the ServerApi class for handling server in the XUI API."""

from urllib.parse import quote

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.server.server import RealityKeyPair, Server
from py3xui.server.metrics import (
    CpuHistoryPoint,
    Fail2banStatus,
    HistoryPoint,
    ObservatorySnapshot,
    XrayMetricsState,
)
from py3xui.server.config import ServerConfig, XrayVersionUnavailableError



class ServerApi(BaseApi):
    """This class provides methods to interact with the server in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_db: Retrieves a database backup file and saves it to a specified path.
        get_status: Retrieves the current status of the server.
        generate_reality_keys: Generates a new Reality (X25519) key pair on the server.
        install_new_xray_version: Installs a new version of Xray on the server.
        update_geofile: Triggers an update of the geofile on the server.
        get_xray_version: Retrieves the current version of Xray running on the server.
        get_server_config: Retrieves the current server configuration.
        get_fail2ban_status: Retrieves the availability of Fail2ban on the server.
        get_cpu_history: Retrieves the legacy aggregated CPU history.
        get_history: Retrieves the aggregated history of a system metric.
        get_xray_metrics_state: Retrieves the state of the Xray metrics collection.
        get_xray_metrics_history: Retrieves the aggregated history of an Xray metric.
        get_xray_observatory: Retrieves the latest Xray observatory results.
        get_xray_observatory_history: Retrieves the delay history of an observatory outbound.

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()
        api.login()

        db_save_path = "db_backup.db"
        api.server.get_db(db_save_path)
        ```
    """

    def get_db(self, save_path: str) -> None:
        """This route is used to retrieve a database backup file and save it to a specified path.

        Arguments:
            save_path (str): The path to save the database backup file.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            db_save_path = "db_backup.db"
            api.server.get_db(db_save_path)
            ```
        """
        endpoint = "panel/api/server/getDb"
        headers = {"Accept": "application/octet-stream"}
        url = self._url(endpoint)
        self.logger.info("Getting DB backup...")

        response = self._get(url, headers, skip_check=True)

        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            self.logger.info("DB backup saved to %s", save_path)
        else:
            self.logger.error("Failed to get DB backup: %s", response.text)
            response.raise_for_status()

    def get_status(self) -> Server:
        """Gets the current server status.

        Returns:
            Server: Object containing server status information

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            status = api.server.get_status()
            print(f"CPU Load: {status.cpu}%")
            print(f"Memory Used: {status.mem.current}/{status.mem.total} bytes")
            ```
        """
        endpoint = "panel/api/server/status"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting server status...")

        response = self._get(url, headers)
        server_json = response.json().get(ApiFields.OBJ)

        self.logger.debug("Server status: %s", server_json)
        server = Server.model_validate(server_json)
        return server

    def generate_reality_keys(self) -> RealityKeyPair:
        """Generates a new Reality (X25519) key pair on the server.

        Returns:
            RealityKeyPair: Generated key pair containing private and public keys.
        """
        endpoint = "panel/api/server/getNewX25519Cert"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new Reality keys...")

        response = self._get(url, headers)
        keys_json = response.json().get(ApiFields.OBJ)

        if not keys_json:
            raise ValueError("Reality keys were not returned by the server.")

        self.logger.debug("Reality keys generated: %s", keys_json)
        return RealityKeyPair.model_validate(keys_json)

    def install_new_xray_version(self, version: str) -> None:
        """Installs a new version of Xray on the server.

        Arguments:
            version (str): The version of Xray to install (e.g. "1.5.0").
        
        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.server.install_new_xray_version("1.5.0")
            ```
        """
        endpoint = f"panel/api/server/installXray/{version}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Installing new Xray version %s...", version)

        self._post(url, headers, data={})
        self.logger.info("Xray version %s installed successfully.", version)

    def update_geofile(self) -> None:
        """Triggers an update of the geofile on the server.
        
        Examples:
            ```python
            import py3xui
            
            api = py3xui.Api.from_env()
            api.login()

            api.server.update_geofile()                
            ```
        """

        endpoint = "panel/api/server/updateGeofile"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Updating geofile...")

        self._post(url, headers, data={})
        self.logger.info("Geofile updated successfully.")


    def get_xray_version(self) -> list[str]:
        """Gets the current version of Xray running on the server.

        Returns:
            list[str]: The version of Xray.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            xray_version = api.server.get_xray_version()
            print(f"Xray Version: {xray_version}")
            ```
        """
        endpoint = "panel/api/server/getXrayVersion"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray version...")

        response = self._get(url, headers)
        version_json = response.json().get(ApiFields.OBJ)

        if version_json is None:
            raise XrayVersionUnavailableError("Xray version was not returned by the server.")

        self.logger.debug("Xray version: %s", version_json)
        return version_json

    def get_server_config(self) -> ServerConfig:
        """Gets the current server configuration.

        Returns:
            ServerConfig: The server configuration.
        
        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            config = api.server.get_server_config()
            print(f"Inbounds: {config.inbounds}")
            print(f"Transport is used: {config.transport}")
            ```
        """
        endpoint = "panel/api/server/getConfigJson"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting server config...")

        response = self._get(url, headers)
        config_json = response.json().get(ApiFields.OBJ)

        if not config_json:
            raise ValueError("Server config was not returned by the server.")

        self.logger.debug("Server config: %s", config_json)
        return ServerConfig.model_validate(config_json)

    def get_fail2ban_status(self) -> Fail2banStatus:
        """Gets the availability of Fail2ban, which per-client IP limits depend on.

        Returns:
            Fail2banStatus: The Fail2ban status.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            status = api.server.get_fail2ban_status()
            print(status.usable)
            ```
        """
        endpoint = "panel/api/server/fail2banStatus"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Fail2ban status...")

        response = self._get(url, headers)
        return Fail2banStatus.model_validate(response.json().get(ApiFields.OBJ))

    def get_cpu_history(self, bucket: int) -> list[CpuHistoryPoint]:
        """Gets the legacy aggregated CPU history (up to 60 points). The panel keeps this route
        for compatibility, `get_history("cpu", bucket)` returns the same data.

        Arguments:
            bucket (int): The bucket size in seconds: 2, 30, 60, 180, 360, 720, 1440, 2880 or
                10080.

        Returns:
            list[CpuHistoryPoint]: The history points.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            points = api.server.get_cpu_history(60)
            print(points[-1].cpu)
            ```
        """
        endpoint = f"panel/api/server/cpuHistory/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting CPU history for bucket %s...", bucket)

        response = self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [CpuHistoryPoint.model_validate(point) for point in points_json]

    def get_history(self, metric: str, bucket: int) -> list[HistoryPoint]:
        """Gets the aggregated history of a system metric (up to 60 points).

        Arguments:
            metric (str): The metric: cpu, mem, swap, netUp, netDown, pktUp, pktDown, diskRead,
                diskWrite, diskUsage, tcpCount, udpCount, online, load1, load5 or load15.
            bucket (int): The bucket size in seconds: 2, 30, 60, 180, 360, 720, 1440, 2880 or
                10080.

        Returns:
            list[HistoryPoint]: The history points.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            points = api.server.get_history("mem", 60)
            print(points[-1].v)
            ```
        """
        endpoint = f"panel/api/server/history/{quote(metric, safe='')}/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting history of %s for bucket %s...", metric, bucket)

        response = self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [HistoryPoint.model_validate(point) for point in points_json]

    def get_xray_metrics_state(self) -> XrayMetricsState:
        """Gets the state of the Xray runtime metrics collection.

        Returns:
            XrayMetricsState: The metrics state.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            state = api.server.get_xray_metrics_state()
            print(state.enabled, state.listen)
            ```
        """
        endpoint = "panel/api/server/xrayMetricsState"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray metrics state...")

        response = self._get(url, headers)
        return XrayMetricsState.model_validate(response.json().get(ApiFields.OBJ))

    def get_xray_metrics_history(self, metric: str, bucket: int) -> list[HistoryPoint]:
        """Gets the aggregated history of an Xray runtime metric (up to 60 points).

        Arguments:
            metric (str): The metric: xrAlloc, xrSys, xrHeapObjects, xrNumGC or xrPauseNs.
            bucket (int): The bucket size in seconds: 2, 30, 60, 180, 360, 720, 1440, 2880 or
                10080.

        Returns:
            list[HistoryPoint]: The history points.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            points = api.server.get_xray_metrics_history("xrAlloc", 60)
            print(points[-1].v)
            ```
        """
        endpoint = f"panel/api/server/xrayMetricsHistory/{quote(metric, safe='')}/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray metric history of %s for bucket %s...", metric, bucket)

        response = self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [HistoryPoint.model_validate(point) for point in points_json]

    def get_xray_observatory(self) -> list[ObservatorySnapshot]:
        """Gets the latest Xray observatory results for each probed outbound. The list is empty
        when the Xray config has no observatory.

        Returns:
            list[ObservatorySnapshot]: The results sorted by the outbound tag.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            for outbound in api.server.get_xray_observatory():
                print(outbound.tag, outbound.alive, outbound.delay)
            ```
        """
        endpoint = "panel/api/server/xrayObservatory"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray observatory...")

        response = self._get(url, headers)
        snapshots_json = response.json().get(ApiFields.OBJ) or []
        return [ObservatorySnapshot.model_validate(snapshot) for snapshot in snapshots_json]

    def get_xray_observatory_history(self, tag: str, bucket: int) -> list[HistoryPoint]:
        """Gets the aggregated delay history of an observatory outbound (up to 60 points).

        Arguments:
            tag (str): The outbound tag known to the observatory.
            bucket (int): The bucket size in seconds: 2, 30, 60, 180, 360, 720, 1440, 2880 or
                10080.

        Returns:
            list[HistoryPoint]: The history points.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            points = api.server.get_xray_observatory_history("proxy", 60)
            print(points[-1].v)
            ```
        """
        endpoint = f"panel/api/server/xrayObservatoryHistory/{quote(tag, safe='')}/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting observatory history of %s for bucket %s...", tag, bucket)

        response = self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [HistoryPoint.model_validate(point) for point in points_json]
