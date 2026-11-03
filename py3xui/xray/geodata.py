"""This module contains the models of the geo databases in the XUI API."""

from pydantic import BaseModel, ConfigDict, Field

from py3xui.xray.xray import StrList


# pylint: disable=too-few-public-methods
class GeodataFields:
    """Stores the fields returned by the XUI API for parsing."""

    NAME = "name"
    KIND = "kind"
    SIZE = "size"
    MODIFIED_AT = "modifiedAt"
    CATEGORIES = "categories"
    ERROR = "error"

    CODE = "code"
    ENTRIES = "entries"
    ATTRIBUTES = "attributes"

    VALUE = "value"

    TOTAL = "total"
    ITEMS = "items"

    TOKEN = "token"
    REASON = "reason"
    FILE = "file"


class GeoFile(BaseModel):
    """Represents a geo database (.dat file) in the Xray asset folder.

    Attributes:
        name (str): The name of the file.
        kind (str): The layout detected from the contents ("site" or "ip").
        size (int): The size of the file in bytes.
        modified_at (int): The modification time in milliseconds.
        categories (int): The number of the categories.
        error (str): The reason why the file failed to parse.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(alias=GeodataFields.NAME)  # type: ignore
    kind: str = Field(default="", alias=GeodataFields.KIND)  # type: ignore
    size: int = Field(default=0, alias=GeodataFields.SIZE)  # type: ignore
    modified_at: int = Field(default=0, alias=GeodataFields.MODIFIED_AT)  # type: ignore
    categories: int = Field(default=0, alias=GeodataFields.CATEGORIES)  # type: ignore
    error: str = Field(default="", alias=GeodataFields.ERROR)  # type: ignore


class GeoCategory(BaseModel):
    """Represents one code inside a geo database, such as geosite's "google".

    Attributes:
        code (str): The code of the category.
        entries (int): The number of the entries.
        attributes (list[str]): The attributes the domains of the category carry.
    """

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(alias=GeodataFields.CODE)  # type: ignore
    entries: int = Field(default=0, alias=GeodataFields.ENTRIES)  # type: ignore
    attributes: StrList = Field(default=[], alias=GeodataFields.ATTRIBUTES)  # type: ignore


class GeoCategoryPage(BaseModel):
    """Represents one page of the categories plus the unpaged total.

    Attributes:
        total (int): The unpaged number of the categories.
        items (list[GeoCategory]): The categories of the page.
    """

    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(default=0, alias=GeodataFields.TOTAL)  # type: ignore
    items: list[GeoCategory] = Field(default=[], alias=GeodataFields.ITEMS)  # type: ignore


class GeoEntry(BaseModel):
    """Represents a single rule inside a category: a domain rule for geosite databases, a CIDR for
    geoip ones.

    Attributes:
        kind (str): The kind of the rule.
        value (str): The value of the rule.
    """

    model_config = ConfigDict(populate_by_name=True)

    kind: str = Field(alias=GeodataFields.KIND)  # type: ignore
    value: str = Field(alias=GeodataFields.VALUE)  # type: ignore


class GeoEntryPage(BaseModel):
    """Represents one page of the entries of a category plus the unpaged total.

    Attributes:
        total (int): The unpaged number of the entries.
        items (list[GeoEntry]): The entries of the page.
    """

    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(default=0, alias=GeodataFields.TOTAL)  # type: ignore
    items: list[GeoEntry] = Field(default=[], alias=GeodataFields.ITEMS)  # type: ignore


class GeodataTokenIssue(BaseModel):
    """Represents a routing token the running core would reject or would silently match nothing
    against.

    Attributes:
        token (str): The routing token.
        reason (str): The reason: "syntax", "fileMissing", "categoryMissing", "attributeMissing"
            or "wrongKind".
        file (str): The name of the database file.
        code (str): The code of the category.
    """

    model_config = ConfigDict(populate_by_name=True)

    token: str = Field(alias=GeodataFields.TOKEN)  # type: ignore
    reason: str = Field(alias=GeodataFields.REASON)  # type: ignore
    file: str = Field(default="", alias=GeodataFields.FILE)  # type: ignore
    code: str = Field(default="", alias=GeodataFields.CODE)  # type: ignore
