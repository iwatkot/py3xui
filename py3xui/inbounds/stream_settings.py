from __future__ import annotations

from pydantic import Field

from py3xui.inbounds.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class StreamSettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    EXTERNAL_PROXY = "externalProxy"
    NETWORK = "network"
    SECURITY = "security"
    TCP_SETTINGS = "tcpSettings"
    REALITY_SETTINGS = "realitySettings"
    XTLS_SETTINGS = "xtlsSettings"
    TLS_SETTINGS = "tlsSettings"


class StreamSettings(JsonStringModel):
    external_proxy: list = Field(alias=StreamSettingsFields.EXTERNAL_PROXY)  # type: ignore
    network: str
    security: str
    tcp_settings: dict = Field(alias=StreamSettingsFields.TCP_SETTINGS)  # type: ignore

    reality_settings: dict | None = Field(  # type: ignore
        None, alias=StreamSettingsFields.REALITY_SETTINGS
    )
    xtls_settings: dict | None = Field(  # type: ignore
        None, alias=StreamSettingsFields.XTLS_SETTINGS
    )
    tls_settings: dict | None = Field(None, alias=StreamSettingsFields.TLS_SETTINGS)  # type: ignore

    def __repr__(self) -> str:
        return (
            f"StreamSettings(external_proxy={self.external_proxy}, network={self.network}, "
            f"security={self.security}, tcp_settings={self.tcp_settings}, "
            f"reality_settings={self.reality_settings}, xtls_settings={self.xtls_settings}, "
            f"tls_settings={self.tls_settings})"
        )
