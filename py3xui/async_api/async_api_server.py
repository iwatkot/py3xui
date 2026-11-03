"""This module contains the ServerApi class for handling server in the XUI API."""

from urllib.parse import quote

from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_base import AsyncBaseApi
from py3xui.server.config import ServerConfig, XrayVersionUnavailableError
from py3xui.server.keys import (
    EchCert,
    KeysFields,
    Mldsa65KeyPair,
    Mlkem768KeyPair,
    VlessEncryptionAuth,
    WebCertFiles,
)
from py3xui.server.reality_scan import RealityScanResult
from py3xui.server.server import RealityKeyPair, Server
from py3xui.server.panel_update import PanelUpdateFields, PanelUpdateInfo, PanelUpdateStatus
from py3xui.server.metrics import (
    CpuHistoryPoint,
    Fail2banStatus,
    HistoryPoint,
    ObservatorySnapshot,
    XrayMetricsState,
)


class AsyncServerApi(AsyncBaseApi):  # pylint: disable=too-many-public-methods
    """This class provides methods to interact with the server in the XUI API in an asynchronous
    manner.

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
        get_status: Retrieves the current server status.
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
        get_panel_update_info: Retrieves the current and the latest version of the panel.
        get_update_status: Retrieves the outcome of the most recent panel self-update.
        update_panel: Starts a panel self-update.
        set_update_channel: Switches the panel update channel between stable and dev.
        stop_xray: Stops the Xray service.
        restart_xray: Restarts the Xray service.
        generate_uuid: Generates a new UUID on the server.
        generate_mldsa65_keys: Generates a new ML-DSA-65 key pair on the server.
        generate_mlkem768_keys: Generates a new ML-KEM-768 key pair on the server.
        generate_vless_encryption: Generates new VLESS encryption options on the server.
        generate_ech_cert: Generates a new ECH key set on the server.
        get_web_cert_files: Retrieves the paths of the web TLS files of the panel.
        get_cert_hash: Computes the SHA-256 hash of a certificate.
        get_remote_cert_hash: Retrieves the SHA-256 hash of the certificate of a remote server.
        scan_reality_target: Probes a candidate REALITY target.
        scan_reality_targets: Probes several candidate REALITY targets.

    Examples:
        ```python
        import py3xui

        api = py3xui.AsyncApi.from_env()
        await api.login()

        # Get server status
        status = await api.server.get_status()
        print(f"CPU Load: {status.cpu}%")
        print(f"Memory Used: {status.mem.current}/{status.mem.total} bytes")

        # Get DB backup
        db_save_path = "db_backup.db"
        await api.server.get_db(db_save_path)
        ```
    """

    # pylint: disable=R0801
    async def get_db(self, save_path: str) -> None:
        """This route is used to retrieve a database backup file and save it to a specified path.

        Arguments:
            save_path (str): The path to save the database backup file.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            db_save_path = "db_backup.db"
            await api.server.get_db(db_save_path)
            ```
        """
        endpoint = "panel/api/server/getDb"
        headers = {"Accept": "application/octet-stream"}
        url = self._url(endpoint)
        self.logger.info("Getting DB backup...")

        response = await self._get(url, headers, skip_check=True)

        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            self.logger.info("DB backup saved to %s", save_path)
        else:
            self.logger.error("Failed to get DB backup: %s", response.text)
            response.raise_for_status()

    async def get_status(self) -> Server:
        """Retrieves the current server status.

        Returns:
            Server: An object containing server status information

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            status = await api.server.get_status()
            print(f"CPU Load: {status.cpu}%")
            print(f"Memory Used: {status.mem.current}/{status.mem.total} bytes")
            ```
        """
        endpoint = "panel/api/server/status"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting server status...")

        response = await self._get(url, headers)
        server_json = response.json().get(ApiFields.OBJ)
        self.logger.info("Server status: %s", server_json)
        server = Server.model_validate(server_json)
        return server

    async def generate_reality_keys(self) -> RealityKeyPair:
        """Generates a new Reality (X25519) key pair on the server.

        Returns:
            RealityKeyPair: Generated key pair containing private and public keys.
        """
        endpoint = "panel/api/server/getNewX25519Cert"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new Reality keys...")

        response = await self._get(url, headers)
        keys_json = response.json().get(ApiFields.OBJ)

        if not keys_json:
            raise ValueError("Reality keys were not returned by the server.")

        self.logger.debug("Reality keys generated: %s", keys_json)
        return RealityKeyPair.model_validate(keys_json)

    async def install_new_xray_version(self, version: str) -> None:
        """Installs a new version of Xray on the server.

        Arguments:
            version (str): The version of Xray to install (e.g. "1.5.0").
        """
        endpoint = f"panel/api/server/installXray/{version}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Installing new Xray version %s...", version)

        await self._post(url, headers, data={})

        self.logger.info("Xray version %s installed successfully.", version)

    async def update_geofile(self, file_name: str | None = None) -> None:
        """Triggers an update of the geofile on the server.

        Arguments:
            file_name (str | None): The geofile to update (e.g. "geoip.dat"). All the geofiles
                are updated when it is not set.
        """

        endpoint = "panel/api/server/updateGeofile"
        if file_name is not None:
            endpoint = f"panel/api/server/updateGeofile/{quote(file_name, safe='')}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Updating geofile...")

        await self._post(url, headers, data={})

        self.logger.info("Geofile updated successfully.")

    async def get_xray_version(self) -> list[str]:
        """Gets the current version of Xray running on the server.

        Returns:
            list[str]: The version of Xray.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            xray_version = await api.server.get_xray_version()
            print(f"Xray Version: {xray_version}")
            ```
        """
        endpoint = "panel/api/server/getXrayVersion"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray version...")

        response = await self._get(url, headers)
        versions_json = response.json().get(ApiFields.OBJ)

        if versions_json is None:
            raise XrayVersionUnavailableError("Xray version was not returned by the server.")

        self.logger.debug("Xray version: %s", versions_json)
        return versions_json

    async def get_server_config(self) -> ServerConfig:
        """Gets the current server configuration.

        Returns:
            ServerConfig: The server configuration.
        
        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            config = await api.server.get_server_config()
            print(f"Inbounds: {config.inbounds}")
            print(f"Transport is used: {config.transport}")
            ```
        """
        endpoint = "panel/api/server/getConfigJson"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting server config...")

        response = await self._get(url, headers)
        config_json = response.json().get(ApiFields.OBJ)

        if not config_json:
            raise ValueError("Server config was not returned by the server.")

        self.logger.debug("Server config: %s", config_json)
        return ServerConfig.model_validate(config_json)

    async def get_fail2ban_status(self) -> Fail2banStatus:
        """Gets the availability of Fail2ban, which per-client IP limits depend on.

        Returns:
            Fail2banStatus: The Fail2ban status.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            status = await api.server.get_fail2ban_status()
            print(status.usable)
            ```
        """
        endpoint = "panel/api/server/fail2banStatus"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Fail2ban status...")

        response = await self._get(url, headers)
        return Fail2banStatus.model_validate(response.json().get(ApiFields.OBJ))

    async def get_cpu_history(self, bucket: int) -> list[CpuHistoryPoint]:
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

            api = py3xui.AsyncApi.from_env()
            await api.login()

            points = await api.server.get_cpu_history(60)
            print(points[-1].cpu)
            ```
        """
        endpoint = f"panel/api/server/cpuHistory/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting CPU history for bucket %s...", bucket)

        response = await self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [CpuHistoryPoint.model_validate(point) for point in points_json]

    async def get_history(self, metric: str, bucket: int) -> list[HistoryPoint]:
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

            api = py3xui.AsyncApi.from_env()
            await api.login()

            points = await api.server.get_history("mem", 60)
            print(points[-1].v)
            ```
        """
        endpoint = f"panel/api/server/history/{quote(metric, safe='')}/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting history of %s for bucket %s...", metric, bucket)

        response = await self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [HistoryPoint.model_validate(point) for point in points_json]

    async def get_xray_metrics_state(self) -> XrayMetricsState:
        """Gets the state of the Xray runtime metrics collection.

        Returns:
            XrayMetricsState: The metrics state.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            state = await api.server.get_xray_metrics_state()
            print(state.enabled, state.listen)
            ```
        """
        endpoint = "panel/api/server/xrayMetricsState"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray metrics state...")

        response = await self._get(url, headers)
        return XrayMetricsState.model_validate(response.json().get(ApiFields.OBJ))

    async def get_xray_metrics_history(self, metric: str, bucket: int) -> list[HistoryPoint]:
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

            api = py3xui.AsyncApi.from_env()
            await api.login()

            points = await api.server.get_xray_metrics_history("xrAlloc", 60)
            print(points[-1].v)
            ```
        """
        endpoint = f"panel/api/server/xrayMetricsHistory/{quote(metric, safe='')}/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray metric history of %s for bucket %s...", metric, bucket)

        response = await self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [HistoryPoint.model_validate(point) for point in points_json]

    async def get_xray_observatory(self) -> list[ObservatorySnapshot]:
        """Gets the latest Xray observatory results for each probed outbound. The list is empty
        when the Xray config has no observatory.

        Returns:
            list[ObservatorySnapshot]: The results sorted by the outbound tag.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            for outbound in await api.server.get_xray_observatory():
                print(outbound.tag, outbound.alive, outbound.delay)
            ```
        """
        endpoint = "panel/api/server/xrayObservatory"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Xray observatory...")

        response = await self._get(url, headers)
        snapshots_json = response.json().get(ApiFields.OBJ) or []
        return [ObservatorySnapshot.model_validate(snapshot) for snapshot in snapshots_json]

    async def get_xray_observatory_history(self, tag: str, bucket: int) -> list[HistoryPoint]:
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

            api = py3xui.AsyncApi.from_env()
            await api.login()

            points = await api.server.get_xray_observatory_history("proxy", 60)
            print(points[-1].v)
            ```
        """
        endpoint = f"panel/api/server/xrayObservatoryHistory/{quote(tag, safe='')}/{bucket}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting observatory history of %s for bucket %s...", tag, bucket)

        response = await self._get(url, headers)
        points_json = response.json().get(ApiFields.OBJ) or []
        return [HistoryPoint.model_validate(point) for point in points_json]

    async def get_panel_update_info(self) -> PanelUpdateInfo:
        """Gets the current and the latest version of the panel.

        Returns:
            PanelUpdateInfo: The panel versions.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            info = await api.server.get_panel_update_info()
            print(info.current_version, info.latest_version, info.update_available)
            ```
        """
        endpoint = "panel/api/server/getPanelUpdateInfo"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting panel update info...")

        response = await self._get(url, headers)
        return PanelUpdateInfo.model_validate(response.json().get(ApiFields.OBJ))

    async def get_update_status(self) -> PanelUpdateStatus:
        """Gets the outcome of the most recently launched panel self-update.

        Returns:
            PanelUpdateStatus: The status of the update.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            status = await api.server.get_update_status()
            print(status.run_id, status.state)
            ```
        """
        endpoint = "panel/api/server/getUpdateStatus"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting panel update status...")

        response = await self._get(url, headers)
        return PanelUpdateStatus.model_validate(response.json().get(ApiFields.OBJ))

    async def update_panel(self, dev: bool | None = None) -> str:
        """Starts a panel self-update. The panel restarts when the update succeeds.

        Arguments:
            dev (bool | None): Overrides the update channel for this run: True for the dev channel,
                False for the stable one. The channel configured on the panel is used when it is
                not set.

        Returns:
            str: The ID of the update run, to compare with `get_update_status().run_id`.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            run_id = await api.server.update_panel()
            print(run_id)
            ```
        """
        endpoint = "panel/api/server/updatePanel"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Starting panel update...")

        response = await self._post_form(url, headers, {"dev": dev})
        return response.json().get(ApiFields.OBJ).get(PanelUpdateFields.RUN_ID)

    async def set_update_channel(self, dev: bool) -> None:
        """Switches the panel update channel between stable and dev.

        Arguments:
            dev (bool): True for the dev channel, False for the stable one.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.server.set_update_channel(False)
            ```
        """
        endpoint = "panel/api/server/setUpdateChannel"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Setting panel update channel, dev: %s...", dev)

        await self._post_form(url, headers, {"dev": dev})
        self.logger.info("Panel update channel set successfully.")

    async def stop_xray(self) -> None:
        """Stops the Xray service. All the proxies go offline immediately.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.server.stop_xray()
            ```
        """
        endpoint = "panel/api/server/stopXrayService"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Stopping Xray service...")

        await self._post(url, headers, data={})
        self.logger.info("Xray service stopped successfully.")

    async def restart_xray(self) -> None:
        """Restarts the Xray service.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.server.restart_xray()
            ```
        """
        endpoint = "panel/api/server/restartXrayService"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Restarting Xray service...")

        await self._post(url, headers, data={})
        self.logger.info("Xray service restarted successfully.")

    async def generate_uuid(self) -> str:
        """Generates a new UUID on the server.

        Returns:
            str: The generated UUID.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            print(await api.server.generate_uuid())
            ```
        """
        endpoint = "panel/api/server/getNewUUID"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new UUID...")

        response = await self._get(url, headers)
        return response.json().get(ApiFields.OBJ).get(KeysFields.UUID)

    async def generate_mldsa65_keys(self) -> Mldsa65KeyPair:
        """Generates a new ML-DSA-65 key pair on the server.

        Returns:
            Mldsa65KeyPair: The generated key pair.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            keys = await api.server.generate_mldsa65_keys()
            print(keys.seed, keys.verify)
            ```
        """
        endpoint = "panel/api/server/getNewmldsa65"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new ML-DSA-65 keys...")

        response = await self._get(url, headers)
        return Mldsa65KeyPair.model_validate(response.json().get(ApiFields.OBJ))

    async def generate_mlkem768_keys(self) -> Mlkem768KeyPair:
        """Generates a new ML-KEM-768 key pair on the server.

        Returns:
            Mlkem768KeyPair: The generated key pair.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            keys = await api.server.generate_mlkem768_keys()
            print(keys.seed, keys.client)
            ```
        """
        endpoint = "panel/api/server/getNewmlkem768"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new ML-KEM-768 keys...")

        response = await self._get(url, headers)
        return Mlkem768KeyPair.model_validate(response.json().get(ApiFields.OBJ))

    async def generate_vless_encryption(self) -> list[VlessEncryptionAuth]:
        """Generates new VLESS encryption options on the server.

        Returns:
            list[VlessEncryptionAuth]: The generated options.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            for auth in await api.server.generate_vless_encryption():
                print(auth.id, auth.decryption, auth.encryption)
            ```
        """
        endpoint = "panel/api/server/getNewVlessEnc"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new VLESS encryption options...")

        response = await self._get(url, headers)
        auths_json = response.json().get(ApiFields.OBJ).get(KeysFields.AUTHS) or []
        return [VlessEncryptionAuth.model_validate(auth) for auth in auths_json]

    async def generate_ech_cert(self, sni: str) -> EchCert:
        """Generates a new ECH (Encrypted Client Hello) key set on the server.

        Arguments:
            sni (str): The server name to generate the key set for.

        Returns:
            EchCert: The generated key set.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            cert = await api.server.generate_ech_cert("example.com")
            print(cert.ech_config_list)
            ```
        """
        endpoint = "panel/api/server/getNewEchCert"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new ECH key set for %s...", sni)

        response = await self._post_form(url, headers, {"sni": sni})
        return EchCert.model_validate(response.json().get(ApiFields.OBJ))

    async def get_web_cert_files(self) -> WebCertFiles:
        """Gets the paths of the web TLS certificate and key files of the panel.

        Returns:
            WebCertFiles: The paths on the host of the panel.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            files = await api.server.get_web_cert_files()
            print(files.web_cert_file, files.web_key_file)
            ```
        """
        endpoint = "panel/api/server/getWebCertFiles"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting web certificate files...")

        response = await self._get(url, headers)
        return WebCertFiles.model_validate(response.json().get(ApiFields.OBJ))

    async def get_cert_hash(
        self, cert_file: str | None = None, cert_content: str | None = None
    ) -> list[str]:
        """Computes the hex SHA-256 hash of a certificate for pinning.

        Arguments:
            cert_file (str | None): The path to a certificate file on the server, which must be
                referenced by an inbound or by the panel settings. Takes precedence over
                `cert_content`.
            cert_content (str | None): The inline PEM (or DER) certificate content.

        Returns:
            list[str]: The hashes of the certificates.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            print(await api.server.get_cert_hash(cert_file="/root/cert/fullchain.pem"))
            ```
        """
        endpoint = "panel/api/server/getCertHash"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting certificate hash...")

        data = {"certFile": cert_file, "certContent": cert_content}
        response = await self._post_form(url, headers, data)
        return response.json().get(ApiFields.OBJ) or []

    async def get_remote_cert_hash(self, server: str, allow_private: bool = False) -> list[str]:
        """Gets the live SHA-256 hashes of the certificate of a remote server for pinning.

        Arguments:
            server (str): The remote server as domain or domain:port (the default port is 443).
            allow_private (bool): Whether a private or loopback server may be pinged. The panel
                rejects such a server otherwise.

        Returns:
            list[str]: The hashes of the certificates.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            print(await api.server.get_remote_cert_hash("cloudflare-dns.com"))
            ```
        """
        endpoint = "panel/api/server/getRemoteCertHash"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting certificate hash of %s...", server)

        data = {"server": server, "allowPrivate": allow_private}
        response = await self._post_form(url, headers, data)
        return response.json().get(ApiFields.OBJ) or []

    async def scan_reality_target(
        self, target: str, sni: str | None = None, xver: int = 0, allow_private: bool = False
    ) -> RealityScanResult:
        """Probes a candidate REALITY target and returns a feasibility verdict.

        Arguments:
            target (str): The target as host or host:port (the default port is 443).
            sni (str | None): The SNI for the handshake, defaults to the host of the target.
            xver (int): The PROXY protocol version the target expects, 0 for none.
            allow_private (bool): Whether a private or loopback target may be probed.

        Returns:
            RealityScanResult: The verdict.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            result = await api.server.scan_reality_target("www.cloudflare.com:443")
            print(result.feasible, result.reason)
            ```
        """
        endpoint = "panel/api/server/scanRealityTarget"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Scanning REALITY target %s...", target)

        data = {"target": target, "sni": sni, "xver": xver, "allowPrivate": allow_private}
        response = await self._post_form(url, headers, data)
        return RealityScanResult.model_validate(response.json().get(ApiFields.OBJ))

    async def scan_reality_targets(
        self, targets: list[str] | None = None
    ) -> list[RealityScanResult]:
        """Probes several candidate REALITY targets.

        Arguments:
            targets (list[str] | None): The targets: domain[:port], IP[:port] or CIDR. The
                candidates from the panel settings are probed when it is not set.

        Returns:
            list[RealityScanResult]: The verdicts ranked by feasibility, then by latency.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            targets = ["www.cloudflare.com", "104.16.0.0/24"]
            for result in await api.server.scan_reality_targets(targets):
                print(result.target, result.feasible)
            ```
        """
        endpoint = "panel/api/server/scanRealityTargets"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Scanning REALITY targets...")

        data = {"targets": ",".join(targets) if targets else None}
        response = await self._post_form(url, headers, data)
        results_json = response.json().get(ApiFields.OBJ) or []
        return [RealityScanResult.model_validate(result) for result in results_json]
