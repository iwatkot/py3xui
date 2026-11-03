"""This module contains the Client class which represents a client in the XUI API."""

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


# pylint: disable=too-few-public-methods
class ClientFields:
    """Stores the fields returned by the XUI API for parsing."""

    EMAIL = "email"
    ENABLE = "enable"
    PASSWORD = "password"

    ID = "id"
    INBOUND_ID = "inboundId"

    UP = "up"
    DOWN = "down"

    EXPIRY_TIME = "expiryTime"

    TOTAL = "total"
    RESET = "reset"

    FLOW = "flow"
    METHOD = "method"
    LIMIT_IP = "limitIp"
    SUB_ID = "subId"
    COMMENT = "comment"
    TG_ID = "tgId"
    TOTAL_GB = "totalGB"

    UUID = "uuid"

    GROUP = "group"
    SECURITY = "security"
    AUTH = "auth"
    SECRET = "secret"
    AD_TAG = "adTag"
    REVERSE = "reverse"

    PRIVATE_KEY = "privateKey"
    PUBLIC_KEY = "publicKey"
    PRE_SHARED_KEY = "preSharedKey"
    ALLOWED_IPS = "allowedIPs"
    ALLOWED_IPS_BY_INBOUND = "allowedIPsByInbound"
    KEEP_ALIVE = "keepAlive"
    FORWARDED_PORTS = "forwardedPorts"

    CLIENT_HOST_RULE_IDS = "clientHostRuleIds"
    LIMIT_HWID = "limitHwid"

    RESET_DAY = "resetDay"
    RESET_WEEKDAY = "resetWeekday"
    RESET_MAX = "resetMax"
    TRAFFIC_RESET = "trafficReset"
    TRAFFIC_RESET_DAY = "trafficResetDay"

    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    CREATED_AT_RECORD = "createdAt"
    UPDATED_AT_RECORD = "updatedAt"

    CLIENT = "client"
    INBOUND_IDS = "inboundIds"
    EXTERNAL_LINKS = "externalLinks"
    USED_TRAFFIC = "usedTraffic"
    TUNNEL_ALLOWED_IPS = "tunnelAllowedIPs"

    TRAFFIC = "traffic"
    RESET_COUNT = "resetCount"
    LAST_ONLINE = "lastOnline"
    LAST_SUB_FETCH = "lastSubFetch"

    KIND = "kind"
    VALUE = "value"
    REMARK = "remark"
    NAME_PREFIX = "namePrefix"
    CLIENT_ID = "clientId"
    LAST_FETCH_AT = "lastFetchAt"
    LAST_FETCH_ERROR = "lastFetchError"
    SORT_INDEX = "sortIndex"


