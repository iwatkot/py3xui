"""This module contains the models for the panel self-update endpoints of the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class PanelUpdateFields:
    """Stores the fields returned by the XUI API for parsing."""

    CURRENT_VERSION = "currentVersion"
    LATEST_VERSION = "latestVersion"
    CURRENT_COMMIT = "currentCommit"
    LATEST_COMMIT = "latestCommit"
    UPDATE_AVAILABLE = "updateAvailable"

    RUN_ID = "runId"
    EXIT_CODE = "exitCode"
    FINISHED_AT = "finishedAt"


class PanelUpdateInfo(BaseModel):
    """Represents the current and the latest version of the panel.

    Attributes:
        channel (str): The update channel: "stable" or "dev".
        current_version (str): The running version of the panel.
        latest_version (str): The latest version available in the channel.
        current_commit (str): The running commit, only set in the dev channel.
        latest_commit (str): The latest commit, only set in the dev channel.
        update_available (bool): Whether an update is available.
    """

    channel: str
    current_version: str = Field(alias=PanelUpdateFields.CURRENT_VERSION)  # type: ignore
    latest_version: str = Field(alias=PanelUpdateFields.LATEST_VERSION)  # type: ignore
    current_commit: str = Field(default="", alias=PanelUpdateFields.CURRENT_COMMIT)  # type: ignore
    latest_commit: str = Field(default="", alias=PanelUpdateFields.LATEST_COMMIT)  # type: ignore
    update_available: bool = Field(alias=PanelUpdateFields.UPDATE_AVAILABLE)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)


class PanelUpdateStatus(BaseModel):
    """Represents the outcome of the most recently launched panel self-update.

    Attributes:
        run_id (str): The ID of the update run, compare it with the result of `update_panel`.
        state (str): The state of the update: "pending", "success" or "failed".
        exit_code (int): The exit code of the updater.
        finished_at (int): The finish time, Unix time in seconds.
    """

    run_id: str = Field(alias=PanelUpdateFields.RUN_ID)  # type: ignore
    state: str
    exit_code: int = Field(alias=PanelUpdateFields.EXIT_CODE)  # type: ignore
    finished_at: int = Field(alias=PanelUpdateFields.FINISHED_AT)  # type: ignore

    model_config = ConfigDict(populate_by_name=True)
