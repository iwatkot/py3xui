from pydantic import Field

from py3xui.inbound.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class SniffingFields:
    """Stores the fields returned by the XUI API for parsing."""

    ENABLED = "enabled"

    DEST_OVERRIDE = "destOverride"

    METADATA_ONLY = "metadataOnly"
    ROUTE_ONLY = "routeOnly"


class Sniffing(JsonStringModel):
    enabled: bool

    dest_override: list[str] | None = Field(
        default=None, alias=SniffingFields.DEST_OVERRIDE
    )  # type: ignore

    metadata_only: bool | None = Field(  # type: ignore
        default=None, alias=SniffingFields.METADATA_ONLY
    )
    route_only: bool | None = Field(default=None, alias=SniffingFields.ROUTE_ONLY)  # type: ignore
