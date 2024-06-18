from pydantic import BaseModel, Field


# pylint: disable=too-few-public-methods
class ClientFields:
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

    FLOW = "flow"
    LIMIT_IP = "limitIp"
    SUB_ID = "subId"
    TG_ID = "tgId"
    TOTAL_GB = "totalGB"


class Client(BaseModel):
    id: int | str | None = None
    inbound_id: int = Field(default=None, alias=ClientFields.INBOUND_ID)  # type: ignore
    enable: bool | None = None
    email: str | None = None
    up: int | None = None
    down: int | None = None
    expiry_time: int | None = Field(default=None, alias=ClientFields.EXPIRY_TIME)  # type: ignore
    total: int | None = None
    reset: int | None = None

    flow: str | None = None
    limit_ip: int | None = Field(default=None, alias=ClientFields.LIMIT_IP)  # type: ignore
    sub_id: str | None = Field(default=None, alias=ClientFields.SUB_ID)  # type: ignore
    tg_id: str | None = Field(default=None, alias=ClientFields.TG_ID)  # type: ignore
    total_gb: int | None = Field(default=None, alias=ClientFields.TOTAL_GB)  # type: ignore

    def __repr__(self) -> str:
        return (
            f"Client(id={self.id}, inbound_id={self.inbound_id}, enable={self.enable}, "
            f"email={self.email}, up={self.up}, down={self.down}, expiry_time={self.expiry_time}, "
            f"total={self.total}, reset={self.reset}, flow={self.flow}, limit_ip={self.limit_ip}, "
            f"sub_id={self.sub_id}, tg_id={self.tg_id}, total_gb={self.total_gb})"
        )
