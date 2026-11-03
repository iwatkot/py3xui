"""This module contains the read-only models returned by the client endpoints of the XUI API:
traffic counters, paged client lists, renewal previews, bulk operation results, groups, devices
and IP records."""

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


# pylint: disable=too-few-public-methods
class ClientInfoFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    INBOUND_ID = "inboundId"
    ENABLE = "enable"
    EMAIL = "email"
    UUID = "uuid"
    SUB_ID = "subId"
    UP = "up"
    DOWN = "down"
    EXPIRY_TIME = "expiryTime"
    TOTAL = "total"
    TOTAL_GB = "totalGB"
    LIMIT_IP = "limitIp"
    LIMIT_HWID = "limitHwid"
    RESET = "reset"
    RESET_DAY = "resetDay"
    RESET_WEEKDAY = "resetWeekday"
    RESET_MAX = "resetMax"
    RESET_COUNT = "resetCount"
    LAST_ONLINE = "lastOnline"
    LAST_SUB_FETCH = "lastSubFetch"
    GROUP = "group"
    COMMENT = "comment"
    INBOUND_IDS = "inboundIds"
    TRAFFIC = "traffic"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"

    ACTIVE = "active"
    ONLINE = "online"
    ONLINE_COUNT = "onlineCount"
    DEPLETED = "depleted"
    DEPLETED_COUNT = "depletedCount"
    EXPIRING = "expiring"
    EXPIRING_COUNT = "expiringCount"
    DEACTIVE = "deactive"
    DEACTIVE_COUNT = "deactiveCount"

    ITEMS = "items"
    FILTERED = "filtered"
    PAGE = "page"
    PAGE_SIZE = "pageSize"
    SUMMARY = "summary"
    GROUPS = "groups"

    TIME_ZONE = "timeZone"
    RENEW_AT = "renewAt"
    VALID_THROUGH = "validThrough"
    NEXT_EXPIRY = "nextExpiry"
    SUGGESTED_EXPIRY_TIME = "suggestedExpiryTime"
    SUGGESTED_EXPIRY = "suggestedExpiry"
    RENEWALS = "renewals"
    CAN_RENEW = "canRenew"
    DELAYED_START = "delayedStart"

    REASON = "reason"
    CREATED = "created"
    ADJUSTED = "adjusted"
    DELETED = "deleted"
    CHANGED = "changed"
    SKIPPED = "skipped"

    NAME = "name"
    CLIENT_COUNT = "clientCount"
    TRAFFIC_USED = "trafficUsed"

    FIRST_SEEN = "firstSeen"
    LAST_SEEN = "lastSeen"
    USER_AGENT = "userAgent"
    DEVICE_OS = "deviceOs"
    OS_VERSION = "osVersion"
    DEVICE_MODEL = "deviceModel"
    FINGERPRINT = "fingerprint"
    IP = "ip"
    TIMESTAMP = "timestamp"


def _empty_list(value: Any) -> Any:
    """Replaces JSON null (a nil slice in the panel) with an empty list."""
    return [] if value is None else value


