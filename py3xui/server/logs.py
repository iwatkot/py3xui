"""This module contains the models for the log endpoints of the XUI API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class LogsFields:
    """Stores the fields returned by the XUI API for parsing."""

    DATE_TIME = "DateTime"
    FROM_ADDRESS = "FromAddress"
    TO_ADDRESS = "ToAddress"
    INBOUND = "Inbound"
    OUTBOUND = "Outbound"
    EMAIL = "Email"
    EVENT = "Event"

    INBOUND_ID = "inboundId"
    ALLOWED_IPS = "allowedIPs"


class XrayLogEntry(BaseModel):
    """Represents one line of the Xray access log.

    Attributes:
        date_time (datetime): The time of the event.
        from_address (str): The source address.
        to_address (str): The destination address.
        inbound (str): The inbound tag.
        outbound (str): The outbound tag.
        email (str): The email of the client.
        event (int): The kind of the traffic: 0 for direct, 1 for blocked, 2 for proxied.
    """

    date_time: datetime = Field(alias=LogsFields.DATE_TIME)  # type: ignore
    from_address: str = Field(alias=LogsFields.FROM_ADDRESS)  # type: ignore
    to_address: str = Field(alias=LogsFields.TO_ADDRESS)  # type: ignore
    inbound: str = Field(alias=LogsFields.INBOUND)  # type: ignore
    outbound: str = Field(alias=LogsFields.OUTBOUND)  # type: ignore
    email: str = Field(alias=LogsFields.EMAIL)  # type: ignore
    event: int = Field(alias=LogsFields.EVENT)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)


class AmneziaWGPeer(BaseModel):
    """Represents the live state of one AmneziaWG peer.

    Attributes:
        interface (str): The name of the interface.
        tag (str): The inbound tag.
        inbound_id (int): The ID of the inbound.
        email (str): The email of the client.
        endpoint (str): The address of the peer.
        allowed_ips (str): The IP addresses allowed for the peer.
        handshake (int): The last handshake, Unix time in milliseconds, 0 when there was none.
        up (int): The uploaded traffic in bytes.
        down (int): The downloaded traffic in bytes.
        online (bool): Whether the peer is online.
    """

    interface: str
    tag: str
    inbound_id: int = Field(alias=LogsFields.INBOUND_ID)  # type: ignore
    email: str
    endpoint: str
    allowed_ips: str = Field(alias=LogsFields.ALLOWED_IPS)  # type: ignore
    handshake: int
    up: int
    down: int
    online: bool

    model_config = ConfigDict(populate_by_name=True)


class AmneziaWGLogs(BaseModel):
    """Represents the live AmneziaWG activity of the panel.

    Attributes:
        peers (list[AmneziaWGPeer]): The live state of the peers.
        events (list[str]): The AmneziaWG lines of the panel log.
        running (bool): Whether any AmneziaWG interface is running.
    """

    peers: list[AmneziaWGPeer]
    events: list[str]
    running: bool
