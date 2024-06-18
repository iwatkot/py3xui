from py3xui.clients.client import Client
from py3xui.inbounds.bases import JsonStringModel


# pylint: disable=too-few-public-methods
class SettingsFields:
    """Stores the fields returned by the XUI API for parsing."""

    CLIENTS = "clients"
    DECRYPTION = "decryption"
    FALLBACKS = "fallbacks"


class Settings(JsonStringModel):
    clients: list[Client]
    decryption: str
    fallbacks: list

    def __repr__(self) -> str:
        return (
            f"Settings(clients={self.clients}, decryption={self.decryption}, "
            f"fallbacks={self.fallbacks})"
        )
