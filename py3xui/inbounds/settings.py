from py3xui.clients.client import Client
from py3xui.inbounds.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class SettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    CLIENTS = "clients"
    DECRYPTION = "decryption"
    FALLBACKS = "fallbacks"


class Settings(JsonStringModel):
    clients: list[Client] = None
    decryption: str = None
    fallbacks: list = None
