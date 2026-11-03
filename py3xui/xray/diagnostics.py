"""This module contains the models of the outbound tests, the balancer states and the route tests
in the XUI API."""

from pydantic import BaseModel, ConfigDict, Field

from py3xui.xray.xray import StrList


# pylint: disable=too-few-public-methods
class OutboundTestFields:
    """Stores the fields returned by the XUI API for parsing."""

    TAG = "tag"
    SUCCESS = "success"
    DELAY = "delay"
    ERROR = "error"
    MODE = "mode"

    HTTP_STATUS = "httpStatus"
    CONNECT_MS = "connectMs"
    TLS_MS = "tlsMs"
    TTFB_MS = "ttfbMs"

    ENDPOINTS = "endpoints"
    EGRESS = "egress"

    ADDRESS = "address"

    IPV4 = "ipv4"
    IPV6 = "ipv6"
    COUNTRY = "country"
    WARP = "warp"


class OutboundTestEndpoint(BaseModel):
    """Represents the outcome of a TCP probe of one endpoint of an outbound.

    Attributes:
        address (str): The address of the endpoint.
        success (bool): Whether the endpoint is reachable.
        delay (int): The delay in milliseconds.
        error (str): The error message.
    """

    model_config = ConfigDict(populate_by_name=True)

    address: str = Field(alias=OutboundTestFields.ADDRESS)  # type: ignore
    success: bool = Field(alias=OutboundTestFields.SUCCESS)  # type: ignore
    delay: int = Field(default=0, alias=OutboundTestFields.DELAY)  # type: ignore
    error: str = Field(default="", alias=OutboundTestFields.ERROR)  # type: ignore


class OutboundTestEgress(BaseModel):
    """Represents what an external service sees after the outbound chain (HTTP probes only).

    Attributes:
        ipv4 (str): The IPv4 address.
        ipv6 (str): The IPv6 address.
        country (str): The country code.
        warp (str): The Warp status.
    """

    model_config = ConfigDict(populate_by_name=True)

    ipv4: str = Field(default="", alias=OutboundTestFields.IPV4)  # type: ignore
    ipv6: str = Field(default="", alias=OutboundTestFields.IPV6)  # type: ignore
    country: str = Field(default="", alias=OutboundTestFields.COUNTRY)  # type: ignore
    warp: str = Field(default="", alias=OutboundTestFields.WARP)  # type: ignore


class OutboundTestResult(BaseModel):
    """Represents the result of an outbound test.

    Attributes:
        tag (str): The tag of the outbound.
        success (bool): Whether the outbound is reachable.
        delay (int): The delay in milliseconds.
        error (str): The error message.
        mode (str): The mode of the probe.
        http_status (int): The HTTP status the test URL answered with.
        connect_ms (int): The time of the dial to the local test inbound in milliseconds.
        tls_ms (int): The time of the outbound chain establishment and target TLS in milliseconds.
        ttfb_ms (int): The time from the request start to the first response byte in milliseconds.
        endpoints (list[OutboundTestEndpoint]): The outcomes per endpoint (TCP probes only).
        egress (OutboundTestEgress | None): The egress information (HTTP probes only).
    """

    model_config = ConfigDict(populate_by_name=True)

    tag: str = Field(default="", alias=OutboundTestFields.TAG)  # type: ignore
    success: bool = Field(alias=OutboundTestFields.SUCCESS)  # type: ignore
    delay: int = Field(default=0, alias=OutboundTestFields.DELAY)  # type: ignore
    error: str = Field(default="", alias=OutboundTestFields.ERROR)  # type: ignore
    mode: str = Field(default="", alias=OutboundTestFields.MODE)  # type: ignore

    http_status: int = Field(default=0, alias=OutboundTestFields.HTTP_STATUS)  # type: ignore
    connect_ms: int = Field(default=0, alias=OutboundTestFields.CONNECT_MS)  # type: ignore
    tls_ms: int = Field(default=0, alias=OutboundTestFields.TLS_MS)  # type: ignore
    ttfb_ms: int = Field(default=0, alias=OutboundTestFields.TTFB_MS)  # type: ignore

    endpoints: list[OutboundTestEndpoint] = Field(  # type: ignore
        default=[], alias=OutboundTestFields.ENDPOINTS
    )
    egress: OutboundTestEgress | None = Field(  # type: ignore
        default=None, alias=OutboundTestFields.EGRESS
    )


# pylint: disable=too-few-public-methods
class BalancerStatusFields:
    """Stores the fields returned by the XUI API for parsing."""

    TAG = "tag"
    RUNNING = "running"
    OVERRIDE = "override"
    SELECTED = "selected"


class BalancerStatus(BaseModel):
    """Represents the live state of a balancer in the running core.

    Attributes:
        tag (str): The tag of the balancer.
        running (bool): Whether the balancer is present in the running core.
        override (str): The tag of the forced outbound.
        selected (list[str]): The outbounds the strategy prefers.
    """

    model_config = ConfigDict(populate_by_name=True)

    tag: str = Field(alias=BalancerStatusFields.TAG)  # type: ignore
    running: bool = Field(default=False, alias=BalancerStatusFields.RUNNING)  # type: ignore
    override: str = Field(default="", alias=BalancerStatusFields.OVERRIDE)  # type: ignore
    selected: StrList = Field(default=[], alias=BalancerStatusFields.SELECTED)  # type: ignore


# pylint: disable=too-few-public-methods
class RouteTestResultFields:
    """Stores the fields returned by the XUI API for parsing."""

    MATCHED = "matched"
    OUTBOUND_TAG = "outboundTag"
    GROUP_TAGS = "groupTags"


class RouteTestResult(BaseModel):
    """Represents the routing decision of the running core.

    Attributes:
        matched (bool): Whether a routing rule matched. If not, the traffic would use the default
            outbound and the outbound tag is empty.
        outbound_tag (str): The tag of the picked outbound.
        group_tags (list[str]): The balancer chain the decision went through.
    """

    model_config = ConfigDict(populate_by_name=True)

    matched: bool = Field(default=False, alias=RouteTestResultFields.MATCHED)  # type: ignore
    outbound_tag: str = Field(default="", alias=RouteTestResultFields.OUTBOUND_TAG)  # type: ignore
    group_tags: StrList = Field(default=[], alias=RouteTestResultFields.GROUP_TAGS)  # type: ignore
