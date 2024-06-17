"""Module for the ClientStats class, which represents the client statistics from XUI API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# pylint: disable=too-few-public-methods
class ClientStatsFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    INBOUND_ID = "inboundId"
    ENABLE = "enable"
    EMAIL = "email"
    UP = "up"
    DOWN = "down"
    EXPIRY_TIME = "expiryTime"
    TOTAL = "total"
    RESET = "reset"


class ClientStats(BaseModel):
    id: int
    inbound_id: int = Field(alias=ClientStatsFields.INBOUND_ID)  # type: ignore
    enable: bool
    email: str
    up: int
    down: int
    expiry_time: int = Field(alias=ClientStatsFields.EXPIRY_TIME)  # type: ignore
    total: int
    reset: int

    def __repr__(self) -> str:
        return (
            f"ClientStats(id={self.id}, inbound_id={self.inbound_id}, enable={self.enable}, "
            f"email={self.email}, up={self.up}, down={self.down}, expiry_time={self.expiry_time}, "
            f"total={self.total}, reset={self.reset})"
        )
