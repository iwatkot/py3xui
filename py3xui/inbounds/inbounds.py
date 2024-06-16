from __future__ import annotations

from pydantic import BaseModel

from py3xui.clients.client_stats import ClientStats


class Inbound(BaseModel):
    id: int
    up: int
    down: int
    total: int
    remark: str
    enable: bool
    expiryTime: int
    clientStats: list[ClientStats]
    listen: str
    port: int
    protocol: str
    # TODO: Settings to classes
    settings: str
    streamSettings: str
    tag: str
    sniffing: str

    @classmethod
    def from_json(cls, data: dict[str, int | bool | str]) -> Inbound:
        return cls(**data)  # type: ignore

    def __repr__(self) -> str:
        return (
            f"Inbound(id={self.id}, up={self.up}, down={self.down}, total={self.total}, "
            f"remark={self.remark}, enable={self.enable}, expiryTime={self.expiryTime}, "
            f"clientStats={self.clientStats}, listen={self.listen}, port={self.port}, "
            f"protocol={self.protocol}"
        )
