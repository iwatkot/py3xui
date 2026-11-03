"""This module contains the models of the remote nodes in the XUI API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# pylint: disable=too-few-public-methods
class NodeFields:
    """Stores the fields used by the XUI API for parsing and building node requests."""

    ID = "id"
    NAME = "name"
    REMARK = "remark"
    SCHEME = "scheme"
    ADDRESS = "address"
    PORT = "port"
    BASE_PATH = "basePath"
    ENABLE = "enable"
    ALLOW_PRIVATE_ADDRESS = "allowPrivateAddress"

    API_TOKEN = "apiToken"
    CLEAR_API_TOKEN = "clearApiToken"
    HAS_API_TOKEN = "hasApiToken"

    TLS_VERIFY_MODE = "tlsVerifyMode"
    PINNED_CERT_SHA256 = "pinnedCertSha256"
    INBOUND_SYNC_MODE = "inboundSyncMode"
    INBOUND_TAGS = "inboundTags"
    OUTBOUND_TAG = "outboundTag"

    GUID = "guid"
    PARENT_GUID = "parentGuid"
    TRANSITIVE = "transitive"

    STATUS = "status"
    LAST_HEARTBEAT = "lastHeartbeat"
    LATENCY_MS = "latencyMs"
    XRAY_VERSION = "xrayVersion"
    PANEL_VERSION = "panelVersion"
    CPU_PCT = "cpuPct"
    MEM_PCT = "memPct"
    UPTIME_SECS = "uptimeSecs"
    UNAVAILABLE_METRICS = "unavailableMetrics"
    NET_UP = "netUp"
    NET_DOWN = "netDown"
    LAST_ERROR = "lastError"
    XRAY_STATE = "xrayState"
    XRAY_ERROR = "xrayError"

    CONFIG_DIRTY = "configDirty"
    CONFIG_DIRTY_AT = "configDirtyAt"

    INBOUND_COUNT = "inboundCount"
    CLIENT_COUNT = "clientCount"
    ONLINE_COUNT = "onlineCount"
    ACTIVE_COUNT = "activeCount"
    DISABLED_COUNT = "disabledCount"
    DEPLETED_COUNT = "depletedCount"

    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"

    CA_CERT = "caCert"
    IDS = "ids"
    DEV = "dev"

    WEB_CERT_FILE = "webCertFile"
    WEB_KEY_FILE = "webKeyFile"


class Node(BaseModel):
    """Represents a remote panel registered as a node.

    The same model is read from and sent to the panel. All optional fields default to the zero
    value of the panel, because the requests are built with `exclude_defaults=True`: an omitted
    field and a field with the default value mean the same thing to the panel.

    Attributes:
        name (str): The name of the node. Required.
        address (str): The host of the node. Required.
        port (int): The port of the node, from 1 to 65535. Required.
        enable (bool): Whether the node is enabled. Required.
        id (int): The ID of the node, 0 for a node that is not saved.
        remark (str): The remark of the node.
        scheme (str): `http` or `https`. The panel uses `https` when empty.
        base_path (str): The base path of the node panel. The panel uses `/` when empty.
        api_token (str | None): The new API token, write-only: the panel never returns it, and
            `None` keeps the stored token on update.
        clear_api_token (bool): Removes the stored API token on update. Cannot be used together
            with `api_token`.
        has_api_token (bool): Whether the node has an API token. Read-only.
        allow_private_address (bool): Whether a private address is allowed for the node.
        tls_verify_mode (str): `verify`, `skip`, `pin` or `mtls`. The panel uses `verify` when
            empty.
        pinned_cert_sha256 (str): The base64 SHA-256 of the pinned certificate.
        inbound_sync_mode (str): `all` or `selected`. The panel uses `all` when empty.
        inbound_tags (list[str]): The tags of the synchronized inbounds in the `selected` mode.
        outbound_tag (str): The outbound used to reach the node.
        guid (str): The stable ID of the remote panel. Read-only.
        parent_guid (str): The GUID of the parent in a node tree. Read-only.
        transitive (bool): Whether it is a read-only sub-node of another node. Read-only.
        status (str): `online`, `offline` or `unknown`. Read-only.
        last_heartbeat (int): The Unix time of the last heartbeat, 0 if never. Read-only.
        latency_ms (int): The latency in milliseconds. Read-only.
        xray_version (str): The Xray version of the node. Read-only.
        panel_version (str): The panel version of the node. Read-only.
        cpu_pct (float): The CPU usage in percent. Read-only.
        mem_pct (float): The memory usage in percent. Read-only.
        uptime_secs (int): The uptime in seconds. Read-only.
        unavailable_metrics (list[str]): The metrics the node did not report. Read-only.
        net_up (int): The upload speed. Read-only.
        net_down (int): The download speed. Read-only.
        last_error (str): The last error of the node. Read-only.
        xray_state (str): The state of the Xray core of the node. Read-only.
        xray_error (str): The error of the Xray core of the node. Read-only.
        config_dirty (bool): Whether the node has unsynchronized changes. Read-only.
        config_dirty_at (int): The Unix time of the first such change. Read-only.
        inbound_count (int): The number of inbounds. Read-only.
        client_count (int): The number of clients. Read-only.
        online_count (int): The number of online clients. Read-only.
        active_count (int): The number of active clients. Read-only.
        disabled_count (int): The number of disabled clients. Read-only.
        depleted_count (int): The number of depleted clients. Read-only.
        created_at (int): The Unix time of creation. Read-only.
        updated_at (int): The Unix time of the last update. Read-only.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    name: str
    address: str
    port: int
    enable: bool

    id: int = 0
    remark: str = ""
    scheme: str = ""
    base_path: str = Field(default="", alias=NodeFields.BASE_PATH)  # type: ignore

    api_token: str | None = Field(  # type: ignore
        default=None, alias=NodeFields.API_TOKEN, repr=False
    )
    clear_api_token: bool = Field(default=False, alias=NodeFields.CLEAR_API_TOKEN)  # type: ignore
    has_api_token: bool = Field(default=False, alias=NodeFields.HAS_API_TOKEN)  # type: ignore

    allow_private_address: bool = Field(  # type: ignore
        default=False, alias=NodeFields.ALLOW_PRIVATE_ADDRESS
    )
    tls_verify_mode: str = Field(default="", alias=NodeFields.TLS_VERIFY_MODE)  # type: ignore
    pinned_cert_sha256: str = Field(  # type: ignore
        default="", alias=NodeFields.PINNED_CERT_SHA256
    )
    inbound_sync_mode: str = Field(default="", alias=NodeFields.INBOUND_SYNC_MODE)  # type: ignore
    inbound_tags: list[str] = Field(  # type: ignore
        default_factory=list, alias=NodeFields.INBOUND_TAGS
    )
    outbound_tag: str = Field(default="", alias=NodeFields.OUTBOUND_TAG)  # type: ignore

    guid: str = ""
    parent_guid: str = Field(default="", alias=NodeFields.PARENT_GUID)  # type: ignore
    transitive: bool = False

    status: str = ""
    last_heartbeat: int = Field(default=0, alias=NodeFields.LAST_HEARTBEAT)  # type: ignore
    latency_ms: int = Field(default=0, alias=NodeFields.LATENCY_MS)  # type: ignore
    xray_version: str = Field(default="", alias=NodeFields.XRAY_VERSION)  # type: ignore
    panel_version: str = Field(default="", alias=NodeFields.PANEL_VERSION)  # type: ignore
    cpu_pct: float = Field(default=0.0, alias=NodeFields.CPU_PCT)  # type: ignore
    mem_pct: float = Field(default=0.0, alias=NodeFields.MEM_PCT)  # type: ignore
    uptime_secs: int = Field(default=0, alias=NodeFields.UPTIME_SECS)  # type: ignore
    unavailable_metrics: list[str] = Field(  # type: ignore
        default_factory=list, alias=NodeFields.UNAVAILABLE_METRICS
    )
    net_up: int = Field(default=0, alias=NodeFields.NET_UP)  # type: ignore
    net_down: int = Field(default=0, alias=NodeFields.NET_DOWN)  # type: ignore
    last_error: str = Field(default="", alias=NodeFields.LAST_ERROR)  # type: ignore
    xray_state: str = Field(default="", alias=NodeFields.XRAY_STATE)  # type: ignore
    xray_error: str = Field(default="", alias=NodeFields.XRAY_ERROR)  # type: ignore

    config_dirty: bool = Field(default=False, alias=NodeFields.CONFIG_DIRTY)  # type: ignore
    config_dirty_at: int = Field(default=0, alias=NodeFields.CONFIG_DIRTY_AT)  # type: ignore

    inbound_count: int = Field(default=0, alias=NodeFields.INBOUND_COUNT)  # type: ignore
    client_count: int = Field(default=0, alias=NodeFields.CLIENT_COUNT)  # type: ignore
    online_count: int = Field(default=0, alias=NodeFields.ONLINE_COUNT)  # type: ignore
    active_count: int = Field(default=0, alias=NodeFields.ACTIVE_COUNT)  # type: ignore
    disabled_count: int = Field(default=0, alias=NodeFields.DISABLED_COUNT)  # type: ignore
    depleted_count: int = Field(default=0, alias=NodeFields.DEPLETED_COUNT)  # type: ignore

    created_at: int = Field(default=0, alias=NodeFields.CREATED_AT)  # type: ignore
    updated_at: int = Field(default=0, alias=NodeFields.UPDATED_AT)  # type: ignore

    @field_validator("inbound_tags", mode="before")
    @classmethod
    def _none_to_empty_list(cls, value: Any) -> Any:
        """The panel sends `null` instead of an empty list for the `all` synchronization mode."""
        return [] if value is None else value


