"""This module contains the models of the Private Internet Access integration in the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class PiaFields:
    """Stores the fields returned by the XUI API for parsing."""

    USERNAME = "username"
    ACCOUNT_HINT = "accountHint"

    CODE = "code"

    ID = "id"
    NAME = "name"

    HOSTNAME = "hostname"
    IP = "ip"
    REGION_ID = "regionId"
    REGION_NAME = "regionName"

    REGIONS = "regions"
    SERVERS = "servers"

    TAG = "tag"
    SECRET_KEY = "secretKey"
    ADDRESS = "address"
    PUBLIC_KEY = "publicKey"
    ENDPOINT = "endpoint"


class PiaAccount(BaseModel):
    """Represents the signed in PIA account.

    Attributes:
        username (str): The username of the account.
        account_hint (str): The masked account name shown in the panel.
    """

    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(alias=PiaFields.USERNAME)  # type: ignore
    account_hint: str = Field(default="", alias=PiaFields.ACCOUNT_HINT)  # type: ignore


class PiaCountry(BaseModel):
    """Represents a country with PIA servers.

    Attributes:
        code (str): The country code.
    """

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(alias=PiaFields.CODE)  # type: ignore


class PiaRegion(BaseModel):
    """Represents a PIA region.

    Attributes:
        id (str): The ID of the region.
        name (str): The name of the region.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias=PiaFields.ID)  # type: ignore
    name: str = Field(alias=PiaFields.NAME)  # type: ignore


class PiaServer(BaseModel):
    """Represents a PIA WireGuard server.

    Attributes:
        hostname (str): The hostname of the server.
        ip (str): The IP address of the server.
        region_id (str): The ID of the region.
        region_name (str): The name of the region.
    """

    model_config = ConfigDict(populate_by_name=True)

    hostname: str = Field(alias=PiaFields.HOSTNAME)  # type: ignore
    ip: str = Field(alias=PiaFields.IP)  # type: ignore
    region_id: str = Field(alias=PiaFields.REGION_ID)  # type: ignore
    region_name: str = Field(alias=PiaFields.REGION_NAME)  # type: ignore


class PiaServers(BaseModel):
    """Represents the PIA regions and servers of a country.

    Attributes:
        regions (list[PiaRegion]): The regions of the country.
        servers (list[PiaServer]): The servers of the country.
    """

    model_config = ConfigDict(populate_by_name=True)

    regions: list[PiaRegion] = Field(default=[], alias=PiaFields.REGIONS)  # type: ignore
    servers: list[PiaServer] = Field(default=[], alias=PiaFields.SERVERS)  # type: ignore


class PiaKey(BaseModel):
    """Represents a WireGuard key registered on a PIA server.

    Attributes:
        tag (str): The suggested tag of the outbound.
        hostname (str): The hostname of the server.
        secret_key (str): The generated private key.
        address (str): The address assigned to the peer.
        public_key (str): The public key of the server.
        endpoint (str): The endpoint of the server.
    """

    model_config = ConfigDict(populate_by_name=True)

    tag: str = Field(alias=PiaFields.TAG)  # type: ignore
    hostname: str = Field(alias=PiaFields.HOSTNAME)  # type: ignore
    secret_key: str = Field(alias=PiaFields.SECRET_KEY)  # type: ignore
    address: str = Field(alias=PiaFields.ADDRESS)  # type: ignore
    public_key: str = Field(alias=PiaFields.PUBLIC_KEY)  # type: ignore
    endpoint: str = Field(alias=PiaFields.ENDPOINT)  # type: ignore
