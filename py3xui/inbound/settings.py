"""This module contains the Settings class, which is used to parse the JSON response
from the XUI API."""

from py3xui.client.client import Client
from py3xui.inbound.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class SettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    CLIENTS = "clients"
    DECRYPTION = "decryption"
    FALLBACKS = "fallbacks"


class Settings(JsonStringModel):
    """Represents the settings for an inbound connection.

    Attributes:
        clients (list[Client]): The clients for the inbound connection. Optional.
        decryption (str): The decryption method for the inbound connection. Optional.
        fallbacks (list): The fallbacks for the inbound connection. Optional.
    """

    clients: list[Client] = []
    decryption: str = ""
    fallbacks: list = []