class NodeProbeResult(BaseModel):
    """Represents the result of a node probe. An unreachable node is a successful response with
    the `offline` status and the reason in `error`.

    Attributes:
        status (str): `online` or `offline`.
        latency_ms (int): The latency in milliseconds.
        xray_version (str): The Xray version of the node.
        panel_version (str): The panel version of the node.
        cpu_pct (float): The CPU usage in percent.
        mem_pct (float): The memory usage in percent.
        uptime_secs (int): The uptime in seconds.
        unavailable_metrics (list[str]): The metrics the node did not report.
        error (str): The reason of the failed probe.
        xray_state (str): The state of the Xray core of the node.
        xray_error (str): The error of the Xray core of the node.
    """

    model_config = ConfigDict(populate_by_name=True)

    status: str
    latency_ms: int = Field(default=0, alias=NodeFields.LATENCY_MS)  # type: ignore
    xray_version: str = Field(default="", alias=NodeFields.XRAY_VERSION)  # type: ignore
    panel_version: str = Field(default="", alias=NodeFields.PANEL_VERSION)  # type: ignore
    cpu_pct: float = Field(default=0.0, alias=NodeFields.CPU_PCT)  # type: ignore
    mem_pct: float = Field(default=0.0, alias=NodeFields.MEM_PCT)  # type: ignore
    uptime_secs: int = Field(default=0, alias=NodeFields.UPTIME_SECS)  # type: ignore
    unavailable_metrics: list[str] = Field(  # type: ignore
        default_factory=list, alias=NodeFields.UNAVAILABLE_METRICS
    )
    error: str = ""
    xray_state: str = Field(default="", alias=NodeFields.XRAY_STATE)  # type: ignore
    xray_error: str = Field(default="", alias=NodeFields.XRAY_ERROR)  # type: ignore


