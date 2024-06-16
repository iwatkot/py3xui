"""Module for the ClientStats class, which represents the client statistics from XUI API."""

from __future__ import annotations

from pydantic import BaseModel


class ClientStats(BaseModel):
    id: int
    inboundId: int
    enable: bool
    email: str
    up: int
    down: int
    expiryTime: int
    total: int
    reset: int

    @classmethod
    def from_json(cls, data: dict[str, int | bool | str]) -> ClientStats:
        return cls(**data)  # type: ignore

    def __repr__(self) -> str:
        return (
            f"ClientStats(id={self.id}, inboundId={self.inboundId}, enable={self.enable}, "
            f"email={self.email}, up={self.up}, down={self.down}, expiryTime={self.expiryTime}, "
            f"total={self.total}, reset={self.reset})"
        )
