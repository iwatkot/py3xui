"""Tests for AsyncXrayApi."""

import json
import re
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from py3xui import (
    AsyncApi,
    BalancerStatus,
    GeoCategory,
    GeoCategoryPage,
    GeodataSource,
    GeodataTokenIssue,
    GeoEntry,
    GeoEntryPage,
    GeoFile,
    OutboundTestEgress,
    OutboundTestEndpoint,
    OutboundTestResult,
    OutboundTraffic,
    PiaAccount,
    PiaCountry,
    PiaKey,
    PiaServers,
    RouteTestResult,
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


def body_text(m):
    return m.get_requests()[-1].content.decode()


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


@pytest.mark.asyncio
async def test_test_outbound(m, api):
    mock(m, "POST", "testOutbound", load("test_outbound"))

    result = await api.xray.test_outbound('{"tag":"proxy"}', '[{"tag":"proxy"}]', "tcp")

    check(m, "POST", "testOutbound")
    assert form(m) == {
        "outbound": ['{"tag":"proxy"}'],
        "allOutbounds": ['[{"tag":"proxy"}]'],
        "mode": ["tcp"],
    }
    assert isinstance(result, OutboundTestResult)
    assert result.success is True
    assert result.http_status == 204
    assert result.ttfb_ms == 90
    assert result.endpoints == [
        OutboundTestEndpoint(address="192.0.2.1:443", success=True, delay=12)
    ]
    assert result.egress == OutboundTestEgress(ipv4="192.0.2.2", country="NL", warp="off")


@pytest.mark.asyncio
async def test_test_outbound_only_required_fields(m, api):
    mock(m, "POST", "testOutbound", {"success": True, "msg": "", "obj": {"success": False, "delay": 0}})

    result = await api.xray.test_outbound('{"tag":"proxy"}')

    assert form(m) == {"outbound": ['{"tag":"proxy"}']}
    assert result.success is False
    assert result.endpoints == []
    assert result.egress is None


@pytest.mark.asyncio
async def test_test_outbounds(m, api):
    mock(m, "POST", "testOutbounds", load("test_outbounds"))

    results = await api.xray.test_outbounds('[{"tag":"proxy"}]', mode="real")

    check(m, "POST", "testOutbounds")
    assert form(m) == {"outbounds": ['[{"tag":"proxy"}]'], "mode": ["real"]}
    assert [result.tag for result in results] == ["proxy", "dead"]
    assert results[1].error == "timeout"


@pytest.mark.asyncio
async def test_get_balancer_status(m, api):
    mock(m, "POST", "balancerStatus", load("balancer_status"))

    statuses = await api.xray.get_balancer_status(["b1", "b2"])

    check(m, "POST", "balancerStatus")
    assert form(m) == {"tags": ["b1,b2"]}
    assert statuses == {
        "b1": BalancerStatus(tag="b1", running=True, override="direct", selected=["direct"]),
        "b2": BalancerStatus(tag="b2", running=False, override="", selected=[]),
    }


@pytest.mark.asyncio
async def test_set_balancer_override(m, api):
    mock(m, "POST", "balancerOverride")

    result = await api.xray.set_balancer_override("b1", "direct")

    check(m, "POST", "balancerOverride")
    assert form(m) == {"tag": ["b1"], "target": ["direct"]}
    assert result is None


@pytest.mark.asyncio
async def test_set_balancer_override_clear(m, api):
    mock(m, "POST", "balancerOverride")

    await api.xray.set_balancer_override("b1")

    assert parse_qs(body_text(m), keep_blank_values=True) == {"tag": ["b1"], "target": [""]}


@pytest.mark.asyncio
async def test_test_route(m, api):
    mock(m, "POST", "routeTest", load("route_test"))

    result = await api.xray.test_route(
        domain="example.com",
        ip="192.0.2.1",
        port=443,
        network="tcp",
        inbound_tag="in-443",
        protocol="tls",
        email="user@example.com",
    )

    check(m, "POST", "routeTest")
    assert form(m) == {
        "domain": ["example.com"],
        "ip": ["192.0.2.1"],
        "port": ["443"],
        "network": ["tcp"],
        "inboundTag": ["in-443"],
        "protocol": ["tls"],
        "email": ["user@example.com"],
    }
    assert result == RouteTestResult(matched=True, outbound_tag="direct", group_tags=["b1"])


@pytest.mark.asyncio
async def test_test_route_skips_empty_arguments(m, api):
    mock(m, "POST", "routeTest", {"success": True, "msg": "", "obj": {"matched": False, "outboundTag": ""}})

    result = await api.xray.test_route(ip="192.0.2.1")

    assert form(m) == {"ip": ["192.0.2.1"]}
    assert result == RouteTestResult(matched=False, outbound_tag="", group_tags=[])


@pytest.mark.asyncio
async def test_get_geodata_files(m, api):
    mock(m, "GET", "geodata/files", load("geodata_files"))

    files = await api.xray.get_geodata_files()

    check(m, "GET", "geodata/files")
    assert files[0] == GeoFile(
        name="geosite.dat",
        kind="site",
        size=1467392,
        modified_at=1769558400000,
        categories=1043,
    )
    assert files[1].error == "failed to parse"


@pytest.mark.asyncio
async def test_get_geodata_categories(m, api):
    mock(m, "GET", "geodata/categories", load("geodata_categories"))

    page = await api.xray.get_geodata_categories("geosite.dat", "goo", 10, 20)

    check(m, "GET", "geodata/categories")
    assert query(m) == {
        "file": ["geosite.dat"],
        "q": ["goo"],
        "offset": ["10"],
        "limit": ["20"],
    }
    assert page == GeoCategoryPage(
        total=1043,
        items=[
            GeoCategory(code="google", entries=1284, attributes=["ads", "cn"]),
            GeoCategory(code="plain", entries=1, attributes=[]),
        ],
    )


@pytest.mark.asyncio
async def test_get_geodata_categories_only_file(m, api):
    mock(m, "GET", "geodata/categories", load("geodata_categories"))

    await api.xray.get_geodata_categories("geosite.dat")

    assert query(m) == {"file": ["geosite.dat"]}


@pytest.mark.asyncio
async def test_get_geodata_categories_zero_offset_is_sent(m, api):
    mock(m, "GET", "geodata/categories", load("geodata_categories"))

    await api.xray.get_geodata_categories("geosite.dat", offset=0)

    assert query(m) == {"file": ["geosite.dat"], "offset": ["0"]}


@pytest.mark.asyncio
async def test_get_geodata_entries(m, api):
    mock(m, "GET", "geodata/entries", load("geodata_entries"))

    page = await api.xray.get_geodata_entries("geosite.dat", "google", "mail", 5, 10)

    check(m, "GET", "geodata/entries")
    assert query(m) == {
        "file": ["geosite.dat"],
        "code": ["google"],
        "q": ["mail"],
        "offset": ["5"],
        "limit": ["10"],
    }
    assert page == GeoEntryPage(
        total=1284, items=[GeoEntry(kind="domain", value="google.com")]
    )


@pytest.mark.asyncio
async def test_validate_geodata(m, api):
    mock(m, "POST", "geodata/validate", load("geodata_validate"))

    issues = await api.xray.validate_geodata(["geosite:google", "geosite:blabla"], "ip")

    check(m, "POST", "geodata/validate")
    assert form(m) == {"tokens": ["geosite:google,geosite:blabla"], "kind": ["ip"]}
    assert issues == [
        GeodataTokenIssue(
            token="geosite:blabla",
            reason="categoryMissing",
            file="geosite.dat",
            code="blabla",
        )
    ]
