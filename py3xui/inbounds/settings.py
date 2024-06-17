from pydantic import BaseModel, Field

from py3xui.inbounds.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class SettingsClientFields:
    """Stores the fields returned by the XUI API for parsing."""

    EMAIL = "email"
    ENABLE = "enable"
    EXPIRY_TIME = "expiryTime"
    FLOW = "flow"
    ID = "id"
    LIMIT_IP = "limitIp"
    RESET = "reset"
    SUB_ID = "subId"
    TG_ID = "tgId"
    TOTAL_GB = "totalGB"


# pylint: disable=too-few-public-methods
class SettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    CLIENTS = "clients"
    DECRYPTION = "decryption"
    FALLBACKS = "fallbacks"


class SettingsClient(BaseModel):
    email: str
    enable: bool
    expiry_time: int = Field(alias=SettingsClientFields.EXPIRY_TIME)  # type: ignore
    flow: str
    id: str
    limit_ip: int = Field(alias=SettingsClientFields.LIMIT_IP)  # type: ignore
    reset: int
    sub_id: str = Field(alias=SettingsClientFields.SUB_ID)  # type: ignore
    tg_id: str = Field(alias=SettingsClientFields.TG_ID)  # type: ignore
    total_gb: int = Field(alias=SettingsClientFields.TOTAL_GB)  # type: ignore

    def __repr__(self) -> str:
        return (
            f"SettingsClient(email={self.email}, enable={self.enable}, "
            f"expiry_time={self.expiry_time}, "
            f"flow={self.flow}, id={self.id}, limit_ip={self.limit_ip}, reset={self.reset}, "
            f"sub_id={self.sub_id}, tg_id={self.tg_id}, total_gb={self.total_gb})"
        )


class Settings(JsonStringModel):
    clients: list[SettingsClient]
    decryption: str
    fallbacks: list

    def __repr__(self) -> str:
        return (
            f"Settings(clients={self.clients}, decryption={self.decryption}, "
            f"fallbacks={self.fallbacks})"
        )
