"""This module contains the ServerApi class for handling server in the XUI API."""

# pylint: disable=too-many-lines

import os
from urllib.parse import quote

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.server.client_ips import InboundClientIps
from py3xui.server.keys import (
    EchCert,
    KeysFields,
    Mldsa65KeyPair,
    Mlkem768KeyPair,
    VlessEncryptionAuth,
    WebCertFiles,
)
from py3xui.server.node_summary import NodeSummary
from py3xui.server.reality_scan import RealityScanResult
from py3xui.server.server import RealityKeyPair, Server
from py3xui.server.panel_update import PanelUpdateFields, PanelUpdateInfo, PanelUpdateStatus
from py3xui.server.logs import AmneziaWGLogs, XrayLogEntry
from py3xui.server.metrics import (
    CpuHistoryPoint,
    Fail2banStatus,
    HistoryPoint,
    ObservatorySnapshot,
    XrayMetricsState,
)
from py3xui.server.config import ServerConfig, XrayVersionUnavailableError



class ServerApi(BaseApi):  # pylint: disable=too-many-public-methods
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
        get_logs: Retrieves the last lines of the panel log.
        get_xray_logs: Retrieves the last lines of the Xray access log.
        get_amneziawg_logs: Retrieves the live AmneziaWG activity.
        get_migration: Retrieves a cross-engine migration file and saves it to a specified path.
        import_db: Restores the panel database from a backup or migration file.
        get_descendants: Retrieves the summaries of the nodes managed by the panel.
        get_client_ips: Retrieves the recently active IP addresses of all the clients.
        push_client_ips: Merges recently active IP addresses into the panel database.

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

    def update_geofile(self, file_name: str | None = None) -> None:
        """Triggers an update of the geofile on the server.

        Arguments:
            file_name (str | None): The geofile to update (e.g. "geoip.dat"). All the geofiles
                are updated when it is not set.

        Examples:
            ```python
            import py3xui
            
            api = py3xui.Api.from_env()
            api.login()

            api.server.update_geofile()                
            api.server.update_geofile("geoip.dat")
            ```
        """

        endpoint = "panel/api/server/updateGeofile"
        if file_name is not None:
            endpoint = f"panel/api/server/updateGeofile/{quote(file_name, safe='')}"
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

    def get_panel_update_info(self) -> PanelUpdateInfo:
        """Gets the current and the latest version of the panel.

        Returns:
            PanelUpdateInfo: The panel versions.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            info = api.server.get_panel_update_info()
            print(info.current_version, info.latest_version, info.update_available)
            ```
        """
        endpoint = "panel/api/server/getPanelUpdateInfo"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting panel update info...")

        response = self._get(url, headers)
        return PanelUpdateInfo.model_validate(response.json().get(ApiFields.OBJ))

    def get_update_status(self) -> PanelUpdateStatus:
        """Gets the outcome of the most recently launched panel self-update.

        Returns:
            PanelUpdateStatus: The status of the update.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            status = api.server.get_update_status()
            print(status.run_id, status.state)
            ```
        """
        endpoint = "panel/api/server/getUpdateStatus"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting panel update status...")

        response = self._get(url, headers)
        return PanelUpdateStatus.model_validate(response.json().get(ApiFields.OBJ))

    def update_panel(self, dev: bool | None = None) -> str:
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

            api = py3xui.Api.from_env()
            api.login()

            run_id = api.server.update_panel()
            print(run_id)
            ```
        """
        endpoint = "panel/api/server/updatePanel"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Starting panel update...")

        response = self._post_form(url, headers, {"dev": dev})
        return response.json().get(ApiFields.OBJ).get(PanelUpdateFields.RUN_ID)

    def set_update_channel(self, dev: bool) -> None:
        """Switches the panel update channel between stable and dev.

        Arguments:
            dev (bool): True for the dev channel, False for the stable one.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.server.set_update_channel(False)
            ```
        """
        endpoint = "panel/api/server/setUpdateChannel"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Setting panel update channel, dev: %s...", dev)

        self._post_form(url, headers, {"dev": dev})
        self.logger.info("Panel update channel set successfully.")

    def stop_xray(self) -> None:
        """Stops the Xray service. All the proxies go offline immediately.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.server.stop_xray()
            ```
        """
        endpoint = "panel/api/server/stopXrayService"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Stopping Xray service...")

        self._post(url, headers, data={})
        self.logger.info("Xray service stopped successfully.")

    def restart_xray(self) -> None:
        """Restarts the Xray service.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.server.restart_xray()
            ```
        """
        endpoint = "panel/api/server/restartXrayService"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Restarting Xray service...")

        self._post(url, headers, data={})
        self.logger.info("Xray service restarted successfully.")

    def generate_uuid(self) -> str:
        """Generates a new UUID on the server.

        Returns:
            str: The generated UUID.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            print(api.server.generate_uuid())
            ```
        """
        endpoint = "panel/api/server/getNewUUID"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new UUID...")

        response = self._get(url, headers)
        return response.json().get(ApiFields.OBJ).get(KeysFields.UUID)

    def generate_mldsa65_keys(self) -> Mldsa65KeyPair:
        """Generates a new ML-DSA-65 key pair on the server.

        Returns:
            Mldsa65KeyPair: The generated key pair.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            keys = api.server.generate_mldsa65_keys()
            print(keys.seed, keys.verify)
            ```
        """
        endpoint = "panel/api/server/getNewmldsa65"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new ML-DSA-65 keys...")

        response = self._get(url, headers)
        return Mldsa65KeyPair.model_validate(response.json().get(ApiFields.OBJ))

    def generate_mlkem768_keys(self) -> Mlkem768KeyPair:
        """Generates a new ML-KEM-768 key pair on the server.

        Returns:
            Mlkem768KeyPair: The generated key pair.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            keys = api.server.generate_mlkem768_keys()
            print(keys.seed, keys.client)
            ```
        """
        endpoint = "panel/api/server/getNewmlkem768"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new ML-KEM-768 keys...")

        response = self._get(url, headers)
        return Mlkem768KeyPair.model_validate(response.json().get(ApiFields.OBJ))

    def generate_vless_encryption(self) -> list[VlessEncryptionAuth]:
        """Generates new VLESS encryption options on the server.

        Returns:
            list[VlessEncryptionAuth]: The generated options.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            for auth in api.server.generate_vless_encryption():
                print(auth.id, auth.decryption, auth.encryption)
            ```
        """
        endpoint = "panel/api/server/getNewVlessEnc"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new VLESS encryption options...")

        response = self._get(url, headers)
        auths_json = response.json().get(ApiFields.OBJ).get(KeysFields.AUTHS) or []
        return [VlessEncryptionAuth.model_validate(auth) for auth in auths_json]

    def generate_ech_cert(self, sni: str) -> EchCert:
        """Generates a new ECH (Encrypted Client Hello) key set on the server.

        Arguments:
            sni (str): The server name to generate the key set for.

        Returns:
            EchCert: The generated key set.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            cert = api.server.generate_ech_cert("example.com")
            print(cert.ech_config_list)
            ```
        """
        endpoint = "panel/api/server/getNewEchCert"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Generating new ECH key set for %s...", sni)

        response = self._post_form(url, headers, {"sni": sni})
        return EchCert.model_validate(response.json().get(ApiFields.OBJ))

    def get_web_cert_files(self) -> WebCertFiles:
        """Gets the paths of the web TLS certificate and key files of the panel.

        Returns:
            WebCertFiles: The paths on the host of the panel.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            files = api.server.get_web_cert_files()
            print(files.web_cert_file, files.web_key_file)
            ```
        """
        endpoint = "panel/api/server/getWebCertFiles"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting web certificate files...")

        response = self._get(url, headers)
        return WebCertFiles.model_validate(response.json().get(ApiFields.OBJ))

    def get_cert_hash(
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

            api = py3xui.Api.from_env()
            api.login()

            print(api.server.get_cert_hash(cert_file="/root/cert/fullchain.pem"))
            ```
        """
        endpoint = "panel/api/server/getCertHash"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting certificate hash...")

        data = {"certFile": cert_file, "certContent": cert_content}
        response = self._post_form(url, headers, data)
        return response.json().get(ApiFields.OBJ) or []

    def get_remote_cert_hash(self, server: str, allow_private: bool = False) -> list[str]:
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

            api = py3xui.Api.from_env()
            api.login()

            print(api.server.get_remote_cert_hash("cloudflare-dns.com"))
            ```
        """
        endpoint = "panel/api/server/getRemoteCertHash"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting certificate hash of %s...", server)

        data = {"server": server, "allowPrivate": allow_private}
        response = self._post_form(url, headers, data)
        return response.json().get(ApiFields.OBJ) or []

    def scan_reality_target(
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

            api = py3xui.Api.from_env()
            api.login()

            result = api.server.scan_reality_target("www.cloudflare.com:443")
            print(result.feasible, result.reason)
            ```
        """
        endpoint = "panel/api/server/scanRealityTarget"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Scanning REALITY target %s...", target)

        data = {"target": target, "sni": sni, "xver": xver, "allowPrivate": allow_private}
        response = self._post_form(url, headers, data)
        return RealityScanResult.model_validate(response.json().get(ApiFields.OBJ))

    def scan_reality_targets(self, targets: list[str] | None = None) -> list[RealityScanResult]:
        """Probes several candidate REALITY targets.

        Arguments:
            targets (list[str] | None): The targets: domain[:port], IP[:port] or CIDR. The
                candidates from the panel settings are probed when it is not set.

        Returns:
            list[RealityScanResult]: The verdicts ranked by feasibility, then by latency.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            targets = ["www.cloudflare.com", "104.16.0.0/24"]
            for result in api.server.scan_reality_targets(targets):
                print(result.target, result.feasible)
            ```
        """
        endpoint = "panel/api/server/scanRealityTargets"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Scanning REALITY targets...")

        data = {"targets": ",".join(targets) if targets else None}
        response = self._post_form(url, headers, data)
        results_json = response.json().get(ApiFields.OBJ) or []
        return [RealityScanResult.model_validate(result) for result in results_json]

    def get_logs(self, count: int, level: str = "info", syslog: bool = False) -> list[str]:
        """Gets the last lines of the panel log.

        Arguments:
            count (int): The number of lines to return.
            level (str): The minimum level: debug, info, notice, warning or err.
            syslog (bool): Whether to read the system journal instead of the panel log.

        Returns:
            list[str]: The log lines.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            for line in api.server.get_logs(100, level="warning"):
                print(line)
            ```
        """
        endpoint = f"panel/api/server/logs/{count}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting %s lines of the panel log...", count)

        response = self._post_form(url, headers, {"level": level, "syslog": syslog})
        return response.json().get(ApiFields.OBJ) or []

    def get_xray_logs(
        self,
        count: int,
        keyword: str = "",
        show_direct: bool = True,
        show_blocked: bool = True,
        show_proxy: bool = True,
    ) -> list[XrayLogEntry]:  # pylint: disable=R0913, R0917
        """Gets the last lines of the Xray access log.

        Arguments:
            count (int): The number of lines to return.
            keyword (str): Returns only the lines that contain this string.
            show_direct (bool): Whether to include the direct traffic.
            show_blocked (bool): Whether to include the blocked traffic.
            show_proxy (bool): Whether to include the proxied traffic.

        Returns:
            list[XrayLogEntry]: The log lines. The list is empty when the access log is disabled.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            for entry in api.server.get_xray_logs(100, show_direct=False):
                print(entry.date_time, entry.email, entry.to_address)
            ```
        """
        endpoint = f"panel/api/server/xraylogs/{count}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting %s lines of the Xray log...", count)

        data = {
            "filter": keyword,
            "showDirect": show_direct,
            "showBlocked": show_blocked,
            "showProxy": show_proxy,
        }
        response = self._post_form(url, headers, data)
        entries_json = response.json().get(ApiFields.OBJ) or []
        return [XrayLogEntry.model_validate(entry) for entry in entries_json]

    def get_amneziawg_logs(self, count: int, keyword: str = "") -> AmneziaWGLogs:
        """Gets the live AmneziaWG activity and the AmneziaWG lines of the panel log.

        Arguments:
            count (int): The maximum number of peers and of log lines to return.
            keyword (str): Returns only the peers and the lines that contain this string.

        Returns:
            AmneziaWGLogs: The AmneziaWG activity.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            logs = api.server.get_amneziawg_logs(100)
            print(logs.running, len(logs.peers), len(logs.events))
            ```
        """
        endpoint = f"panel/api/server/amneziawglogs/{count}"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting %s lines of the AmneziaWG log...", count)

        response = self._post_form(url, headers, {"filter": keyword})
        return AmneziaWGLogs.model_validate(response.json().get(ApiFields.OBJ))

    def get_migration(self, save_path: str) -> None:
        """Retrieves a cross-engine migration file and saves it to a specified path: a .dump file
        on a SQLite panel, a .db file on a PostgreSQL panel.

        Arguments:
            save_path (str): The path to save the migration file.

        Raises:
            ValueError: If the panel reports that the file could not be created.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.server.get_migration("migration.dump")
            ```
        """
        endpoint = "panel/api/server/getMigration"
        headers = {"Accept": "application/octet-stream"}
        url = self._url(endpoint)
        self.logger.info("Getting migration file...")

        response = self._get(url, headers, skip_check=True)

        # The panel reports a failure as a JSON response with the status code 200.
        if "application/json" in response.headers.get("Content-Type", ""):
            self._check_response(response)

        with open(save_path, "wb") as file:
            file.write(response.content)
        self.logger.info("Migration file saved to %s", save_path)

    def import_db(self, file_path: str, keep_host_settings: bool = True) -> None:
        """Restores the panel database from a backup or migration file. This replaces all the panel
        data, the panel restarts after the restore.

        Arguments:
            file_path (str): The path to the file to upload.
            keep_host_settings (bool): Whether to keep the listen addresses, certificates and node
                identity of this machine. Pass False to clone another machine wholesale.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.server.import_db("db_backup.db")
            ```
        """
        endpoint = "panel/api/server/importDB"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Importing DB from %s...", file_path)

        with open(file_path, "rb") as file:
            content = file.read()

        files = {"db": (os.path.basename(file_path), content)}
        self._post_form(url, headers, {"keepHostSettings": keep_host_settings}, files=files)
        self.logger.info("DB imported successfully.")

    def get_descendants(self) -> list[NodeSummary]:
        """Gets the read-only summaries of the nodes managed by the panel.

        Returns:
            list[NodeSummary]: The summaries of the nodes.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            for node in api.server.get_descendants():
                print(node.name, node.status)
            ```
        """
        endpoint = "panel/api/server/descendants"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting node descendants...")

        response = self._get(url, headers)
        nodes_json = response.json().get(ApiFields.OBJ) or []
        return [NodeSummary.model_validate(node) for node in nodes_json]

    def get_client_ips(self) -> list[InboundClientIps]:
        """Gets the recently active IP addresses of all the clients.

        Returns:
            list[InboundClientIps]: The IP addresses by client.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            for record in api.server.get_client_ips():
                print(record.client_email, record.ips)
            ```
        """
        endpoint = "panel/api/server/clientIps"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting client IPs...")

        response = self._get(url, headers)
        records_json = response.json().get(ApiFields.OBJ) or []
        return [InboundClientIps.model_validate(record) for record in records_json]

    def push_client_ips(self, client_ips: list[InboundClientIps]) -> None:
        """Merges recently active IP addresses into the panel database. The panel ignores the
        entries that were last seen more than 30 minutes ago.

        Arguments:
            client_ips (list[InboundClientIps]): The IP addresses by client.

        Examples:
            ```python
            import time

            import py3xui
            from py3xui.server import InboundClientIpEntry, InboundClientIps

            api = py3xui.Api.from_env()
            api.login()

            entry = InboundClientIpEntry(ip="192.0.2.10", timestamp=int(time.time()))
            record = InboundClientIps(client_email="alice@example.com", ips=[entry])
            api.server.push_client_ips([record])
            ```
        """
        endpoint = "panel/api/server/clientIps"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Pushing IPs of %s clients...", len(client_ips))

        data = [record.model_dump(by_alias=True, exclude_defaults=True) for record in client_ips]
        self._post(url, headers, data)  # type: ignore[arg-type]
        self.logger.info("Client IPs pushed successfully.")
