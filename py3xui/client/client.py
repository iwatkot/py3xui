"""This module contains the Client class which represents a client in the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class ClientFields:
    """Stores the fields returned by the XUI API for parsing."""

    EMAIL = "email"
    ENABLE = "enable"
    PASSWORD = "password"

    ID = "id"
    INBOUND_ID = "inboundId"

    UP = "up"
    DOWN = "down"

    EXPIRY_TIME = "expiryTime"

    TOTAL = "total"
    RESET = "reset"

    FLOW = "flow"
    METHOD = "method"
    LIMIT_IP = "limitIp"
    SUB_ID = "subId"
    TG_ID = "tgId"
    TOTAL_GB = "totalGB"


class Client(BaseModel):
    """Represents a client in the XUI API.

    Attributes:
        email (str): The email of the client. Required.
        enable (bool): Whether the client is enabled. Required.
        password (str): The password of the client. Optional.
        id (int | str): The ID of the client. Required.
        inbound_id (int | None): The ID of the inbound connection. Optional.
        up (int): The upload speed of the client. Optional.
        down (int): The download speed of the client. Optional.
        expiry_time (int): The expiry time of the client. Optional.
        total (int): The total amount of data transferred by the client. Optional.
        reset (int): The time at which the client's data was last reset. Optional.
        flow (str): The flow of the client. Optional.
        method (str): The method (encryption cipher) used by the client. Optional.
        limit_ip (int): The limit of IPs for the client. Optional.
        sub_id (str): The sub ID of the client. Optional.
        tg_id (str): The Telegram ID of the client. Optional.
        total_gb (int): The total amount of data transferred by the client in GB. Optional.
    """

    email: str
    enable: bool
    id: int | str | None = Field(default=None)
    password: str = Field(default="")  # type: ignore

    inbound_id: int | None = Field(default=None, alias=ClientFields.INBOUND_ID)  # type: ignore

    up: int = 0
    down: int = 0

    expiry_time: int = Field(default=0, alias=ClientFields.EXPIRY_TIME)  # type: ignore

    total: int = 0
    reset: int | None = None

    flow: str = ""
    method: str = ""
    limit_ip: int = Field(default=0, alias=ClientFields.LIMIT_IP)  # type: ignore
    sub_id: str = Field(default="", alias=ClientFields.SUB_ID)  # type: ignore
    tg_id: int | str | None = Field(default="", alias=ClientFields.TG_ID)  # type: ignore
    total_gb: int = Field(default=0, alias=ClientFields.TOTAL_GB)  # type: ignore

    model_config = ConfigDict(
        populate_by_name=True,
    )
