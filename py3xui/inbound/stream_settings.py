from pydantic import Field

from py3xui.inbound.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class StreamSettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    SECURITY = "security"
    NETWORK = "network"
    TCP_SETTINGS = "tcpSettings"

    EXTERNAL_PROXY = "externalProxy"

    REALITY_SETTINGS = "realitySettings"
    XTLS_SETTINGS = "xtlsSettings"
    TLS_SETTINGS = "tlsSettings"


class StreamSettings(JsonStringModel):
    security: str
    network: str
    tcp_settings: dict = Field(alias=StreamSettingsFields.TCP_SETTINGS)  # type: ignore

    external_proxy: list | None = Field(
        default=None, alias=StreamSettingsFields.EXTERNAL_PROXY
    )  # type: ignore

    reality_settings: dict | None = Field(  # type: ignore
        default=None, alias=StreamSettingsFields.REALITY_SETTINGS
    )
    xtls_settings: dict | None = Field(  # type: ignore
        default=None, alias=StreamSettingsFields.XTLS_SETTINGS
    )
    tls_settings: dict | None = Field(  # type: ignore
        default=None, alias=StreamSettingsFields.TLS_SETTINGS
    )
