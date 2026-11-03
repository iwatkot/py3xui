"""This module contains the models of the Xray configuration and the outbound traffic
in the XUI API."""

import json
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator

# The panel encodes an empty Go slice as null in some responses.
StrList = Annotated[
    list[str], BeforeValidator(lambda value: [] if value is None else value)
]


def parse_json_obj(obj: str | None) -> Any:
    """Parses a JSON document which the panel returns as a string in the `obj` field.

    Arguments:
        obj (str | None): The value of the `obj` field.

    Returns:
        Any: The parsed document or None if the value is empty."""
    return json.loads(obj) if obj else None


# pylint: disable=too-few-public-methods
class GeodataSourceFields:
    """Stores the fields returned by the XUI API for parsing."""

    URL = "url"
    FILE = "file"


class GeodataSource(BaseModel):
    """Represents a geo database preset which Xray can download.

    Attributes:
        url (str): The download URL.
        file (str): The name of the database file.
    """

    model_config = ConfigDict(populate_by_name=True)

    url: str = Field(alias=GeodataSourceFields.URL)  # type: ignore
    file: str = Field(alias=GeodataSourceFields.FILE)  # type: ignore


# pylint: disable=too-few-public-methods
class XraySettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    XRAY_SETTING = "xraySetting"
    INBOUND_TAGS = "inboundTags"
    CLIENT_REVERSE_TAGS = "clientReverseTags"
    OUTBOUND_TEST_URL = "outboundTestUrl"
    GEODATA_SOURCES = "geodataSources"
    SUBSCRIPTION_OUTBOUNDS = "subscriptionOutbounds"
    SUBSCRIPTION_OUTBOUND_TAGS = "subscriptionOutboundTags"


class XraySettings(BaseModel):
    """Represents the Xray configuration template with the data the panel returns along with it.

    Attributes:
        xray_setting (dict[str, Any]): The Xray configuration template.
        inbound_tags (list[str]): The tags of the inbounds.
        client_reverse_tags (list[str]): The reverse tags of the clients.
        outbound_test_url (str): The URL used to test the outbounds.
        geodata_sources (list[GeodataSource]): The geo database presets.
        subscription_outbounds (list[dict[str, Any]]): The outbounds supplied by the outbound
            subscriptions. They are injected at runtime and are not part of the template.
        subscription_outbound_tags (list[str]): The tags of the subscription outbounds.
    """

    model_config = ConfigDict(populate_by_name=True)

    xray_setting: dict[str, Any] = Field(alias=XraySettingsFields.XRAY_SETTING)  # type: ignore
    inbound_tags: StrList = Field(default=[], alias=XraySettingsFields.INBOUND_TAGS)  # type: ignore
    client_reverse_tags: StrList = Field(  # type: ignore
        default=[], alias=XraySettingsFields.CLIENT_REVERSE_TAGS
    )
    outbound_test_url: str = Field(default="", alias=XraySettingsFields.OUTBOUND_TEST_URL)  # type: ignore
    geodata_sources: list[GeodataSource] = Field(  # type: ignore
        default=[], alias=XraySettingsFields.GEODATA_SOURCES
    )
    subscription_outbounds: list[dict[str, Any]] = Field(  # type: ignore
        default=[], alias=XraySettingsFields.SUBSCRIPTION_OUTBOUNDS
    )
    subscription_outbound_tags: StrList = Field(  # type: ignore
        default=[], alias=XraySettingsFields.SUBSCRIPTION_OUTBOUND_TAGS
    )


# pylint: disable=too-few-public-methods
class OutboundTrafficFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    TAG = "tag"
    UP = "up"
    DOWN = "down"
    TOTAL = "total"


class OutboundTraffic(BaseModel):
    """Represents the traffic statistics of an outbound.

    Attributes:
        id (int): The ID of the record.
        tag (str): The tag of the outbound.
        up (int): The uploaded traffic in bytes.
        down (int): The downloaded traffic in bytes.
        total (int): The total traffic in bytes.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(default=0, alias=OutboundTrafficFields.ID)  # type: ignore
    tag: str = Field(alias=OutboundTrafficFields.TAG)  # type: ignore
    up: int = Field(default=0, alias=OutboundTrafficFields.UP)  # type: ignore
    down: int = Field(default=0, alias=OutboundTrafficFields.DOWN)  # type: ignore
    total: int = Field(default=0, alias=OutboundTrafficFields.TOTAL)  # type: ignore
