from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# {
#     "destOverride": ["http", "tls", "quic", "fakedns"],
#     "enabled": True,
#     "metadataOnly": False,
#     "routeOnly": False,
# }


# pylint: disable=too-few-public-methods
class SniffingFields:
    """Stores the fields returned by the XUI API for parsing."""

    DEST_OVERRIDE = "destOverride"
    ENABLED = "enabled"
    METADATA_ONLY = "metadataOnly"
    ROUTE_ONLY = "routeOnly"


class Sniffing(BaseModel):
    dest_override: list[str] = Field(alias=SniffingFields.DEST_OVERRIDE)  # type: ignore
    enabled: bool
    metadata_only: bool = Field(alias=SniffingFields.METADATA_ONLY)  # type: ignore
    route_only: bool = Field(alias=SniffingFields.ROUTE_ONLY)  # type: ignore

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Sniffing:
        return cls.parse_obj(data)

    def __repr__(self) -> str:
        return (
            f"Sniffing(dest_override={self.dest_override}, enabled={self.enabled}, "
            f"metadata_only={self.metadata_only}, route_only={self.route_only})"
        )
