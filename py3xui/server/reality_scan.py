"""This module contains the model for the REALITY target scan endpoints of the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class RealityScanFields:
    """Stores the fields returned by the XUI API for parsing."""

    PRIVATE_TARGET = "privateTarget"
    TLS_VERSION = "tlsVersion"
    CURVE_ID = "curveID"
    CERT_VALID = "certValid"
    CERT_CHAIN_VALID = "certChainValid"
    CERT_CHAIN_BYTES = "certChainBytes"
    CERT_SUBJECT = "certSubject"
    CERT_ISSUER = "certIssuer"
    NOT_AFTER = "notAfter"
    SERVER_NAMES = "serverNames"
    LATENCY_MS = "latencyMs"


class RealityScanResult(BaseModel):
    """Represents the verdict of a probe of a candidate REALITY target.

    Attributes:
        target (str): The probed target as it was requested.
        host (str): The host of the target.
        ip (str): The IP address of the target.
        port (int): The port of the target.
        feasible (bool): Whether the target can be used for REALITY.
        private_target (bool): Whether the target resolves to a private address.
        tls13 (bool): Whether the target supports TLS 1.3.
        tls_version (str): The negotiated TLS version.
        h2 (bool): Whether the target supports HTTP/2.
        alpn (str): The negotiated ALPN protocol.
        x25519 (bool): Whether the target supports X25519.
        curve_id (str): The negotiated key exchange curve.
        cert_valid (bool): Whether the certificate is trusted and matches the name.
        cert_chain_valid (bool): Whether the certificate chain is trusted, ignoring the name.
        cert_chain_bytes (int): The size of the presented certificate chain in bytes.
        cert_subject (str): The certificate subject.
        cert_issuer (str): The certificate issuer.
        not_after (str): The certificate expiration time, empty when there was no certificate.
        server_names (list[str] | None): The DNS names of the certificate, None when there are
            none.
        latency_ms (int): The latency of the probe in milliseconds.
        reason (str): The reason why the target is not feasible, if any.
    """

    target: str
    host: str
    ip: str
    port: int
    feasible: bool
    private_target: bool = Field(alias=RealityScanFields.PRIVATE_TARGET)  # type: ignore
    tls13: bool
    tls_version: str = Field(alias=RealityScanFields.TLS_VERSION)  # type: ignore
    h2: bool
    alpn: str
    x25519: bool
    curve_id: str = Field(alias=RealityScanFields.CURVE_ID)  # type: ignore
    cert_valid: bool = Field(alias=RealityScanFields.CERT_VALID)  # type: ignore
    cert_chain_valid: bool = Field(alias=RealityScanFields.CERT_CHAIN_VALID)  # type: ignore
    cert_chain_bytes: int = Field(alias=RealityScanFields.CERT_CHAIN_BYTES)  # type: ignore
    cert_subject: str = Field(alias=RealityScanFields.CERT_SUBJECT)  # type: ignore
    cert_issuer: str = Field(alias=RealityScanFields.CERT_ISSUER)  # type: ignore
    not_after: str = Field(alias=RealityScanFields.NOT_AFTER)  # type: ignore
    server_names: list[str] | None = Field(  # type: ignore
        default=None, alias=RealityScanFields.SERVER_NAMES
    )
    latency_ms: int = Field(alias=RealityScanFields.LATENCY_MS)  # type: ignore
    reason: str

    model_config = ConfigDict(populate_by_name=True)
