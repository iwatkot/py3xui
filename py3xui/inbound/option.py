"""This module contains the InboundOption class, a lightweight projection of an inbound
returned by the XUI API for client pickers."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class InboundOptionFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    REMARK = "remark"
    TAG = "tag"
    PROTOCOL = "protocol"
    PORT = "port"
    ENABLE = "enable"
    NETWORK = "network"
    SECURITY = "security"
    TLS_FLOW_CAPABLE = "tlsFlowCapable"
    SS_METHOD = "ssMethod"
    WG_PUBLIC_KEY = "wgPublicKey"
    WG_MTU = "wgMtu"
    WG_DNS = "wgDns"
    MTPROTO_DOMAIN = "mtprotoDomain"
    AWG_SERVER = "awgServer"
    TUIC_SERVER = "tuicServer"
    NODE_ID = "nodeId"
    NODE_ADDRESS = "nodeAddress"
    LISTEN = "listen"
    SHARE_ADDR = "shareAddr"
    SHARE_ADDR_STRATEGY = "shareAddrStrategy"


class InboundOption(BaseModel):
    """Represents a lightweight projection of an inbound (no client settings or traffic stats).

    Attributes:
        id (int): The ID of the inbound. Required.
        remark (str): The remark of the inbound. Optional.
        tag (str): The Xray tag of the inbound. Optional.
        protocol (str): The protocol of the inbound. Optional.
        port (int): The port of the inbound. Optional.
        enable (bool): Whether the inbound is enabled. Optional.
        network (str): The transport network hint (e.g. "tcp"). Optional.
        security (str): The transport security hint (e.g. "reality"). Optional.
        tls_flow_capable (bool): Whether clients of the inbound can use the XTLS flow. Optional.
        ss_method (str): The Shadowsocks method. Optional.
        wg_public_key (str): The WireGuard server public key. Optional.
        wg_mtu (int): The WireGuard MTU. Optional.
        wg_dns (str): The WireGuard DNS servers. Optional.
        mtproto_domain (str): The MTProto fake TLS domain. Optional.
        awg_server (dict[str, Any] | None): The AmneziaWG server block. Optional.
        tuic_server (dict[str, Any] | None): The TUIC server block. Optional.
        node_id (int | None): The ID of the hosting node, None for local inbounds. Optional.
        node_address (str): The external address of the hosting node. Optional.
        listen (str): The listen address of the inbound. Optional.
        share_addr (str): The custom share address. Optional.
        share_addr_strategy (str): The share address strategy. Optional.
    """

    id: int
    remark: str = ""
    tag: str = ""
    protocol: str = ""
    port: int = 0
    enable: bool = False
    network: str = ""
    security: str = ""
    tls_flow_capable: bool = Field(  # type: ignore
        default=False, alias=InboundOptionFields.TLS_FLOW_CAPABLE
    )
    ss_method: str = Field(default="", alias=InboundOptionFields.SS_METHOD)  # type: ignore
    wg_public_key: str = Field(default="", alias=InboundOptionFields.WG_PUBLIC_KEY)  # type: ignore
    wg_mtu: int = Field(default=0, alias=InboundOptionFields.WG_MTU)  # type: ignore
    wg_dns: str = Field(default="", alias=InboundOptionFields.WG_DNS)  # type: ignore
    mtproto_domain: str = Field(  # type: ignore
        default="", alias=InboundOptionFields.MTPROTO_DOMAIN
    )
    awg_server: dict[str, Any] | None = Field(  # type: ignore
        default=None, alias=InboundOptionFields.AWG_SERVER
    )
    tuic_server: dict[str, Any] | None = Field(  # type: ignore
        default=None, alias=InboundOptionFields.TUIC_SERVER
    )
    node_id: int | None = Field(default=None, alias=InboundOptionFields.NODE_ID)  # type: ignore
    node_address: str = Field(default="", alias=InboundOptionFields.NODE_ADDRESS)  # type: ignore
    listen: str = ""
    share_addr: str = Field(default="", alias=InboundOptionFields.SHARE_ADDR)  # type: ignore
    share_addr_strategy: str = Field(  # type: ignore
        default="", alias=InboundOptionFields.SHARE_ADDR_STRATEGY
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )
