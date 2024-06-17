import json
import os

import pytest
import requests_mock

from py3xui import Api
from py3xui.api.api import ApiFields
from py3xui.clients.client import Client
from py3xui.inbounds.inbounds import Inbound
from py3xui.inbounds.sniffing import Sniffing
from py3xui.inbounds.stream_settings import StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alhtim2x"


def test_init():
    api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
    assert api.host == HOST, f"Expected {HOST}, got {api.host}"
    assert api.username == USERNAME, f"Expected {USERNAME}, got {api.username}"
    assert api.password == PASSWORD, f"Expected {PASSWORD}, got {api.password}"
    assert api.max_retries == 3, f"Expected 3, got {api.max_retries}"
    assert api.session is None, f"Expected None, got {api.session}"


def test_setters():
    api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
    api.max_retries = 5
    api.session = "abc123"
    assert api.max_retries == 5, f"Expected 5, got {api.max_retries}"
    assert api.session == "abc123", f"Expected abc123, got {api.session}"


def test_login_success():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: True}, cookies={"session": SESSION})
        api = Api(HOST, "username", "password", skip_login=True)
        api.login()
        assert api.session == {"session": SESSION}, f"Expected {SESSION}, got {api.session}"


def test_login_failed():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: True})
        api = Api(HOST, "username", "password", skip_login=True)
        with pytest.raises(ValueError):
            api.login()


def test_from_env():
    os.environ["XUI_HOST"] = HOST
    os.environ["XUI_USERNAME"] = USERNAME
    os.environ["XUI_PASSWORD"] = PASSWORD

    api = Api.from_env(skip_login=True)
    assert api.host == HOST, f"Expected {HOST}, got {api.host}"
    assert api.username == USERNAME, f"Expected {USERNAME}, got {api.username}"
    assert api.password == PASSWORD, f"Expected {PASSWORD}, got {api.password}"


def test_get_inbounds():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/list", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        inbounds = api.get_inbounds()
        assert len(inbounds) == 1, f"Expected 1, got {len(inbounds)}"
        inbound = inbounds[0]
        assert isinstance(inbound, Inbound), f"Expected Inbound, got {type(inbound)}"
        assert isinstance(
            inbound.stream_settings, StreamSettings
        ), f"Expected StreamSettings, got {type(inbound.stream_settings)}"
        assert isinstance(
            inbound.sniffing, Sniffing
        ), f"Expected Sniffing, got {type(inbound.sniffing)}"
        assert isinstance(
            inbound.client_stats[0], Client
        ), f"Expected ClientStats, got {type(inbound.client_stats[0])}"

        assert inbound.id == 1, f"Expected 1, got {inbound.id}"


def test_get_client():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/getClientTraffics/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        client = api.get_client(EMAIL)
        assert isinstance(client, Client), f"Expected Client, got {type(client)}"

        assert client.email == EMAIL, f"Expected {EMAIL}, got {client.email}"
        assert client.id == 1, f"Expected 1, got {client.id}"
        assert client.inbound_id == 1, f"Expected 1, got {client.inbound_id}"
