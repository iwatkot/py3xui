"""Tests for AsyncXrayApi."""

import json
import re
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from py3xui import (
    AsyncApi,
    GeodataSource,
    OutboundTraffic,
    PiaAccount,
    PiaCountry,
    PiaKey,
    PiaServers,
    XraySettings,
)
from py3xui.async_api import AsyncXrayApi

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
BASE = f"{HOST}/panel/api/xray"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
OK = {"success": True, "msg": "", "obj": ""}


@pytest.fixture(name="m")
def fixture_m(httpx_mock: HTTPXMock) -> HTTPXMock:
    return httpx_mock


@pytest.fixture(name="api")
def fixture_api() -> AsyncApi:
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def load(name):
    with open(f"{RESPONSES_DIR}/xray_{name}.json", encoding="utf-8") as file:
        return json.load(file)


def mock(m, method, path, payload=None):
    url = re.compile(re.escape(f"{BASE}/{path}") + r"(\?.*)?$")
    m.add_response(method=method, url=url, json=OK if payload is None else payload)


def check(m, method, path):
    request = m.get_requests()[-1]
    assert request.method == method
    assert str(request.url).split("?", maxsplit=1)[0] == f"{BASE}/{path}"


def form(m):
    request = m.get_requests()[-1]
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    return parse_qs(request.content.decode())


def query(m):
    return parse_qs(m.get_requests()[-1].url.query.decode())


# --- tests ---
@pytest.mark.asyncio
async def test_facade_propagates_auth():
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    assert isinstance(api.xray, AsyncXrayApi)

    api.session = SESSION
    api.csrf_token = "csrf"
    api.cookie_name = "3x-ui"

    assert api.xray.session == SESSION
    assert api.xray.csrf_token == "csrf"
    assert api.xray.cookie_name == "3x-ui"


@pytest.mark.asyncio
async def test_get_settings(m, api):
    mock(m, "POST", "", load("settings"))

    settings = await api.xray.get_settings()

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


@pytest.mark.asyncio
async def test_get_default_config(m, api):
    mock(m, "GET", "getDefaultJsonConfig", load("default_config"))

    config = await api.xray.get_default_config()

    check(m, "GET", "getDefaultJsonConfig")
    assert config["log"]["loglevel"] == "warning"


@pytest.mark.asyncio
async def test_get_outbounds_traffic(m, api):
    mock(m, "GET", "getOutboundsTraffic", load("outbounds_traffic"))

    traffic = await api.xray.get_outbounds_traffic()

    check(m, "GET", "getOutboundsTraffic")
    assert traffic == [OutboundTraffic(id=1, tag="direct", up=100, down=200, total=300)]


@pytest.mark.asyncio
async def test_get_result(m, api):
    mock(m, "GET", "getXrayResult", {"success": True, "msg": "", "obj": "exit status 1"})

    result = await api.xray.get_result()

    check(m, "GET", "getXrayResult")
    assert result == "exit status 1"


@pytest.mark.asyncio
async def test_update(m, api):
    mock(m, "POST", "update")

    result = await api.xray.update('{"log":{}}', "https://example.com/204")

    check(m, "POST", "update")
    assert form(m) == {
        "xraySetting": ['{"log":{}}'],
        "outboundTestUrl": ["https://example.com/204"],
    }
    assert result is None


@pytest.mark.asyncio
async def test_update_without_test_url(m, api):
    mock(m, "POST", "update")

    await api.xray.update('{"log":{}}')

    assert form(m) == {"xraySetting": ['{"log":{}}']}


@pytest.mark.asyncio
async def test_reset_outbound_stats(m, api):
    mock(m, "POST", "resetOutboundsTraffic")

    result = await api.xray.reset_outbound_stats("direct")

    check(m, "POST", "resetOutboundsTraffic")
    assert form(m) == {"tag": ["direct"]}
    assert result is None


@pytest.mark.asyncio
async def test_warp_get_data(m, api):
    mock(m, "POST", "warp/data", load("warp_data"))

    data = await api.xray.warp_get_data()

    check(m, "POST", "warp/data")
    assert data["device_id"] == "fake-device-id"


@pytest.mark.asyncio
async def test_warp_get_data_empty(m, api):
    mock(m, "POST", "warp/data")

    assert await api.xray.warp_get_data() == {}


@pytest.mark.asyncio
async def test_warp_delete(m, api):
    mock(m, "POST", "warp/del")

    result = await api.xray.warp_delete()

    check(m, "POST", "warp/del")
    assert result is None


@pytest.mark.asyncio
async def test_warp_get_config(m, api):
    mock(m, "POST", "warp/config", load("warp_config"))

    config = await api.xray.warp_get_config()

    check(m, "POST", "warp/config")
    assert config["id"] == "fake-device-id"


@pytest.mark.asyncio
async def test_warp_register(m, api):
    mock(m, "POST", "warp/reg", load("warp_register"))

    result = await api.xray.warp_register("fake-private-key", "fake-public-key")

    check(m, "POST", "warp/reg")
    assert form(m) == {
        "privateKey": ["fake-private-key"],
        "publicKey": ["fake-public-key"],
    }
    assert result["data"]["private_key"] == "fake-private-key"
    assert result["config"]["id"] == "fake-device-id"


@pytest.mark.asyncio
async def test_warp_register_masque(m, api):
    mock(m, "POST", "warp/regMasque", load("warp_masque"))

    result = await api.xray.warp_register_masque()

    check(m, "POST", "warp/regMasque")
    assert result["publicKey"] == "fake-public-key"
    assert result["address"] == ["172.16.0.2/32", "2606:4700::2/128"]