class Client(BaseModel):
    """Represents a client in the XUI API.

    Attributes:
        email (str): The email of the client. Required.
        enable (bool): Whether the client is enabled. Required.
        password (str): The password of the client. Optional.
        id (int | str): The ID of the client. Required.
        inbound_id (int | None): The ID of the inbound connection. Optional.
        up (int): The upload speed of the client. Optional.
        down (int): The download speed of the client. Optional.
        expiry_time (int): The expiry time of the client. Optional.
        total (int): The total amount of data transferred by the client. Optional.
        reset (int): The time at which the client's data was last reset. Optional.
        flow (str): The flow of the client. Optional.
        method (str): The method (encryption cipher) used by the client. Optional.
        limit_ip (int): The limit of IPs for the client. Optional.
        sub_id (str): The sub ID of the client. Optional.
        comment (str): The comment of the client. Optional.
        tg_id (str): The Telegram ID of the client. Optional.
        total_gb (int): The total amount of data transferred by the client in GB. Optional.
        uuid (str | None): The UUID of the client (record responses carry it here). Optional.
        group (str): The logical group label of the client. Optional.
        security (str): The VMess security method (e.g. "auto"). Optional.
        auth (str): The Hysteria auth password. Optional.
        secret (str): The MTProto secret. Optional.
        ad_tag (str): The MTProto ad tag. Optional.
        reverse (dict[str, Any] | None): The VLESS simple reverse proxy settings. Optional.
        private_key (str): The WireGuard / AmneziaWG private key. Optional.
        public_key (str): The WireGuard / AmneziaWG public key. Optional.
        pre_shared_key (str): The WireGuard / AmneziaWG pre-shared key. Optional.
        allowed_ips (list[str]): The WireGuard / AmneziaWG allowed IPs. A comma-separated
            string (as returned in client records) is split into a list. Optional.
        allowed_ips_by_inbound (dict[int, list[str]] | None): Per-inbound overrides of
            allowed IPs, keyed by inbound ID. Optional.
        keep_alive (int | str): The WireGuard / AmneziaWG keepalive (number or range).
            Left out of update requests when 0, so the panel preserves the stored value.
            Optional.
        forwarded_ports (str): The AmneziaWG port-forwarding spec. Optional.
        client_host_rule_ids (list[int] | None): The IDs of host rules bound to the client.
            Optional.
        limit_hwid (int): The limit of hardware IDs (devices) for the client. Optional.
        reset_day (int): The calendar renewal day 1-31, 0 disables monthly renewal. Optional.
        reset_weekday (int): The calendar weekday 1-7, 0 disables weekly renewal. Optional.
        reset_max (int): The maximum auto-renew count, 0 means unlimited. Optional.
        traffic_reset (str): The per-client traffic reset cycle. Optional.
        traffic_reset_day (int): The day of the traffic reset cycle. Optional.
        created_at (int): The creation timestamp in milliseconds. Optional.
        updated_at (int): The last update timestamp in milliseconds. Optional.

    Fields that are not declared above are kept as extra fields and sent back to the panel
    by `model_dump()`, so a "get -> modify -> update" cycle does not drop any client data.
    """

    email: str
    enable: bool
    id: int | str | None = Field(default=None)
    password: str = Field(default="")  # type: ignore

    inbound_id: int | None = Field(default=None, alias=ClientFields.INBOUND_ID)  # type: ignore

    up: int = 0
    down: int = 0

    expiry_time: int = Field(default=0, alias=ClientFields.EXPIRY_TIME)  # type: ignore

    total: int = 0
    reset: int | None = None

    flow: str = ""
    method: str = ""
    limit_ip: int = Field(default=0, alias=ClientFields.LIMIT_IP)  # type: ignore
    sub_id: str = Field(default="", alias=ClientFields.SUB_ID)  # type: ignore
    comment: str = Field(default="", alias=ClientFields.COMMENT)  # type: ignore
    tg_id: int | str | None = Field(default="", alias=ClientFields.TG_ID)  # type: ignore
    total_gb: int = Field(default=0, alias=ClientFields.TOTAL_GB)  # type: ignore
    uuid: str | None = Field(default=None, alias=ClientFields.UUID)  # type: ignore

    group: str = Field(default="", alias=ClientFields.GROUP)  # type: ignore
    security: str = Field(default="", alias=ClientFields.SECURITY)  # type: ignore
    auth: str = Field(default="", alias=ClientFields.AUTH)  # type: ignore
    secret: str = Field(default="", alias=ClientFields.SECRET)  # type: ignore
    ad_tag: str = Field(default="", alias=ClientFields.AD_TAG)  # type: ignore
    reverse: dict[str, Any] | None = Field(default=None, alias=ClientFields.REVERSE)  # type: ignore

    private_key: str = Field(default="", alias=ClientFields.PRIVATE_KEY)  # type: ignore
    public_key: str = Field(default="", alias=ClientFields.PUBLIC_KEY)  # type: ignore
    pre_shared_key: str = Field(default="", alias=ClientFields.PRE_SHARED_KEY)  # type: ignore
    allowed_ips: list[str] = Field(  # type: ignore
        default_factory=list, alias=ClientFields.ALLOWED_IPS
    )
    allowed_ips_by_inbound: dict[int, list[str]] | None = Field(  # type: ignore
        default=None, alias=ClientFields.ALLOWED_IPS_BY_INBOUND
    )
    keep_alive: int | str = Field(default=0, alias=ClientFields.KEEP_ALIVE)  # type: ignore
    forwarded_ports: str = Field(default="", alias=ClientFields.FORWARDED_PORTS)  # type: ignore

    client_host_rule_ids: list[int] | None = Field(  # type: ignore
        default=None, alias=ClientFields.CLIENT_HOST_RULE_IDS
    )
    limit_hwid: int = Field(default=0, alias=ClientFields.LIMIT_HWID)  # type: ignore

    reset_day: int = Field(default=0, alias=ClientFields.RESET_DAY)  # type: ignore
    reset_weekday: int = Field(default=0, alias=ClientFields.RESET_WEEKDAY)  # type: ignore
    reset_max: int = Field(default=0, alias=ClientFields.RESET_MAX)  # type: ignore
    traffic_reset: str = Field(default="", alias=ClientFields.TRAFFIC_RESET)  # type: ignore
    traffic_reset_day: int = Field(default=0, alias=ClientFields.TRAFFIC_RESET_DAY)  # type: ignore

    created_at: int = Field(  # type: ignore
        default=0,
        alias=ClientFields.CREATED_AT,
        validation_alias=AliasChoices(ClientFields.CREATED_AT, ClientFields.CREATED_AT_RECORD),
    )
    updated_at: int = Field(  # type: ignore
        default=0,
        alias=ClientFields.UPDATED_AT,
        validation_alias=AliasChoices(ClientFields.UPDATED_AT, ClientFields.UPDATED_AT_RECORD),
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @field_validator("reverse", mode="before")
    @classmethod
    def ignore_invalid_reverse(cls, value: Any) -> Any:
        """Treats a stored reverse value that is not a JSON object as absent, like the panel does
        when it converts a client record to a client."""
        return value if isinstance(value, dict) else None

    @field_validator("allowed_ips", mode="before")
    @classmethod
    def split_allowed_ips(cls, value: Any) -> Any:
        """Splits the comma-separated allowed IPs string returned in client records into a list,
        which is the shape the panel accepts on create and update."""
        if value is None:
            return []
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value


class ClientDetails(BaseModel):
    """Represents the full client payload returned by `panel/api/clients/get/{email}`.

    Attributes:
        client (Client): The client itself.
        inbound_ids (list[int]): The IDs of all inbounds the client is attached to.
        external_links (list[dict[str, Any]]): The external links of the client's subscription.
        used_traffic (int): The traffic used by the client (up + down), in bytes.
        tunnel_allowed_ips (dict[int, str]): The client's tunnel address for each WireGuard /
            AmneziaWG inbound, keyed by inbound ID.
    """

    client: Client = Field(alias=ClientFields.CLIENT)  # type: ignore
    inbound_ids: list[int] = Field(  # type: ignore
        default_factory=list, alias=ClientFields.INBOUND_IDS
    )
    external_links: list[dict[str, Any]] = Field(  # type: ignore
        default_factory=list, alias=ClientFields.EXTERNAL_LINKS
    )
    used_traffic: int = Field(default=0, alias=ClientFields.USED_TRAFFIC)  # type: ignore
    tunnel_allowed_ips: dict[int, str] = Field(  # type: ignore
        default_factory=dict, alias=ClientFields.TUNNEL_ALLOWED_IPS
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @field_validator("inbound_ids", "external_links", "tunnel_allowed_ips", mode="before")
    @classmethod
    def replace_null(cls, value: Any, info: Any) -> Any:
        """Replaces JSON null (nil slices and maps in the panel) with an empty container."""
        if value is None:
            return {} if info.field_name == "tunnel_allowed_ips" else []
        return value


class ClientExternalLink(BaseModel):
    """Represents an external link or subscription of a client. The panel merges these into the
    client's subscription.

    Attributes:
        kind (str): "link" for a single share link, "subscription" for a remote subscription URL.
        value (str): The share link or the subscription URL.
        remark (str): The node name that overrides the one in a share link. Optional.
        enable (bool | None): Whether the link is emitted in subscriptions; None means True.
            Optional.
        expiry_time (int): The expiry time of the link in milliseconds, 0 means none. Optional.
        name_prefix (str): The prefix of the node names of a subscription. Optional.
        id (int): The ID of the link. Ignored by the panel on write. Optional.
        client_id (int): The record ID of the client. Ignored by the panel on write. Optional.
        last_fetch_at (int): The last subscription fetch time. Read-only. Optional.
        last_fetch_error (str): The last subscription fetch error. Read-only. Optional.
        sort_index (int): The position of the link. Read-only. Optional.
        created_at (int): The creation time in milliseconds. Read-only. Optional.
    """

    kind: str
    value: str
    remark: str = ""
    enable: bool | None = None
    expiry_time: int = Field(default=0, alias=ClientFields.EXPIRY_TIME)  # type: ignore
    name_prefix: str = Field(default="", alias=ClientFields.NAME_PREFIX)  # type: ignore
    id: int = 0
    client_id: int = Field(default=0, alias=ClientFields.CLIENT_ID)  # type: ignore
    last_fetch_at: int = Field(default=0, alias=ClientFields.LAST_FETCH_AT)  # type: ignore
    last_fetch_error: str = Field(default="", alias=ClientFields.LAST_FETCH_ERROR)  # type: ignore
    sort_index: int = Field(default=0, alias=ClientFields.SORT_INDEX)  # type: ignore
    created_at: int = Field(default=0, alias=ClientFields.CREATED_AT_RECORD)  # type: ignore

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


class ClientEntryTraffic(BaseModel):
    """Represents the usage counters carried by a `ClientEntry`. On import, they are restored
    only for the clients that the import creates.

    Attributes:
        up (int): The uploaded traffic in bytes. Optional.
        down (int): The downloaded traffic in bytes. Optional.
        reset_count (int): The number of renewals already done. Optional.
        last_online (int): The last time the client was online, in milliseconds. Optional.
        last_sub_fetch (int): The last subscription fetch time, in milliseconds. Optional.
    """

    up: int = 0
    down: int = 0
    reset_count: int = Field(default=0, alias=ClientFields.RESET_COUNT)  # type: ignore
    last_online: int = Field(default=0, alias=ClientFields.LAST_ONLINE)  # type: ignore
    last_sub_fetch: int = Field(default=0, alias=ClientFields.LAST_SUB_FETCH)  # type: ignore

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


class ClientEntry(BaseModel):
    """Represents a client together with its inbounds: an item of `export_clients`, and the input
    of `import_clients` and `bulk_add`.

    Attributes:
        client (Client): The client.
        inbound_ids (list[int]): The IDs of the inbounds the client is attached to. Optional.
        traffic (ClientEntryTraffic | None): The usage counters of the client. Optional.
    """

    client: Client = Field(alias=ClientFields.CLIENT)  # type: ignore
    inbound_ids: list[int] = Field(  # type: ignore
        default_factory=list, alias=ClientFields.INBOUND_IDS
    )
    traffic: ClientEntryTraffic | None = Field(  # type: ignore
        default=None, alias=ClientFields.TRAFFIC
    )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @field_validator("inbound_ids", mode="before")
    @classmethod
    def replace_null(cls, value: Any) -> Any:
        """Replaces JSON null (a nil slice in the panel) with an empty list."""
        return [] if value is None else value
