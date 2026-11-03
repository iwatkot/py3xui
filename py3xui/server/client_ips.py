"""This module contains the models for the client IPs endpoints of the XUI API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# pylint: disable=too-few-public-methods
class ClientIpsFields:
    """Stores the fields returned by the XUI API for parsing."""

    CLIENT_EMAIL = "clientEmail"


class InboundClientIpEntry(BaseModel):
    """Represents an IP address observed for a client.

    Attributes:
        ip (str): The IP address.
        timestamp (int): When the IP was last seen, Unix time in seconds, 0 when it is unknown.
    """

    ip: str
    timestamp: int = 0


class InboundClientIps(BaseModel):
    """Represents the recently active IP addresses of a client.

    Attributes:
        id (int): The ID of the record on the panel.
        client_email (str): The email of the client.
        ips (list[InboundClientIpEntry] | None): The IP addresses, None when there are none.
    """

    id: int = 0
    client_email: str = Field(alias=ClientIpsFields.CLIENT_EMAIL)  # type: ignore
    ips: list[InboundClientIpEntry] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("ips", mode="before")
    @classmethod
    def _normalize_ips(cls, value: Any) -> Any:
        """Accepts the records of old panels: plain IP strings become entries without a timestamp,
        and a value that is not a list means that there are no IPs."""
        if not isinstance(value, list):
            return None
        return [{"ip": item} if isinstance(item, str) else item for item in value]
