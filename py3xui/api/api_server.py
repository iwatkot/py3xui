"""This module contains the ServerApi class for handling server in the XUI API."""

from py3xui.api.api_base import ApiFields
from py3xui.api.api_base import BaseApi
from py3xui.server.config import ServerConfig
from py3xui.server.config import XrayVersionUnavailableError
from py3xui.server.server import RealityKeyPair
from py3xui.server.server import Server
from py3xui.utils.endpoints import Endpoints


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
        endpoint = Endpoints.SERVER_GET_DB
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
        endpoint = Endpoints.SERVER_STATUS
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
        endpoint = Endpoints.SERVER_GET_NEW_X25519_CERT
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
        endpoint = Endpoints.SERVER_INSTALL_XRAY.format(version=version)
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Installing new Xray version %s...", version)

        response = self._post(url, headers, data={})

        if response.json().get(ApiFields.OBJ) is not None:  # If "obj" is not null, success
            self.logger.info("Xray version %s installed successfully.", version)
        else:
            self.logger.error("Failed to install Xray version %s.", version)
            raise ValueError(f"Failed to install Xray version {version}.")

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

        endpoint = Endpoints.SERVER_UPDATE_GEOFILE
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
        endpoint = Endpoints.SERVER_GET_XRAY_VERSION
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
        endpoint = Endpoints.SERVER_GET_CONFIG_JSON
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting server config...")

        response = self._get(url, headers)
        config_json = response.json().get(ApiFields.OBJ)

        if not config_json:
            raise ValueError("Server config was not returned by the server.")

        self.logger.debug("Server config: %s", config_json)
        return ServerConfig.model_validate(config_json)