class NodeUpdateResult(BaseModel):
    """Represents the result of triggering the panel self-update on one node.

    Attributes:
        id (int): The ID of the node.
        name (str): The name of the node, empty if the node was not found.
        ok (bool): Whether the update was started.
        error (str): The reason why the update was not started.
    """

    id: int
    name: str = ""
    ok: bool = False
    error: str = ""


class NodeRemoteInbound(BaseModel):
    """Represents an inbound of a remote panel available for the selective import.

    Attributes:
        id (int): The ID of the inbound on the remote panel.
        tag (str): The tag of the inbound.
        remark (str): The remark of the inbound.
        listen (str): The listen address of the inbound.
        protocol (str): The protocol of the inbound.
        port (int): The port of the inbound.
    """

    id: int = 0
    tag: str
    remark: str = ""
    listen: str = ""
    protocol: str = ""
    port: int = 0


class NodeWebCertFiles(BaseModel):
    """Represents the paths of the web TLS certificate files on the node.

    Attributes:
        web_cert_file (str): The path of the certificate file.
        web_key_file (str): The path of the key file.
    """

    model_config = ConfigDict(populate_by_name=True)

    web_cert_file: str = Field(default="", alias=NodeFields.WEB_CERT_FILE)  # type: ignore
    web_key_file: str = Field(default="", alias=NodeFields.WEB_KEY_FILE)  # type: ignore


class NodeHistoryPoint(BaseModel):
    """Represents one aggregated point of a node metric history.

    Attributes:
        t (int): The start of the bucket, Unix time in seconds.
        v (float): The mean value of the metric in the bucket.
    """

    t: int
    v: float