class ClientTraffic(BaseModel):
    """Represents the traffic counters of a client (`panel/api/clients/traffic/{email}`).

    Attributes:
        id (int): The ID of the traffic record.
        inbound_id (int): The ID of the inbound the record belongs to.
        enable (bool): Whether the client is enabled.
        email (str): The email of the client.
        uuid (str): The UUID (or password) of the client.
        sub_id (str): The subscription ID of the client.
        up (int): The uploaded traffic in bytes.
        down (int): The downloaded traffic in bytes.
        expiry_time (int): The expiry time in milliseconds, 0 means unlimited.
        total (int): The traffic limit in bytes, 0 means unlimited.
        reset (int): The auto-renew interval in days, 0 disables it.
        reset_day (int): The monthly renewal day 1-31, 0 disables it.
        reset_weekday (int): The weekly renewal day 1-7, 0 disables it.
        reset_max (int): The maximum number of renewals, 0 means unlimited.
        reset_count (int): The number of renewals already done.
        last_online (int): The last time the client was online, in milliseconds.
        last_sub_fetch (int): The last time the subscription was fetched, in milliseconds.
    """

    id: int = 0
    inbound_id: int = Field(default=0, alias=ClientInfoFields.INBOUND_ID)  # type: ignore
    enable: bool = True
    email: str = ""
    uuid: str = ""
    sub_id: str = Field(default="", alias=ClientInfoFields.SUB_ID)  # type: ignore
    up: int = 0
    down: int = 0
    expiry_time: int = Field(default=0, alias=ClientInfoFields.EXPIRY_TIME)  # type: ignore
    total: int = 0
    reset: int = 0
    reset_day: int = Field(default=0, alias=ClientInfoFields.RESET_DAY)  # type: ignore
    reset_weekday: int = Field(default=0, alias=ClientInfoFields.RESET_WEEKDAY)  # type: ignore
    reset_max: int = Field(default=0, alias=ClientInfoFields.RESET_MAX)  # type: ignore
    reset_count: int = Field(default=0, alias=ClientInfoFields.RESET_COUNT)  # type: ignore
    last_online: int = Field(default=0, alias=ClientInfoFields.LAST_ONLINE)  # type: ignore
    last_sub_fetch: int = Field(default=0, alias=ClientInfoFields.LAST_SUB_FETCH)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)


class ClientSlim(BaseModel):
    """Represents a compact client row of `panel/api/clients/list/paged`. It does not carry the
    UUID, password, flow and other credentials, so it can not be passed to `update`; use
    `get_details` to get the full client.

    Attributes:
        email (str): The email of the client.
        sub_id (str): The subscription ID of the client.
        enable (bool): Whether the client is enabled.
        total_gb (int): The traffic limit in bytes, 0 means unlimited.
        expiry_time (int): The expiry time in milliseconds, 0 means unlimited.
        limit_ip (int): The limit of IPs.
        limit_hwid (int): The limit of hardware IDs (devices).
        reset (int): The auto-renew interval in days.
        reset_day (int): The monthly renewal day.
        reset_weekday (int): The weekly renewal day.
        reset_max (int): The maximum number of renewals.
        group (str): The group of the client.
        comment (str): The comment of the client.
        inbound_ids (list[int]): The IDs of the inbounds the client is attached to.
        traffic (ClientTraffic | None): The traffic counters of the client.
        created_at (int): The creation time in milliseconds.
        updated_at (int): The last update time in milliseconds.
    """

    email: str
    sub_id: str = Field(default="", alias=ClientInfoFields.SUB_ID)  # type: ignore
    enable: bool = True
    total_gb: int = Field(default=0, alias=ClientInfoFields.TOTAL_GB)  # type: ignore
    expiry_time: int = Field(default=0, alias=ClientInfoFields.EXPIRY_TIME)  # type: ignore
    limit_ip: int = Field(default=0, alias=ClientInfoFields.LIMIT_IP)  # type: ignore
    limit_hwid: int = Field(default=0, alias=ClientInfoFields.LIMIT_HWID)  # type: ignore
    reset: int = 0
    reset_day: int = Field(default=0, alias=ClientInfoFields.RESET_DAY)  # type: ignore
    reset_weekday: int = Field(default=0, alias=ClientInfoFields.RESET_WEEKDAY)  # type: ignore
    reset_max: int = Field(default=0, alias=ClientInfoFields.RESET_MAX)  # type: ignore
    group: str = ""
    comment: str = ""
    inbound_ids: list[int] = Field(  # type: ignore
        default_factory=list, alias=ClientInfoFields.INBOUND_IDS
    )
    traffic: ClientTraffic | None = None
    created_at: int = Field(default=0, alias=ClientInfoFields.CREATED_AT)  # type: ignore
    updated_at: int = Field(default=0, alias=ClientInfoFields.UPDATED_AT)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("inbound_ids", mode="before")
    @classmethod
    def replace_null(cls, value: Any) -> Any:
        """Replaces JSON null with an empty list."""
        return _empty_list(value)


