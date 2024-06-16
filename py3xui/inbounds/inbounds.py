from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from py3xui.clients.client_stats import ClientStats
from py3xui.inbounds.stream_settings import StreamSettings


# pylint: disable=too-few-public-methods
class InboundFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    UP = "up"
    DOWN = "down"
    TOTAL = "total"
    REMARK = "remark"
    ENABLE = "enable"
    EXPIRY_TIME = "expiryTime"
    CLIENT_STATS = "clientStats"
    LISTEN = "listen"
    PORT = "port"
    PROTOCOL = "protocol"
    SETTINGS = "settings"
    STREAM_SETTINGS = "streamSettings"
    TAG = "tag"
    SNIFFING = "sniffing"


class Inbound(BaseModel):
    id: int
    up: int
    down: int
    total: int
    remark: str
    enable: bool
    expiry_time: int = Field(alias=InboundFields.EXPIRY_TIME)  # type: ignore
    client_stats: list[ClientStats] = Field(alias=InboundFields.CLIENT_STATS)  # type: ignore
    listen: str
    port: int
    protocol: str
    # TODO: Move dict values to pydantic models.
    settings: dict
    stream_settings: StreamSettings = Field(alias=InboundFields.STREAM_SETTINGS)  # type: ignore
    tag: str
    sniffing: dict

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Inbound:
        raw_client_stats = data.pop(InboundFields.CLIENT_STATS, [])
        client_stats = []
        for raw_client_stat in raw_client_stats:
            if not isinstance(raw_client_stat, dict):
                continue
            client_stats.append(ClientStats.from_json(raw_client_stat))
        data[InboundFields.CLIENT_STATS] = client_stats

        raw_stream_settings = json.loads(data.pop(InboundFields.STREAM_SETTINGS, "{}"))
        stream_settings = StreamSettings.from_json(raw_stream_settings)
        data[InboundFields.STREAM_SETTINGS] = stream_settings

        possible_json_strings = [InboundFields.SETTINGS, InboundFields.SNIFFING]
        for key in possible_json_strings:
            if isinstance(data.get(key), str):
                data[key] = json.loads(data[key])

        return cls.parse_obj(data)

    def __repr__(self) -> str:
        return (
            f"Inbound(id={self.id}, up={self.up}, down={self.down}, total={self.total}, "
            f"remark={self.remark}, enable={self.enable}, expiryTime={self.expiry_time}, "
            f"clientStats={self.client_stats}, listen={self.listen}, port={self.port}, "
            f"protocol={self.protocol}, settings={self.settings}, "
            f"streamSettings={self.stream_settings}, tag={self.tag}, sniffing={self.sniffing})"
        )
