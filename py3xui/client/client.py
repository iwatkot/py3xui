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
    inbound_id: int = Field(default=None, alias=ClientFields.INBOUND_ID)  # type: ignore

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
