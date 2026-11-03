"""This module contains the read-only models returned by the client endpoints of the XUI API:
traffic counters, paged client lists and renewal previews."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
