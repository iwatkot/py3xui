"""This module contains the StreamSettings class for parsing the XUI API response."""
import random
import secrets

from pydantic import ConfigDict, Field

from py3xui.inbound.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class StreamSettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    SECURITY = "security"
    NETWORK = "network"
    TCP_SETTINGS = "tcpSettings"
    KCP_SETTINGS = "kcpSettings"

    EXTERNAL_PROXY = "externalProxy"

    REALITY_SETTINGS = "realitySettings"
    XTLS_SETTINGS = "xtlsSettings"
    TLS_SETTINGS = "tlsSettings"


class StreamSettings(JsonStringModel):
    """Represents the stream settings for an inbound.

    Attributes:
        security (str): The security for the inbound connection. Required.
        network (str): The network for the inbound connection. Required.
        tcp_settings (dict): The TCP settings for the inbound connection. Required.
        external_proxy (list): The external proxy for the inbound connection. Optional.
        reality_settings (dict): The reality settings for the inbound connection. Optional.
        xtls_settings (dict): The xTLS settings for the inbound connection. Optional.
        tls_settings (dict): The TLS settings for the inbound connection. Optional.
    """

    security: str
    network: str
    tcp_settings: dict = Field(  # type: ignore
        default={}, alias=StreamSettingsFields.TCP_SETTINGS
    )
    kcp_settings: dict = Field(  # type: ignore
        default={}, alias=StreamSettingsFields.KCP_SETTINGS
    )

    external_proxy: list = Field(  # type: ignore
        default=[], alias=StreamSettingsFields.EXTERNAL_PROXY
    )

    reality_settings: dict = Field(  # type: ignore
        default={}, alias=StreamSettingsFields.REALITY_SETTINGS
    )
    xtls_settings: dict = Field(  # type: ignore
        default={}, alias=StreamSettingsFields.XTLS_SETTINGS
    )
    tls_settings: dict = Field(default={}, alias=StreamSettingsFields.TLS_SETTINGS)  # type: ignore

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @staticmethod
    def get_random_short_ids(self)->list:
        """
        generate random short Ids
        """

        def random_seq(count, type="default", has_numbers=True, has_lowercase=True, has_uppercase=True):
            seq = ''
            if type == "hex":
                seq = "0123456789abcdef"
            else:
                if has_numbers:
                    seq += "0123456789"
                if has_lowercase:
                    seq += "abcdefghijklmnopqrstuvwxyz"
                if has_uppercase:
                    seq += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

            # 生成随机序列
            seq_length = len(seq)
            result = ''.join(seq[secrets.randbelow(seq_length)] for _ in range(count))
            return result

        lengths = [2, 4, 6, 8, 10, 12, 14, 16]
        random.shuffle(lengths)

        return [random_seq(length, type="hex") for length in lengths]