@pytest.mark.asyncio
async def test_warp_change_ip(m, api):
    mock(m, "POST", "warp/changeIp", load("warp_change_ip"))

    result = await api.xray.warp_change_ip()

    check(m, "POST", "warp/changeIp")
    assert result["data"]["device_id"] == "fake-device-id"
    assert "warning" in result


@pytest.mark.asyncio
async def test_warp_set_license(m, api):
    mock(m, "POST", "warp/license", load("warp_data"))

    data = await api.xray.warp_set_license("fake-license")

    check(m, "POST", "warp/license")
    assert form(m) == {"license": ["fake-license"]}
    assert data["license_key"] == "fake-license"


@pytest.mark.asyncio
async def test_warp_set_interval(m, api):
    mock(m, "POST", "warp/interval")

    result = await api.xray.warp_set_interval(24)

    check(m, "POST", "warp/interval")
    assert form(m) == {"interval": ["24"]}
    assert result is None


@pytest.mark.asyncio
async def test_warp_set_interval_zero_is_sent(m, api):
    mock(m, "POST", "warp/interval")

    await api.xray.warp_set_interval(0)

    assert form(m) == {"interval": ["0"]}


@pytest.mark.asyncio
async def test_nord_get_countries(m, api):
    mock(m, "POST", "nord/countries", load("nord_countries"))

    countries = await api.xray.nord_get_countries()

    check(m, "POST", "nord/countries")
    assert countries == [{"id": 1, "name": "Albania", "code": "AL"}]


@pytest.mark.asyncio
async def test_nord_get_servers(m, api):
    mock(m, "POST", "nord/servers", load("nord_servers"))

    servers = await api.xray.nord_get_servers(1)

    check(m, "POST", "nord/servers")
    assert form(m) == {"countryId": ["1"]}
    assert servers["servers"][0]["hostname"] == "al1.example.com"
    assert servers["locations"][0]["id"] == 5


@pytest.mark.asyncio
async def test_nord_register(m, api):
    mock(m, "POST", "nord/reg", load("nord_data"))

    data = await api.xray.nord_register("fake-token")

    check(m, "POST", "nord/reg")
    assert form(m) == {"token": ["fake-token"]}
    assert data == {"private_key": "fake-private-key", "token": "fake-token"}


@pytest.mark.asyncio
async def test_nord_set_key(m, api):
    mock(m, "POST", "nord/setKey", load("nord_data"))

    data = await api.xray.nord_set_key("fake-private-key")

    check(m, "POST", "nord/setKey")
    assert form(m) == {"key": ["fake-private-key"]}
    assert data["private_key"] == "fake-private-key"


@pytest.mark.asyncio
async def test_nord_get_data(m, api):
    mock(m, "POST", "nord/data", load("nord_data"))

    data = await api.xray.nord_get_data()

    check(m, "POST", "nord/data")
    assert data["token"] == "fake-token"


@pytest.mark.asyncio
async def test_nord_get_data_empty(m, api):
    mock(m, "POST", "nord/data")

    assert await api.xray.nord_get_data() == {}


@pytest.mark.asyncio
async def test_nord_delete(m, api):
    mock(m, "POST", "nord/del")

    result = await api.xray.nord_delete()

    check(m, "POST", "nord/del")
    assert result is None


@pytest.mark.asyncio
async def test_pia_get_countries(m, api):
    mock(m, "POST", "pia/countries", load("pia_countries"))

    countries = await api.xray.pia_get_countries()

    check(m, "POST", "pia/countries")
    assert countries == [PiaCountry(code="AL"), PiaCountry(code="US")]


@pytest.mark.asyncio
async def test_pia_get_servers(m, api):
    mock(m, "POST", "pia/servers", load("pia_servers"))

    servers = await api.xray.pia_get_servers("US")

    check(m, "POST", "pia/servers")
    assert form(m) == {"countryCode": ["US"]}
    assert isinstance(servers, PiaServers)
    assert servers.regions[0].name == "US East"
    assert servers.servers[0].region_id == "us_east"


@pytest.mark.asyncio
async def test_pia_register(m, api):
    mock(m, "POST", "pia/reg", load("pia_account"))

    account = await api.xray.pia_register("fake-user", "fake-password")

    check(m, "POST", "pia/reg")
    assert form(m) == {"username": ["fake-user"], "password": ["fake-password"]}
    assert account == PiaAccount(username="fake-user", account_hint="fa***")


@pytest.mark.asyncio
async def test_pia_get_data(m, api):
    mock(m, "POST", "pia/data", load("pia_account"))

    account = await api.xray.pia_get_data()

    check(m, "POST", "pia/data")
    assert account == PiaAccount(username="fake-user", account_hint="fa***")


@pytest.mark.asyncio
async def test_pia_get_data_without_account(m, api):
    mock(m, "POST", "pia/data", {"success": True, "msg": "", "obj": None})

    assert await api.xray.pia_get_data() is None


@pytest.mark.asyncio
async def test_pia_delete(m, api):
    mock(m, "POST", "pia/del", {"success": True, "msg": "", "obj": None})

    result = await api.xray.pia_delete()

    check(m, "POST", "pia/del")
    assert result is None


@pytest.mark.asyncio
async def test_pia_add_key(m, api):
    mock(m, "POST", "pia/addKey", load("pia_key"))

    key = await api.xray.pia_add_key("server.example.com")

    check(m, "POST", "pia/addKey")
    assert form(m) == {"hostname": ["server.example.com"]}
    assert isinstance(key, PiaKey)
    assert key.secret_key == "fake-secret-key"
    assert key.endpoint == "192.0.2.1:1337"
