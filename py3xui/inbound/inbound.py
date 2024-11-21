"""This module contains the Inbound class, which represents an inbound connection in the XUI API."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from py3xui.client.client import Client
from py3xui.inbound.settings import Settings
from py3xui.inbound.sniffing import Sniffing
from py3xui.inbound.stream_settings import StreamSettings


# pylint: disable=too-few-public-methods
class InboundFields:
    """Stores the fields returned by the XUI API for parsing."""

    ENABLE = "enable"
    PORT = "port"
    PROTOCOL = "protocol"
    SETTINGS = "settings"
    STREAM_SETTINGS = "streamSettings"
    SNIFFING = "sniffing"

    ID = "id"
    UP = "up"
    DOWN = "down"
    TOTAL = "total"
    REMARK = "remark"

    EXPIRY_TIME = "expiryTime"
    CLIENT_STATS = "clientStats"
    LISTEN = "listen"

    TAG = "tag"


class Inbound(BaseModel):
    """Represents an inbound connection in the XUI API.

    Attributes:
        enable (bool): Whether the inbound connection is enabled. Required.
        port (int): The port number for the inbound connection. Required.
        protocol (str): The protocol for the inbound connection. Required.
        settings (Settings): The settings for the inbound connection. Required.
        stream_settings (StreamSettings): The stream settings for the inbound connection. Optional.
        sniffing (Sniffing): The sniffing settings for the inbound connection. Required.
        listen (str): The listen address for the inbound connection. Optional.
        remark (str): The remark for the inbound connection. Optional.
        id (int): The ID of the inbound connection. Optional.
        up (int): The up value for the inbound connection. Optional.
        down (int): The down value for the inbound connection. Optional.
        total (int): The total value for the inbound connection. Optional.
        expiry_time (int): The expiry time for the inbound connection. Optional.
        client_stats (list[Client]): The client stats for the inbound connection. Optional.
        tag (str): The tag for the inbound connection. Optional.
    """

    enable: bool
    port: int
    protocol: str
    settings: Settings
    stream_settings: StreamSettings | str = Field(  # type: ignore
        default="", alias=InboundFields.STREAM_SETTINGS
    )
    sniffing: Sniffing

    listen: str = ""
    remark: str = ""
    id: int = 0

    up: int = 0
    down: int = 0

    total: int = 0

    expiry_time: int = Field(default=0, alias=InboundFields.EXPIRY_TIME)  # type: ignore
    client_stats: list[Client] | None = Field(  # type: ignore
        default=[], alias=InboundFields.CLIENT_STATS
    )

    tag: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @field_validator("stream_settings")
    def validate_stream_settings(  # pylint: disable=no-self-argument
        cls, value: StreamSettings | str
    ) -> StreamSettings | str:
        """Validates the stream settings field taking into account that it can be either a
        dictionary with the StreamSettings model, JSON string or an empty string.
        If the value is a string, it will try to parse it as JSON and create a StreamSettings,
        otherwise it will return the value as is (empty string).

        Args:
            value (StreamSettings | str): The value to validate.

        Returns:
            StreamSettings | str: The validated value.
        """
        if isinstance(value, dict):
            return StreamSettings(**value)
        if isinstance(value, str):
            try:
                data = json.loads(value)
                return StreamSettings(**data)
            except json.JSONDecodeError:
                pass
        return value

    # pylint: disable=no-member, no-self-argument
    def to_json(self) -> dict[str, Any]:
        """Converts the Inbound instance to a JSON-compatible dictionary for the XUI API.

        Returns:
            dict[str, Any]: The JSON-compatible dictionary.
        """

        include = {
            InboundFields.REMARK,
            InboundFields.ENABLE,
            InboundFields.LISTEN,
            InboundFields.PORT,
            InboundFields.PROTOCOL,
            InboundFields.EXPIRY_TIME,
        }

        result = super().model_dump(by_alias=True)
        result = {k: v for k, v in result.items() if k in include}
        result.update(
            {
                InboundFields.SETTINGS: self.settings.model_dump_json(by_alias=True),
                InboundFields.SNIFFING: self.sniffing.model_dump_json(by_alias=True),
            }
        )

        # Handle stream_settings which can be either StreamSettings or str.
        if isinstance(self.stream_settings, StreamSettings):
            result[InboundFields.STREAM_SETTINGS] = self.stream_settings.model_dump_json(
                by_alias=True
            )
        else:
            result[InboundFields.STREAM_SETTINGS] = self.stream_settings

        return result
