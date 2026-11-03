"""This module contains the NodeApi class for handling remote nodes in the XUI API."""

# pylint: disable=R0801
from typing import Any
from urllib.parse import quote

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.node import (
    Node,
    NodeFields,
    NodeHistoryPoint,
    NodeProbeResult,
    NodeRemoteInbound,
    NodeUpdateResult,
    NodeWebCertFiles,
)


class NodeApi(BaseApi):
    """This class provides methods to interact with the remote nodes in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_list: Retrieves all nodes.
        get_by_id: Retrieves a node by its ID.
        get_web_cert_files: Retrieves the web TLS certificate file paths of a node.
        add: Adds a new node.
        update: Updates a node.
        delete: Deletes a node.
        set_enable: Enables or disables a node.
        test: Probes the connection details of a node without saving them.
        get_cert_fingerprint: Retrieves the certificate fingerprint of a node.
        get_remote_inbounds: Retrieves the inbounds of a remote panel.
        probe: Probes a saved node and updates its cached state.
        update_panel: Triggers the panel self-update on nodes.
        get_history: Retrieves the aggregated history of a node metric.
        get_mtls_ca: Retrieves the CA certificate used to authenticate on nodes.
        set_mtls_trust_ca: Sets the CA certificate trusted for incoming node requests.
        reload_mtls_client: Reloads the stored mTLS client certificate.

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()
        api.login()

        nodes: list[py3xui.Node] = api.node.get_list()
        ```
    """

    def get_list(self) -> list[Node]:
        """Retrieves all nodes, including the read-only sub-nodes of the node tree.

        Returns:
            list[Node]: The list of nodes.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            nodes: list[py3xui.Node] = api.node.get_list()
            ```
        """
        endpoint = "panel/api/nodes/list"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting nodes...")

        response = self._get(url, headers)

        nodes_json = response.json().get(ApiFields.OBJ) or []
        return [Node.model_validate(data) for data in nodes_json]

    def get_by_id(self, node_id: int) -> Node:
        """Retrieves a node by its ID.

        Arguments:
            node_id (int): The ID of the node.

        Returns:
            Node: The node.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            node: py3xui.Node = api.node.get_by_id(1)
            ```
        """
        endpoint = f"panel/api/nodes/get/{node_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting node by ID: %s", node_id)

        response = self._get(url, headers)

        return Node.model_validate(response.json().get(ApiFields.OBJ))

    def get_web_cert_files(self, node_id: int) -> NodeWebCertFiles:
        """Retrieves the paths of the web TLS certificate files that exist on the node.
        The request is proxied to the node, the node must be enabled.

        Arguments:
            node_id (int): The ID of the node.

        Returns:
            NodeWebCertFiles: The paths of the certificate and key files.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            files = api.node.get_web_cert_files(1)
            print(files.web_cert_file, files.web_key_file)
            ```
        """
        endpoint = f"panel/api/nodes/webCert/{node_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting web certificate files of node: %s", node_id)

        response = self._get(url, headers)

        return NodeWebCertFiles.model_validate(response.json().get(ApiFields.OBJ))

    def add(self, node: Node) -> Node:
        """Adds a new node. The panel checks that the node is reachable before saving it.
        `api_token` is required unless `tls_verify_mode` is `mtls`.

        Arguments:
            node (Node): The node to add.

        Returns:
            Node: The created node. It does not contain the API token.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            node = py3xui.Node(
                name="de-fra-1",
                address="node1.example.com",
                port=2053,
                enable=True,
                api_token="token",
            )
            created: py3xui.Node = api.node.add(node)
            ```
        """
        endpoint = "panel/api/nodes/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = node.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Adding node: %s", node.name)

        response = self._post(url, headers, data)

        return Node.model_validate(response.json().get(ApiFields.OBJ))

    def update(self, node_id: int, node: Node) -> None:
        """Updates a node. The panel replaces the node with the given one, so pass a node read
        from the panel with the fields changed. The API token is never returned by the panel and
        stays untouched unless `api_token` or `clear_api_token` is set.

        Arguments:
            node_id (int): The ID of the node to update.
            node (Node): The new state of the node.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            node = api.node.get_by_id(1)
            node.remark = "Primary edge"
            api.node.update(node.id, node)
            ```
        """
        endpoint = f"panel/api/nodes/update/{node_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = node.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Updating node: %s", node_id)

        self._post(url, headers, data)
        self.logger.info("Node updated successfully.")

    def delete(self, node_id: int) -> None:
        """Deletes a node. The inbounds bound to it are not migrated automatically.

        Arguments:
            node_id (int): The ID of the node to delete.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.node.delete(1)
            ```
        """
        endpoint = f"panel/api/nodes/del/{node_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Deleting node: %s", node_id)

        self._post(url, headers, data)
        self.logger.info("Node deleted successfully.")

    def set_enable(self, node_id: int, enable: bool) -> None:
        """Enables or disables a node.

        Arguments:
            node_id (int): The ID of the node.
            enable (bool): Whether the node should be enabled.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.node.set_enable(1, False)
            ```
        """
        endpoint = f"panel/api/nodes/setEnable/{node_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {NodeFields.ENABLE: enable}
        self.logger.info("Setting enable=%s for node: %s", enable, node_id)

        self._post(url, headers, data)

    def test(self, node: Node) -> NodeProbeResult:
        """Probes the connection details of a node without saving them. For a node with an ID
        and without `api_token` the panel uses the stored token. A failed probe does not raise:
        check `status` and `error` of the result.

        Arguments:
            node (Node): The node to probe.

        Returns:
            NodeProbeResult: The result of the probe.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            node = py3xui.Node(
                name="de-fra-1",
                address="node1.example.com",
                port=2053,
                enable=True,
                api_token="token",
            )
            result: py3xui.NodeProbeResult = api.node.test(node)
            ```
        """
        endpoint = "panel/api/nodes/test"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = node.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Testing node: %s", node.name)

        response = self._post(url, headers, data)

        return NodeProbeResult.model_validate(response.json().get(ApiFields.OBJ))

    def get_cert_fingerprint(self, node: Node) -> str:
        """Connects to the node over HTTPS without verifying its certificate and retrieves the
        fingerprint of the leaf certificate, to use as `pinned_cert_sha256`.

        Arguments:
            node (Node): The node to connect to.

        Returns:
            str: The base64 SHA-256 of the certificate.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            node = py3xui.Node(
                name="de-fra-1", address="node1.example.com", port=2053, enable=True
            )
            fingerprint: str = api.node.get_cert_fingerprint(node)
            ```
        """
        endpoint = "panel/api/nodes/certFingerprint"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = node.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Getting certificate fingerprint of node: %s", node.name)

        response = self._post(url, headers, data)

        return response.json().get(ApiFields.OBJ)

    def get_remote_inbounds(self, node: Node) -> list[NodeRemoteInbound]:
        """Retrieves the inbounds of a remote panel available for the selective import. For a
        node with an ID and without `api_token` the panel uses the stored token.

        Arguments:
            node (Node): The connection details of the remote panel.

        Returns:
            list[NodeRemoteInbound]: The inbounds of the remote panel.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            node = py3xui.Node(
                name="de-fra-1",
                address="node1.example.com",
                port=2053,
                enable=True,
                api_token="token",
            )
            inbounds = api.node.get_remote_inbounds(node)
            ```
        """
        endpoint = "panel/api/nodes/inbounds"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = node.model_dump(by_alias=True, exclude_defaults=True)
        self.logger.info("Getting remote inbounds of node: %s", node.name)

        response = self._post(url, headers, data)

        inbounds_json = response.json().get(ApiFields.OBJ) or []
        return [NodeRemoteInbound.model_validate(item) for item in inbounds_json]

    def probe(self, node_id: int) -> NodeProbeResult:
        """Probes a saved node and updates its cached state. A failed probe does not raise:
        check `status` and `error` of the result.

        Arguments:
            node_id (int): The ID of the node.

        Returns:
            NodeProbeResult: The result of the probe.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            result: py3xui.NodeProbeResult = api.node.probe(1)
            ```
        """
        endpoint = f"panel/api/nodes/probe/{node_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Probing node: %s", node_id)

        response = self._post(url, headers, data)

        return NodeProbeResult.model_validate(response.json().get(ApiFields.OBJ))

    def update_panel(self, node_ids: list[int], dev: bool = False) -> list[NodeUpdateResult]:
        """Triggers the panel self-update on the given nodes. Only enabled and online nodes are
        updated, the others are reported in the result.

        Arguments:
            node_ids (list[int]): The IDs of the nodes, at least one.
            dev (bool): Whether to move the nodes to the rolling dev channel instead of the
                latest stable release.

        Returns:
            list[NodeUpdateResult]: The result for each node.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            results = api.node.update_panel([1, 2])
            ```
        """
        endpoint = "panel/api/nodes/updatePanel"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {NodeFields.IDS: node_ids, NodeFields.DEV: dev}
        self.logger.info("Updating panel on nodes: %s", node_ids)

        response = self._post(url, headers, data)

        results_json = response.json().get(ApiFields.OBJ) or []
        return [NodeUpdateResult.model_validate(item) for item in results_json]

    def get_history(self, node_id: int, metric: str, bucket: int) -> list[NodeHistoryPoint]:
        """Retrieves the aggregated history of a node metric (up to 60 points).

        Arguments:
            node_id (int): The ID of the node.
            metric (str): `cpu`, `mem`, `netUp` or `netDown`.
            bucket (int): The bucket size in seconds: 2, 30, 60, 180, 360, 720, 1440, 2880
                or 10080.

        Returns:
            list[NodeHistoryPoint]: The points of the history.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            points = api.node.get_history(1, "cpu", 60)
            ```
        """
        endpoint = f"panel/api/nodes/history/{node_id}/{quote(metric, safe='')}/{bucket}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting %s history of node: %s", metric, node_id)

        response = self._get(url, headers)

        points_json = response.json().get(ApiFields.OBJ) or []
        return [NodeHistoryPoint.model_validate(point) for point in points_json]

    def get_mtls_ca(self) -> str:
        """Retrieves the CA certificate this panel uses to authenticate on nodes, to paste into
        the mTLS trust setting of a node. The panel creates the CA on the first call.

        Returns:
            str: The CA certificate in the PEM format.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            ca_cert: str = api.node.get_mtls_ca()
            ```
        """
        endpoint = "panel/api/nodes/mtls/ca"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Getting node mTLS CA certificate...")

        response = self._post(url, headers, data)

        return response.json().get(ApiFields.OBJ).get(NodeFields.CA_CERT)

    def set_mtls_trust_ca(self, ca_cert: str) -> None:
        """Sets the CA certificate this panel trusts for incoming node requests, when this panel
        acts as a node. Applied on the next panel restart.

        Arguments:
            ca_cert (str): The CA certificate of the managing panel in the PEM format. An empty
                string disables the mTLS trust.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.node.set_mtls_trust_ca("-----BEGIN CERTIFICATE-----...")
            ```
        """
        endpoint = "panel/api/nodes/mtls/trustCA"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = {NodeFields.CA_CERT: ca_cert}
        self.logger.info("Setting node mTLS trusted CA certificate...")

        self._post(url, headers, data)

    def reload_mtls_client(self) -> None:
        """Validates the stored mTLS client certificate and closes the cached connections, so the
        next requests to the nodes present the new certificate.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.node.reload_mtls_client()
            ```
        """
        endpoint = "panel/api/nodes/mtls/reloadClient"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        self.logger.info("Reloading node mTLS client certificate...")

        self._post(url, headers, data)
