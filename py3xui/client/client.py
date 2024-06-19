from pydantic import BaseModel, Field


# pylint: disable=too-few-public-methods
class ClientFields:
    """Stores the fields returned by the XUI API for parsing."""

    EMAIL = "email"
    ENABLE = "enable"

    ID = "id"
    INBOUND_ID = "inboundId"

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
    email: str
    enable: bool

    id: int | str | None = None
    inbound_id: int | None = Field(default=None, alias=ClientFields.INBOUND_ID)  # type: ignore

    up: int = 0
    down: int = 0

    expiry_time: int = Field(default=0, alias=ClientFields.EXPIRY_TIME)  # type: ignore

    total: int = 0
    reset: int = 0

    flow: str = ""
    limit_ip: int = Field(default=0, alias=ClientFields.LIMIT_IP)  # type: ignore
    sub_id: str = Field(default="", alias=ClientFields.SUB_ID)  # type: ignore
    tg_id: str = Field(default="", alias=ClientFields.TG_ID)  # type: ignore
    total_gb: int = Field(default=0, alias=ClientFields.TOTAL_GB)  # type: ignore
