"""This module contains the Host and HostGroup classes which represent subscription hosts
in the XUI API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# pylint: disable=too-few-public-methods
class HostFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    GROUP_ID = "groupId"
    INBOUND_ID = "inboundId"
    INBOUND_IDS = "inboundIds"
    HOSTS = "hosts"
    ADDRESS = "address"

    SORT_ORDER = "sortOrder"
    REMARK = "remark"
    SERVER_DESCRIPTION = "serverDescription"
    IS_DISABLED = "isDisabled"
    IS_HIDDEN = "isHidden"
    TAGS = "tags"
    PORT = "port"

    SECURITY = "security"
    SNI = "sni"
    SNIS = "snis"
    SNI_SHARED_RANDOM = "sniSharedRandom"
    HOST_HEADER = "hostHeader"
    PATH = "path"
    ALPN = "alpn"
    FINGERPRINT = "fingerprint"
    CIPHER_SUITES = "cipherSuites"
    OVERRIDE_SNI_FROM_ADDRESS = "overrideSniFromAddress"
    KEEP_SNI_BLANK = "keepSniBlank"
    PINNED_PEER_CERT_SHA256 = "pinnedPeerCertSha256"
    VERIFY_PEER_CERT_BY_NAME = "verifyPeerCertByName"
    ALLOW_INSECURE = "allowInsecure"
    ECH_CONFIG_LIST = "echConfigList"

    MUX_PARAMS = "muxParams"
    SOCKOPT_PARAMS = "sockoptParams"
    FINAL_MASK = "finalMask"
    VLESS_ROUTE = "vlessRoute"
    EXCLUDE_FROM_SUB_TYPES = "excludeFromSubTypes"
    NODE_GUIDS = "nodeGuids"

    MIHOMO_IP_VERSION = "mihomoIpVersion"
    MIHOMO_X25519 = "mihomoX25519"
    SHUFFLE_HOST = "shuffleHost"
    RANDOM_COUNT = "randomCount"

    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"


class HostBase(BaseModel):
    """Stores the settings shared by a single host row and a host group.

    Defaults are the zero values of the panel, so leaving a field out of a request means the same
    as sending its default. String fields such as `security` keep their empty value here even
    though the panel may store its own default for them.

    Attributes:
        group_id (str): The ID of the host group. Optional.
        sort_order (int): The sort order. Optional.
        remark (str): The remark. Required.
        server_description (str): The server description. Optional.
        is_disabled (bool): Whether the host is disabled. Optional.
        is_hidden (bool): Whether the host is hidden. Optional.
        tags (list[str]): The tags. Optional.
        port (int): The port. Optional.
        security (str): The security: same, tls, none or reality. Optional.
        sni (str): The primary SNI. Optional.
        snis (list[str]): The SNI pool. Optional.
        sni_shared_random (bool): Whether the SNI is picked once for all hosts. Optional.
        host_header (str): The host header. Optional.
        path (str): The path. Optional.
        alpn (list[str]): The ALPN values. Optional.
        fingerprint (str): The TLS fingerprint. Optional.
        cipher_suites (str): The cipher suites. Optional.
        override_sni_from_address (bool): Whether the address is used as the SNI. Optional.
        keep_sni_blank (bool): Whether the SNI is kept blank. Optional.
        pinned_peer_cert_sha256 (list[str]): The pinned peer certificate hashes. Optional.
        verify_peer_cert_by_name (str): The name to verify the peer certificate by. Optional.
        allow_insecure (bool): Whether insecure connections are allowed. Optional.
        ech_config_list (str): The ECH config list. Optional.
        mux_params (str): The mux parameters as a JSON string. Optional.
        sockopt_params (str): The sockopt parameters as a JSON string. Optional.
        final_mask (str): The xray finalmask masks as a JSON string. Optional.
        vless_route (str): The VLESS route value (0-65535). Optional.
        exclude_from_sub_types (list[str]): The subscription types to skip this host in. Optional.
        node_guids (list[str]): The GUIDs of the nodes this host is limited to. Optional.
        mihomo_ip_version (str): The Mihomo IP version: dual, ipv4, ipv6, ipv4-prefer or
            ipv6-prefer. Optional.
        mihomo_x25519 (bool): Whether Mihomo uses X25519. Optional.
        shuffle_host (bool): Whether the hosts are shuffled. Optional.
        random_count (int): How many random hosts to use, the panel treats 0 as 1. Optional.
    """

    group_id: str = Field(default="", alias=HostFields.GROUP_ID)  # type: ignore

    sort_order: int = Field(default=0, alias=HostFields.SORT_ORDER)  # type: ignore
    remark: str
    server_description: str = Field(default="", alias=HostFields.SERVER_DESCRIPTION)  # type: ignore
    is_disabled: bool = Field(default=False, alias=HostFields.IS_DISABLED)  # type: ignore
    is_hidden: bool = Field(default=False, alias=HostFields.IS_HIDDEN)  # type: ignore
    tags: list[str] = Field(default_factory=list)
    port: int = 0

    security: str = ""
    sni: str = ""
    snis: list[str] = Field(default_factory=list)
    sni_shared_random: bool = Field(default=False, alias=HostFields.SNI_SHARED_RANDOM)  # type: ignore
    host_header: str = Field(default="", alias=HostFields.HOST_HEADER)  # type: ignore
    path: str = ""
    alpn: list[str] = Field(default_factory=list)
    fingerprint: str = ""
    cipher_suites: str = Field(default="", alias=HostFields.CIPHER_SUITES)  # type: ignore
    override_sni_from_address: bool = Field(  # type: ignore
        default=False, alias=HostFields.OVERRIDE_SNI_FROM_ADDRESS
    )
    keep_sni_blank: bool = Field(default=False, alias=HostFields.KEEP_SNI_BLANK)  # type: ignore
    pinned_peer_cert_sha256: list[str] = Field(  # type: ignore
        default_factory=list, alias=HostFields.PINNED_PEER_CERT_SHA256
    )
    verify_peer_cert_by_name: str = Field(  # type: ignore
        default="", alias=HostFields.VERIFY_PEER_CERT_BY_NAME
    )
    allow_insecure: bool = Field(default=False, alias=HostFields.ALLOW_INSECURE)  # type: ignore
    ech_config_list: str = Field(default="", alias=HostFields.ECH_CONFIG_LIST)  # type: ignore

    mux_params: str = Field(default="", alias=HostFields.MUX_PARAMS)  # type: ignore
    sockopt_params: str = Field(default="", alias=HostFields.SOCKOPT_PARAMS)  # type: ignore
    final_mask: str = Field(default="", alias=HostFields.FINAL_MASK)  # type: ignore
    vless_route: str = Field(default="", alias=HostFields.VLESS_ROUTE)  # type: ignore
    exclude_from_sub_types: list[str] = Field(  # type: ignore
        default_factory=list, alias=HostFields.EXCLUDE_FROM_SUB_TYPES
    )
    node_guids: list[str] = Field(  # type: ignore
        default_factory=list, alias=HostFields.NODE_GUIDS
    )

    mihomo_ip_version: str = Field(default="", alias=HostFields.MIHOMO_IP_VERSION)  # type: ignore
    mihomo_x25519: bool = Field(default=False, alias=HostFields.MIHOMO_X25519)  # type: ignore
    shuffle_host: bool = Field(default=False, alias=HostFields.SHUFFLE_HOST)  # type: ignore
    random_count: int = Field(default=0, alias=HostFields.RANDOM_COUNT)  # type: ignore

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    @field_validator(
        "tags",
        "snis",
        "alpn",
        "pinned_peer_cert_sha256",
        "exclude_from_sub_types",
        "node_guids",
        mode="before",
    )
    @classmethod
    def null_to_empty_list(cls, value: Any) -> Any:
        """Replaces null with an empty list, the panel returns null for unset lists."""
        return [] if value is None else value


class Host(HostBase):
    """Represents a single host row of an inbound, as returned by the panel.

    Attributes:
        id (int): The numeric ID of the host row. Required.
        inbound_id (int): The ID of the inbound the host belongs to. Required.
        address (str): The address of the host. Optional.
        created_at (int): The creation time in milliseconds. Optional.
        updated_at (int): The last update time in milliseconds. Optional.

    The settings are described in `HostBase`.
    """

    id: int
    inbound_id: int = Field(alias=HostFields.INBOUND_ID)  # type: ignore
    address: str = ""

    created_at: int = Field(default=0, alias=HostFields.CREATED_AT)  # type: ignore
    updated_at: int = Field(default=0, alias=HostFields.UPDATED_AT)  # type: ignore


class HostGroup(HostBase):
    """Represents a host group: the same settings applied to several addresses and inbounds.
    The panel stores it as one `Host` row per address and inbound.

    Attributes:
        inbound_ids (list[int]): The IDs of the inbounds of the group. Required.
        hosts (list[str]): The addresses of the group, each one may carry its own port as
            `address:port`. Optional.

    The settings are described in `HostBase`.
    """

    inbound_ids: list[int] = Field(alias=HostFields.INBOUND_IDS)  # type: ignore
    hosts: list[str] = Field(default_factory=list)