class ClientsSummary(BaseModel):
    """Represents the client counters of `panel/api/clients/list/paged`, computed over all
    clients regardless of filters. The counters are exact, the email lists stop at 200 entries.

    Attributes:
        total (int): The number of clients.
        active (int): The number of active clients.
        online_count (int): The number of online clients.
        depleted_count (int): The number of depleted clients.
        expiring_count (int): The number of clients that expire soon.
        deactive_count (int): The number of disabled clients.
        online (list[str]): The emails of online clients.
        depleted (list[str]): The emails of depleted clients.
        expiring (list[str]): The emails of clients that expire soon.
        deactive (list[str]): The emails of disabled clients.
    """

    total: int = 0
    active: int = 0
    online_count: int = Field(default=0, alias=ClientInfoFields.ONLINE_COUNT)  # type: ignore
    depleted_count: int = Field(default=0, alias=ClientInfoFields.DEPLETED_COUNT)  # type: ignore
    expiring_count: int = Field(default=0, alias=ClientInfoFields.EXPIRING_COUNT)  # type: ignore
    deactive_count: int = Field(default=0, alias=ClientInfoFields.DEACTIVE_COUNT)  # type: ignore
    online: list[str] = Field(default_factory=list)
    depleted: list[str] = Field(default_factory=list)
    expiring: list[str] = Field(default_factory=list)
    deactive: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("online", "depleted", "expiring", "deactive", mode="before")
    @classmethod
    def replace_null(cls, value: Any) -> Any:
        """Replaces JSON null with an empty list."""
        return _empty_list(value)


class ClientPage(BaseModel):
    """Represents one page of `panel/api/clients/list/paged`.

    Attributes:
        items (list[ClientSlim]): The clients of the page.
        total (int): The number of clients in the panel.
        filtered (int): The number of clients that match the filters.
        page (int): The page number, starting from 1.
        page_size (int): The page size.
        summary (ClientsSummary): The client counters.
        groups (list[str]): The names of all client groups.
    """

    items: list[ClientSlim] = Field(default_factory=list)
    total: int = 0
    filtered: int = 0
    page: int = 1
    page_size: int = Field(default=0, alias=ClientInfoFields.PAGE_SIZE)  # type: ignore
    summary: ClientsSummary = Field(default_factory=ClientsSummary)
    groups: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("items", "groups", mode="before")
    @classmethod
    def replace_null(cls, value: Any) -> Any:
        """Replaces JSON null with an empty list."""
        return _empty_list(value)


class ClientRenewalPreview(BaseModel):
    """Represents the result of `panel/api/clients/renewalPreview`. Dates are RFC 3339 strings
    in the panel time zone.

    Attributes:
        time_zone (str): The panel time zone.
        renew_at (str): When the next renewal happens.
        valid_through (str): The last moment of the current period.
        next_expiry (str): The expiry after the next renewal.
        suggested_expiry_time (int): The suggested expiry time in milliseconds.
        suggested_expiry (str): The suggested expiry time.
        renewals (int): The number of renewals that would be applied.
        can_renew (bool): Whether the client can be renewed.
        delayed_start (bool): Whether the expiry starts on first use.
    """

    time_zone: str = Field(default="", alias=ClientInfoFields.TIME_ZONE)  # type: ignore
    renew_at: str = Field(default="", alias=ClientInfoFields.RENEW_AT)  # type: ignore
    valid_through: str = Field(default="", alias=ClientInfoFields.VALID_THROUGH)  # type: ignore
    next_expiry: str = Field(default="", alias=ClientInfoFields.NEXT_EXPIRY)  # type: ignore
    suggested_expiry_time: int = Field(  # type: ignore
        default=0, alias=ClientInfoFields.SUGGESTED_EXPIRY_TIME
    )
    suggested_expiry: str = Field(  # type: ignore
        default="", alias=ClientInfoFields.SUGGESTED_EXPIRY
    )
    renewals: int = 0
    can_renew: bool = Field(default=False, alias=ClientInfoFields.CAN_RENEW)  # type: ignore
    delayed_start: bool = Field(default=False, alias=ClientInfoFields.DELAYED_START)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)


class BulkSkip(BaseModel):
    """Represents a client that a bulk operation skipped.

    Attributes:
        email (str): The email of the client.
        reason (str): Why the client was skipped.
    """

    email: str = ""
    reason: str = ""


class BulkResult(BaseModel):
    """Represents the result of a bulk operation on clients.

    Attributes:
        count (int): The number of processed clients: created, adjusted, deleted or changed,
            depending on the operation.
        skipped (list[BulkSkip]): The clients that were skipped, with reasons.
    """

    count: int = Field(  # type: ignore
        default=0,
        validation_alias=AliasChoices(
            "count",
            ClientInfoFields.CREATED,
            ClientInfoFields.ADJUSTED,
            ClientInfoFields.DELETED,
            ClientInfoFields.CHANGED,
        ),
    )
    skipped: list[BulkSkip] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("skipped", mode="before")
    @classmethod
    def replace_null(cls, value: Any) -> Any:
        """Replaces JSON null with an empty list."""
        return _empty_list(value)


class BulkAttachResult(BaseModel):
    """Represents the result of `panel/api/clients/bulkAttach`.

    Attributes:
        attached (list[str]): The emails of the attached clients.
        skipped (list[str]): The emails of the clients that were already attached.
        errors (list[str]): The error messages.
    """

    attached: list[str] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @field_validator("attached", "skipped", "errors", mode="before")
    @classmethod
    def replace_null(cls, value: Any) -> Any:
        """Replaces JSON null with an empty list."""
        return _empty_list(value)


class BulkDetachResult(BaseModel):
    """Represents the result of `panel/api/clients/bulkDetach`.

    Attributes:
        detached (list[str]): The emails of the detached clients.
        skipped (list[str]): The emails of the clients that were not attached.
        errors (list[str]): The error messages.
    """

    detached: list[str] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @field_validator("detached", "skipped", "errors", mode="before")
    @classmethod
    def replace_null(cls, value: Any) -> Any:
        """Replaces JSON null with an empty list."""
        return _empty_list(value)


class ClientGroup(BaseModel):
    """Represents a client group of `panel/api/clients/groups`.

    Attributes:
        name (str): The name of the group.
        client_count (int): The number of clients in the group.
        traffic_used (int): The traffic used by the group since its last reset, in bytes.
        up (int): The uploaded traffic of the group since its last reset, in bytes.
        down (int): The downloaded traffic of the group since its last reset, in bytes.
    """

    name: str
    client_count: int = Field(default=0, alias=ClientInfoFields.CLIENT_COUNT)  # type: ignore
    traffic_used: int = Field(default=0, alias=ClientInfoFields.TRAFFIC_USED)  # type: ignore
    up: int = 0
    down: int = 0

    model_config = ConfigDict(populate_by_name=True)


class ClientHwid(BaseModel):
    """Represents a device (HWID) registered for a client. The full hash of the device is not
    exposed by the panel.

    Attributes:
        id (int): The ID of the device.
        first_seen (int): When the device was first seen, in milliseconds.
        last_seen (int): When the device was last seen, in milliseconds.
        user_agent (str): The user agent of the device.
        device_os (str): The operating system of the device.
        os_version (str): The operating system version of the device.
        device_model (str): The model of the device.
        fingerprint (str): The short fingerprint of the device.
    """

    id: int
    first_seen: int = Field(default=0, alias=ClientInfoFields.FIRST_SEEN)  # type: ignore
    last_seen: int = Field(default=0, alias=ClientInfoFields.LAST_SEEN)  # type: ignore
    user_agent: str = Field(default="", alias=ClientInfoFields.USER_AGENT)  # type: ignore
    device_os: str = Field(default="", alias=ClientInfoFields.DEVICE_OS)  # type: ignore
    os_version: str = Field(default="", alias=ClientInfoFields.OS_VERSION)  # type: ignore
    device_model: str = Field(default="", alias=ClientInfoFields.DEVICE_MODEL)  # type: ignore
    fingerprint: str = ""

    model_config = ConfigDict(populate_by_name=True)


class ClientIpEntry(BaseModel):
    """Represents a source IP observed for a client.

    Attributes:
        ip (str): The IP address.
        timestamp (int): When the IP was last seen, in Unix seconds.
    """

    ip: str
    timestamp: int = 0
