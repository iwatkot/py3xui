"""This module contains the OutboundSub class which represents an outbound subscription in the
XUI API."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class OutboundSubFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    REMARK = "remark"
    URL = "url"
    ENABLED = "enabled"
    ALLOW_PRIVATE = "allowPrivate"
    ALLOW_INSECURE = "allowInsecure"
    USER_AGENT = "userAgent"
    TAG_PREFIX = "tagPrefix"
    UPDATE_INTERVAL = "updateInterval"
    PRIORITY = "priority"
    PREPEND = "prepend"
    LAST_UPDATED = "lastUpdated"
    LAST_ERROR = "lastError"
    LAST_FETCHED_OUTBOUNDS = "lastFetchedOutbounds"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"
    OUTBOUND_COUNT = "outboundCount"


# The fields the panel manages by itself, it doesn't read them on create and update.
PANEL_MANAGED_FIELDS = {
    "id",
    "priority",
    "last_updated",
    "last_error",
    "last_fetched_outbounds",
    "created_at",
    "updated_at",
    "outbound_count",
}


class OutboundSub(BaseModel):
    """Represents an outbound subscription: a remote URL which supplies additional outbounds.

    The defaults of the editable fields match the values the panel uses for absent form fields.

    Attributes:
        id (int): The ID of the subscription.
        remark (str): The display label.
        url (str): The URL of the subscription.
        enabled (bool): Whether the subscription is active.
        allow_private (bool): Whether to allow a private or loopback address.
        allow_insecure (bool): Whether to skip the TLS certificate verification.
        user_agent (str): The User-Agent used to fetch the URL.
        tag_prefix (str): The prefix of the generated outbound tags. The panel assigns
            a free one when it's empty.
        update_interval (int): The number of seconds between the refreshes.
        priority (int): The position among the subscriptions.
        prepend (bool): Whether to place the outbounds before the template outbounds.
        last_updated (int): The time of the last refresh.
        last_error (str): The error of the last refresh.
        last_fetched_outbounds (str): The last fetched outbounds as a JSON string.
            The list of the subscriptions leaves it empty, see outbound_count.
        created_at (int): The creation time in milliseconds.
        updated_at (int): The modification time in milliseconds.
        outbound_count (int): The number of the fetched outbounds.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: int = Field(default=0, alias=OutboundSubFields.ID)  # type: ignore
    remark: str = Field(default="", alias=OutboundSubFields.REMARK)  # type: ignore
    url: str = Field(alias=OutboundSubFields.URL)  # type: ignore
    enabled: bool = Field(default=True, alias=OutboundSubFields.ENABLED)  # type: ignore
    allow_private: bool = Field(  # type: ignore
        default=False, alias=OutboundSubFields.ALLOW_PRIVATE
    )
    allow_insecure: bool = Field(  # type: ignore
        default=False, alias=OutboundSubFields.ALLOW_INSECURE
    )
    user_agent: str = Field(default="", alias=OutboundSubFields.USER_AGENT)  # type: ignore
    tag_prefix: str = Field(default="", alias=OutboundSubFields.TAG_PREFIX)  # type: ignore
    update_interval: int = Field(  # type: ignore
        default=600, alias=OutboundSubFields.UPDATE_INTERVAL
    )
    priority: int = Field(default=0, alias=OutboundSubFields.PRIORITY)  # type: ignore
    prepend: bool = Field(default=False, alias=OutboundSubFields.PREPEND)  # type: ignore
    last_updated: int = Field(default=0, alias=OutboundSubFields.LAST_UPDATED)  # type: ignore
    last_error: str = Field(default="", alias=OutboundSubFields.LAST_ERROR)  # type: ignore
    last_fetched_outbounds: str = Field(  # type: ignore
        default="", alias=OutboundSubFields.LAST_FETCHED_OUTBOUNDS
    )
    created_at: int = Field(default=0, alias=OutboundSubFields.CREATED_AT)  # type: ignore
    updated_at: int = Field(default=0, alias=OutboundSubFields.UPDATED_AT)  # type: ignore
    outbound_count: int = Field(default=0, alias=OutboundSubFields.OUTBOUND_COUNT)  # type: ignore

    def to_form_fields(self) -> dict[str, Any]:
        """Returns the form fields of the create and update requests. The fields which the panel
        manages by itself are left out. Fields with the default values are left out too because
        the panel applies the same defaults.

        Returns:
            dict[str, Any]: The form fields."""
        return self.model_dump(
            by_alias=True, exclude_defaults=True, exclude=PANEL_MANAGED_FIELDS
        )
