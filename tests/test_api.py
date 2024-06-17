import json
import os

import pytest
import requests_mock

from py3xui import Api
from py3xui.api.api import ApiFields
from py3xui.clients.client_stats import ClientStats
from py3xui.inbounds.inbounds import Inbound
from py3xui.inbounds.sniffing import Sniffing
from py3xui.inbounds.stream_settings import StreamSettings

RESPONSES_DIR = "tests/responses"


def test_init():
    host = "http://localhost"
    username = "admin"
    password = "admin"
    api = Api(host, username, password, skip_login=True)
    assert api.host == host, f"Expected {host}, got {api.host}"
    assert api.username == username, f"Expected {username}, got {api.username}"
    assert api.password == password, f"Expected {password}, got {api.password}"
    assert api.max_retries == 3, f"Expected 3, got {api.max_retries}"
    assert api.session is None, f"Expected None, got {api.session}"


def test_setters():
    host = "http://localhost"
    username = "admin"
    password = "admin"
    api = Api(host, username, password, skip_login=True)
    api.max_retries = 5
    api.session = "abc123"
    assert api.max_retries == 5, f"Expected 5, got {api.max_retries}"
    assert api.session == "abc123", f"Expected abc123, got {api.session}"


def test_login_success():
    session = "abc123"
    host = "http://localhost"
    with requests_mock.Mocker() as m:
        m.post(f"{host}/login", json={ApiFields.SUCCESS: True}, cookies={"session": session})
        api = Api(host, "username", "password", skip_login=True)
        api.login()
        assert api.session == {"session": session}, f"Expected {session}, got {api.session}"


def test_login_failed():
    host = "http://localhost"
    with requests_mock.Mocker() as m:
        m.post(f"{host}/login", json={ApiFields.SUCCESS: True})
        api = Api(host, "username", "password", skip_login=True)
        with pytest.raises(ValueError):
            api.login()


def test_from_env():
    os.environ["XUI_HOST"] = "http://localhost"
    os.environ["XUI_USERNAME"] = "admin"
    os.environ["XUI_PASSWORD"] = "admin"

    api = Api.from_env(skip_login=True)
    assert api.host == "http://localhost", f"Expected http://localhost, got {api.host}"
    assert api.username == "admin", f"Expected admin, got {api.username}"
    assert api.password == "admin", f"Expected admin, got {api.password}"


def test_get_inbounds():
    host = "http://localhost"
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{host}/panel/api/inbounds/list", json=response_example)
        api = Api(host, "username", "password", skip_login=True)
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
            inbound.client_stats[0], ClientStats
        ), f"Expected ClientStats, got {type(inbound.client_stats[0])}"

        assert inbound.id == 1, f"Expected 1, got {inbound.id}"
