"""This module contains the model for the node descendants endpoint of the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class NodeSummaryFields:
    """Stores the fields returned by the XUI API for parsing."""

    PARENT_GUID = "parentGuid"
    LAST_HEARTBEAT = "lastHeartbeat"
    LATENCY_MS = "latencyMs"
    PANEL_VERSION = "panelVersion"
    XRAY_VERSION = "xrayVersion"
    XRAY_STATE = "xrayState"
    XRAY_ERROR = "xrayError"


class NodeSummary(BaseModel):
    """Represents a read-only summary of a node managed by the panel.

    Attributes:
        guid (str): The GUID of the node.
        parent_guid (str): The GUID of the parent panel.
        name (str): The name of the node.
        address (str): The address of the node.
        scheme (str): The scheme of the node API.
        port (int): The port of the node API.
        status (str): The status of the node.
        last_heartbeat (int): The last heartbeat, Unix time in seconds.
        latency_ms (int): The latency in milliseconds.
        panel_version (str): The panel version on the node.
        xray_version (str): The Xray version on the node.
        xray_state (str): The state of Xray on the node.
        xray_error (str): The Xray error on the node, if any.
    """

    guid: str
    parent_guid: str = Field(alias=NodeSummaryFields.PARENT_GUID)  # type: ignore
    name: str
    address: str
    scheme: str
    port: int
    status: str
    last_heartbeat: int = Field(alias=NodeSummaryFields.LAST_HEARTBEAT)  # type: ignore
    latency_ms: int = Field(alias=NodeSummaryFields.LATENCY_MS)  # type: ignore
    panel_version: str = Field(alias=NodeSummaryFields.PANEL_VERSION)  # type: ignore
    xray_version: str = Field(alias=NodeSummaryFields.XRAY_VERSION)  # type: ignore
    xray_state: str = Field(alias=NodeSummaryFields.XRAY_STATE)  # type: ignore
    xray_error: str = Field(default="", alias=NodeSummaryFields.XRAY_ERROR)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)
