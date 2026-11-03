"""Tests for XrayApi."""

import json
from urllib.parse import parse_qs, urlsplit

import pytest
import requests_mock

from py3xui import Api, GeodataSource, OutboundTraffic, XraySettings
from py3xui.api import XrayApi

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
BASE = f"{HOST}/panel/api/xray"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
OK = {"success": True, "msg": "", "obj": ""}


@pytest.fixture(name="m")
def fixture_m():
    with requests_mock.Mocker() as mocker:
        yield mocker


@pytest.fixture(name="api")
def fixture_api() -> Api:
    api = Api(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def load(name):
    with open(f"{RESPONSES_DIR}/xray_{name}.json", encoding="utf-8") as file:
        return json.load(file)


def mock(m, method, path, payload=None):
    m.register_uri(method, f"{BASE}/{path}", json=OK if payload is None else payload)


def check(m, method, path):
    request = m.last_request
    assert request.method == method
    assert request.url.split("?", maxsplit=1)[0] == f"{BASE}/{path}"


def form(m):
    request = m.last_request
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    return parse_qs(request.text)


def query(m):
    return parse_qs(urlsplit(m.last_request.url).query)


# --- tests ---
def test_facade_propagates_auth():
    api = Api(HOST, USERNAME, PASSWORD)
    assert isinstance(api.xray, XrayApi)

    api.session = SESSION
    api.csrf_token = "csrf"
    api.cookie_name = "3x-ui"

    assert api.xray.session == SESSION
    assert api.xray.csrf_token == "csrf"
    assert api.xray.cookie_name == "3x-ui"


def test_get_settings(m, api):
    mock(m, "POST", "", load("settings"))

    settings = api.xray.get_settings()

    check(m, "POST", "")
    assert isinstance(settings, XraySettings)
    assert settings.xray_setting["outbounds"][0]["tag"] == "direct"
    assert settings.inbound_tags == ["in-443-tcp"]
    assert settings.client_reverse_tags == []
    assert settings.outbound_test_url == "https://www.google.com/generate_204"
    assert settings.geodata_sources == [
        GeodataSource(
            url="https://github.com/v2fly/geoip/releases/latest/download/geoip.dat",
            file="geoip.dat",
        )
    ]
    assert settings.subscription_outbounds == [{"tag": "sub1-vless", "protocol": "vless"}]
    assert settings.subscription_outbound_tags == ["sub1-vless"]


def test_get_default_config(m, api):
    mock(m, "GET", "getDefaultJsonConfig", load("default_config"))

    config = api.xray.get_default_config()

    check(m, "GET", "getDefaultJsonConfig")
    assert config["log"]["loglevel"] == "warning"


def test_get_outbounds_traffic(m, api):
    mock(m, "GET", "getOutboundsTraffic", load("outbounds_traffic"))

    traffic = api.xray.get_outbounds_traffic()

    check(m, "GET", "getOutboundsTraffic")
    assert traffic == [OutboundTraffic(id=1, tag="direct", up=100, down=200, total=300)]


def test_get_result(m, api):
    mock(m, "GET", "getXrayResult", {"success": True, "msg": "", "obj": "exit status 1"})

    result = api.xray.get_result()

    check(m, "GET", "getXrayResult")
    assert result == "exit status 1"


def test_update(m, api):
    mock(m, "POST", "update")

    result = api.xray.update('{"log":{}}', "https://example.com/204")

    check(m, "POST", "update")
    assert form(m) == {
        "xraySetting": ['{"log":{}}'],
        "outboundTestUrl": ["https://example.com/204"],
    }
    assert result is None


def test_update_without_test_url(m, api):
    mock(m, "POST", "update")

    api.xray.update('{"log":{}}')

    assert form(m) == {"xraySetting": ['{"log":{}}']}


def test_reset_outbound_stats(m, api):
    mock(m, "POST", "resetOutboundsTraffic")

    result = api.xray.reset_outbound_stats("direct")

    check(m, "POST", "resetOutboundsTraffic")
    assert form(m) == {"tag": ["direct"]}
    assert result is None
