"""Tests for XrayApi."""

import json
from urllib.parse import parse_qs, urlsplit

import pytest
import requests_mock

from py3xui import (
    Api,
    GeodataSource,
    OutboundTraffic,
    PiaAccount,
    PiaCountry,
    PiaKey,
    PiaServers,
    XraySettings,
)
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


def test_warp_get_data(m, api):
    mock(m, "POST", "warp/data", load("warp_data"))

    data = api.xray.warp_get_data()

    check(m, "POST", "warp/data")
    assert data["device_id"] == "fake-device-id"


def test_warp_get_data_empty(m, api):
    mock(m, "POST", "warp/data")

    assert api.xray.warp_get_data() == {}


def test_warp_delete(m, api):
    mock(m, "POST", "warp/del")

    result = api.xray.warp_delete()

    check(m, "POST", "warp/del")
    assert result is None


def test_warp_get_config(m, api):
    mock(m, "POST", "warp/config", load("warp_config"))

    config = api.xray.warp_get_config()

    check(m, "POST", "warp/config")
    assert config["id"] == "fake-device-id"


def test_warp_register(m, api):
    mock(m, "POST", "warp/reg", load("warp_register"))

    result = api.xray.warp_register("fake-private-key", "fake-public-key")

    check(m, "POST", "warp/reg")
    assert form(m) == {
        "privateKey": ["fake-private-key"],
        "publicKey": ["fake-public-key"],
    }
    assert result["data"]["private_key"] == "fake-private-key"
    assert result["config"]["id"] == "fake-device-id"


def test_warp_register_masque(m, api):
    mock(m, "POST", "warp/regMasque", load("warp_masque"))

    result = api.xray.warp_register_masque()

    check(m, "POST", "warp/regMasque")
    assert result["publicKey"] == "fake-public-key"
    assert result["address"] == ["172.16.0.2/32", "2606:4700::2/128"]


def test_warp_change_ip(m, api):
    mock(m, "POST", "warp/changeIp", load("warp_change_ip"))

    result = api.xray.warp_change_ip()

    check(m, "POST", "warp/changeIp")
    assert result["data"]["device_id"] == "fake-device-id"
    assert "warning" in result


def test_warp_set_license(m, api):
    mock(m, "POST", "warp/license", load("warp_data"))

    data = api.xray.warp_set_license("fake-license")

    check(m, "POST", "warp/license")
    assert form(m) == {"license": ["fake-license"]}
    assert data["license_key"] == "fake-license"


def test_warp_set_interval(m, api):
    mock(m, "POST", "warp/interval")

    result = api.xray.warp_set_interval(24)

    check(m, "POST", "warp/interval")
    assert form(m) == {"interval": ["24"]}
    assert result is None


def test_warp_set_interval_zero_is_sent(m, api):
    mock(m, "POST", "warp/interval")

    api.xray.warp_set_interval(0)

    assert form(m) == {"interval": ["0"]}


def test_nord_get_countries(m, api):
    mock(m, "POST", "nord/countries", load("nord_countries"))

    countries = api.xray.nord_get_countries()

    check(m, "POST", "nord/countries")
    assert countries == [{"id": 1, "name": "Albania", "code": "AL"}]


def test_nord_get_servers(m, api):
    mock(m, "POST", "nord/servers", load("nord_servers"))

    servers = api.xray.nord_get_servers(1)

    check(m, "POST", "nord/servers")
    assert form(m) == {"countryId": ["1"]}
    assert servers["servers"][0]["hostname"] == "al1.example.com"
    assert servers["locations"][0]["id"] == 5


def test_nord_register(m, api):
    mock(m, "POST", "nord/reg", load("nord_data"))

    data = api.xray.nord_register("fake-token")

    check(m, "POST", "nord/reg")
    assert form(m) == {"token": ["fake-token"]}
    assert data == {"private_key": "fake-private-key", "token": "fake-token"}


def test_nord_set_key(m, api):
    mock(m, "POST", "nord/setKey", load("nord_data"))

    data = api.xray.nord_set_key("fake-private-key")

    check(m, "POST", "nord/setKey")
    assert form(m) == {"key": ["fake-private-key"]}
    assert data["private_key"] == "fake-private-key"


def test_nord_get_data(m, api):
    mock(m, "POST", "nord/data", load("nord_data"))

    data = api.xray.nord_get_data()

    check(m, "POST", "nord/data")
    assert data["token"] == "fake-token"


def test_nord_get_data_empty(m, api):
    mock(m, "POST", "nord/data")

    assert api.xray.nord_get_data() == {}


def test_nord_delete(m, api):
    mock(m, "POST", "nord/del")

    result = api.xray.nord_delete()

    check(m, "POST", "nord/del")
    assert result is None


def test_pia_get_countries(m, api):
    mock(m, "POST", "pia/countries", load("pia_countries"))

    countries = api.xray.pia_get_countries()

    check(m, "POST", "pia/countries")
    assert countries == [PiaCountry(code="AL"), PiaCountry(code="US")]


def test_pia_get_servers(m, api):
    mock(m, "POST", "pia/servers", load("pia_servers"))

    servers = api.xray.pia_get_servers("US")

    check(m, "POST", "pia/servers")
    assert form(m) == {"countryCode": ["US"]}
    assert isinstance(servers, PiaServers)
    assert servers.regions[0].name == "US East"
    assert servers.servers[0].region_id == "us_east"


def test_pia_register(m, api):
    mock(m, "POST", "pia/reg", load("pia_account"))

    account = api.xray.pia_register("fake-user", "fake-password")

    check(m, "POST", "pia/reg")
    assert form(m) == {"username": ["fake-user"], "password": ["fake-password"]}
    assert account == PiaAccount(username="fake-user", account_hint="fa***")


def test_pia_get_data(m, api):
    mock(m, "POST", "pia/data", load("pia_account"))

    account = api.xray.pia_get_data()

    check(m, "POST", "pia/data")
    assert account == PiaAccount(username="fake-user", account_hint="fa***")


def test_pia_get_data_without_account(m, api):
    mock(m, "POST", "pia/data", {"success": True, "msg": "", "obj": None})

    assert api.xray.pia_get_data() is None


def test_pia_delete(m, api):
    mock(m, "POST", "pia/del", {"success": True, "msg": "", "obj": None})

    result = api.xray.pia_delete()

    check(m, "POST", "pia/del")
    assert result is None


def test_pia_add_key(m, api):
    mock(m, "POST", "pia/addKey", load("pia_key"))

    key = api.xray.pia_add_key("server.example.com")

    check(m, "POST", "pia/addKey")
    assert form(m) == {"hostname": ["server.example.com"]}
    assert isinstance(key, PiaKey)
    assert key.secret_key == "fake-secret-key"
    assert key.endpoint == "192.0.2.1:1337"
