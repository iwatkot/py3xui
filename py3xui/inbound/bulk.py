"""This module contains the result classes of the bulk delete operations on inbounds."""

from pydantic import BaseModel, ConfigDict


# pylint: disable=too-few-public-methods
class InboundBulkDeleteFields:
    """Stores the fields returned by the XUI API for parsing."""

    DELETED = "deleted"
    SKIPPED = "skipped"

    ID = "id"
    EMAIL = "email"
    REASON = "reason"


class InboundBulkDeleteReport(BaseModel):
    """Represents an inbound that could not be deleted.

    Attributes:
        id (int): The ID of the inbound. Required.
        reason (str): The reason why the inbound was skipped. Optional.
    """

    id: int
    reason: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
    )


class InboundBulkDeleteResult(BaseModel):
    """Represents the result of a bulk delete of inbounds.

    Attributes:
        deleted (int): The number of deleted inbounds. Optional.
        skipped (list[InboundBulkDeleteReport]): The inbounds that were not deleted. Optional.
    """

    deleted: int = 0
    skipped: list[InboundBulkDeleteReport] | None = []

    model_config = ConfigDict(
        populate_by_name=True,
    )


class InboundClientsDeleteReport(BaseModel):
    """Represents a client that could not be deleted from an inbound.

    Attributes:
        email (str): The email of the client. Required.
        reason (str): The reason why the client was skipped. Optional.
    """

    email: str
    reason: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
    )


class InboundClientsDeleteResult(BaseModel):
    """Represents the result of deleting all clients of an inbound.

    Attributes:
        deleted (int): The number of deleted clients. Optional.
        skipped (list[InboundClientsDeleteReport]): The clients that were not deleted. Optional.
    """

    deleted: int = 0
    skipped: list[InboundClientsDeleteReport] | None = []

    model_config = ConfigDict(
        populate_by_name=True,
    )
