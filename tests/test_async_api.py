import json
import os
import uuid
from unittest import mock

import httpx
import pytest
import respx
from aiohttp import ClientResponse
from aioresponses import aioresponses

from py3xui import AsyncApi, Client, Inbound
from py3xui.api.api_base import ApiFields
from py3xui.inbound import Settings, Sniffing, StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alhtim2x"


@pytest.mark.asyncio
async def test_get_client():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client.json")))

    with respx.mock:
        request = respx.get(f"{HOST}/panel/api/inbounds/getClientTraffics/{EMAIL}").respond(
            200, json=response_example
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        client = await api.client.get_by_email(EMAIL)

        assert request.called, "Mocked request was not called"
        assert isinstance(client, Client), f"Expected Client, got {type(client)}"
        assert client.email == EMAIL, f"Expected {EMAIL}, got {client.email}"
        assert client.id == 1, f"Expected 1, got {client.id}"
