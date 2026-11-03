"""This module contains the ApiToken class which represents an API token in the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class ApiTokenFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    NAME = "name"
    TOKEN = "token"
    ENABLED = "enabled"
    CREATED_AT = "createdAt"
    SCOPE = "scope"
    EXPIRES_AT = "expiresAt"


class ApiToken(BaseModel):
    """Represents an API token in the XUI API.

    Attributes:
        id (int): The ID of the token. Required.
        name (str): The name of the token. Required.
        token (str): The token value. The panel returns it only once, from
            `add_api_token()`, and leaves it blank in `get_api_tokens()`. Optional.
        enabled (bool): Whether the token is enabled. Required.
        created_at (int): The creation time in Unix seconds. Required.
        scope (str): The scope of the token: `admin`, `monitor`, `node-sync` or
            `node-admin`. Required.
        expires_at (int): The expiry time in Unix milliseconds, 0 for no expiry. Required.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    token: str = ""
    enabled: bool
    created_at: int = Field(alias=ApiTokenFields.CREATED_AT)  # type: ignore
    scope: str
    expires_at: int = Field(alias=ApiTokenFields.EXPIRES_AT)  # type: ignore
