"""This module contains the models for the server history, metrics and observatory endpoints of
the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class MetricsFields:
    """Stores the fields returned by the XUI API for parsing."""

    LAST_SEEN_TIME = "lastSeenTime"
    LAST_TRY_TIME = "lastTryTime"
    UPDATED_AT = "updatedAt"


class Fail2banStatus(BaseModel):
    """Represents the availability of Fail2ban, which per-client IP limits depend on.

    Attributes:
        enabled (bool): Whether Fail2ban support is enabled on the host.
        installed (bool): Whether Fail2ban is installed, only checked when it is enabled.
        usable (bool): Whether IP limits can be enforced on the host.
        windows (bool): Whether the host runs Windows.
    """

    enabled: bool
    installed: bool
    usable: bool
    windows: bool


class HistoryPoint(BaseModel):
    """Represents one aggregated point of a metric history.

    Attributes:
        t (int): The start of the bucket, Unix time in seconds.
        v (float): The mean value of the metric in the bucket.
    """

    t: int
    v: float


class CpuHistoryPoint(BaseModel):
    """Represents one aggregated point of the legacy CPU history.

    Attributes:
        t (int): The start of the bucket, Unix time in seconds.
        cpu (float): The mean CPU usage in the bucket, in percent.
    """

    t: int
    cpu: float


class XrayMetricsState(BaseModel):
    """Represents the state of the Xray runtime metrics collection.

    Attributes:
        enabled (bool): Whether the metrics are being collected.
        listen (str): The address of the Xray metrics listener.
        reason (str): The reason why the metrics are not collected, if any.
    """

    enabled: bool
    listen: str
    reason: str = ""


class ObservatorySnapshot(BaseModel):
    """Represents the latest Xray observatory result for one outbound.

    Attributes:
        tag (str): The outbound tag.
        alive (bool): Whether the outbound passed the last probe.
        delay (int): The measured delay in milliseconds.
        last_seen_time (int): The last successful probe, Unix time in seconds.
        last_try_time (int): The last probe, Unix time in seconds.
        updated_at (int): The time the snapshot was updated, Unix time in seconds.
    """

    tag: str
    alive: bool
    delay: int
    last_seen_time: int = Field(alias=MetricsFields.LAST_SEEN_TIME)  # type: ignore
    last_try_time: int = Field(alias=MetricsFields.LAST_TRY_TIME)  # type: ignore
    updated_at: int = Field(alias=MetricsFields.UPDATED_AT)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)
