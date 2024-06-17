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


class Client(BaseModel):
    id: int
    inbound_id: int = Field(alias=ClientFields.INBOUND_ID)  # type: ignore
    enable: bool
    email: str
    up: int
    down: int
    expiry_time: int = Field(alias=ClientFields.EXPIRY_TIME)  # type: ignore
    total: int
    reset: int

    def __repr__(self) -> str:
        return (
            f"Client(id={self.id}, inbound_id={self.inbound_id}, enable={self.enable}, "
            f"email={self.email}, up={self.up}, down={self.down}, expiry_time={self.expiry_time}, "
            f"total={self.total}, reset={self.reset})"
        )
