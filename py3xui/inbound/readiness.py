"""This module contains the AmneziaWGReadiness class, which reports whether the panel host
can run kernel-mode AmneziaWG inbounds."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class AmneziaWGReadinessFields:
    """Stores the fields returned by the XUI API for parsing."""

    READY = "ready"
    BLOCKERS = "blockers"
    INSTALL_COMMAND = "installCommand"

    CODE = "code"
    DETAIL = "detail"


class AmneziaWGBlocker(BaseModel):
    """Represents one unmet host requirement for kernel-mode AmneziaWG.

    Attributes:
        code (str): The blocker code (e.g. "root", "tools", "module", "nft", "ipv6"). Required.
        detail (str): Additional details (e.g. the missing tool). Optional.
    """

    code: str
    detail: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
    )


class AmneziaWGReadiness(BaseModel):
    """Represents the host readiness for kernel-mode AmneziaWG inbounds.

    Attributes:
        ready (bool): Whether the host can run kernel-mode inbounds. Required.
        blockers (list[AmneziaWGBlocker]): The unmet requirements. Optional.
        install_command (str): The command that installs the kernel module. Optional.
    """

    ready: bool
    blockers: list[AmneziaWGBlocker] | None = []
    install_command: str = Field(  # type: ignore
        default="", alias=AmneziaWGReadinessFields.INSTALL_COMMAND
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )
