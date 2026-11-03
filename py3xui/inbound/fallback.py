"""This module contains the InboundFallback class, which represents a fallback rule of a
master inbound in the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class InboundFallbackFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    MASTER_ID = "masterId"
    CHILD_ID = "childId"
    NAME = "name"
    ALPN = "alpn"
    PATH = "path"
    DEST = "dest"
    XVER = "xver"
    SORT_ORDER = "sortOrder"


class InboundFallback(BaseModel):
    """Represents a fallback rule attached to a master (VLESS / Trojan TCP-TLS) inbound.

    Attributes:
        child_id (int): The ID of the child inbound that receives the traffic. Optional.
        name (str): The SNI to match. Optional.
        alpn (str): The ALPN to match. Optional.
        path (str): The HTTP path to match. Optional.
        dest (str): The destination override (port, address:port or socket path). When empty,
            the panel resolves it from the child inbound's listen address and port. Optional.
        xver (int): The PROXY protocol version (0 disables it). Optional.
        sort_order (int): The sort order of the rule. Optional.
        id (int): The ID of the rule, set by the panel. Optional.
        master_id (int): The ID of the master inbound, set by the panel. Optional.
    """

    child_id: int = Field(default=0, alias=InboundFallbackFields.CHILD_ID)  # type: ignore
    name: str = ""
    alpn: str = ""
    path: str = ""
    dest: str = ""
    xver: int = 0
    sort_order: int = Field(default=0, alias=InboundFallbackFields.SORT_ORDER)  # type: ignore

    id: int = 0
    master_id: int = Field(default=0, alias=InboundFallbackFields.MASTER_ID)  # type: ignore

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )
