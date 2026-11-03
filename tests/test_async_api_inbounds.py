import json
import os
from urllib.parse import parse_qs

import httpx
import pytest
from pytest_httpx import HTTPXMock

from py3xui import (
    AmneziaWGReadiness,
    AsyncApi,
    Client,
    Inbound,
    InboundBulkDeleteResult,
    InboundClientsDeleteResult,
    InboundFallback,
    InboundOption,
)
from py3xui.api.api_base import ApiFields
from py3xui.inbound import Settings, Sniffing

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
BASE = f"{HOST}/panel/api/inbounds"
RESPONSE_OK = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}


def _load(name: str) -> dict:
    with open(os.path.join(RESPONSES_DIR, f"inbounds_{name}.json"), encoding="utf-8") as file:
        return json.load(file)


def _api() -> AsyncApi:
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def _request(httpx_mock: HTTPXMock) -> httpx.Request:
    request = httpx_mock.get_request()
    assert request is not None, "Mocked request was not called"
    return request


def _json_body(httpx_mock: HTTPXMock) -> dict:
    return json.loads(_request(httpx_mock).content)


@pytest.mark.asyncio
async def test_get_list_slim(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/list/slim", json=_load("list_slim"))

    inbounds = await _api().inbound.get_list_slim()

    assert _request(httpx_mock).method == "GET"
    assert len(inbounds) == 1
    inbound = inbounds[0]
    assert isinstance(inbound, Inbound)
    assert inbound.id == 1
    assert isinstance(inbound.settings, Settings)
    assert [client.email for client in inbound.settings.clients] == ["alice", "bob"]
    assert inbound.settings.clients[0].comment == "vip"
    assert inbound.settings.clients[1].enable is False
    assert inbound.client_stats[0].up == 1048576


@pytest.mark.asyncio
async def test_get_options(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/options", json=_load("options"))

    options = await _api().inbound.get_options()

    assert _request(httpx_mock).method == "GET"
    assert len(options) == 1
    option = options[0]
    assert isinstance(option, InboundOption)
    assert option.id == 1
    assert option.tag == "in-443-tcp"
    assert option.tls_flow_capable is True
    assert option.node_id is None
    assert option.awg_server is None


@pytest.mark.asyncio
async def test_get_amneziawg_kernel_readiness(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/amneziawgKernelReadiness",
        json=_load("amneziawg_kernel_readiness"),
    )

    readiness = await _api().inbound.get_amneziawg_kernel_readiness()

    assert _request(httpx_mock).method == "GET"
    assert isinstance(readiness, AmneziaWGReadiness)
    assert readiness.ready is False
    assert readiness.blockers[0].code == "tools"
    assert readiness.blockers[0].detail == "awg"
    assert readiness.install_command == "sudo /usr/local/x-ui/x-ui install-awg-kernel"


@pytest.mark.asyncio
async def test_get_all_links(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/allLinks", json=_load("all_links"))

    links = await _api().inbound.get_all_links()

    assert _request(httpx_mock).method == "GET"
    assert len(links) == 2
    assert links[0].startswith("vless://")


@pytest.mark.asyncio
async def test_get_all_links_null_obj_returns_empty_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/allLinks", json=RESPONSE_OK)

    assert await _api().inbound.get_all_links() == []


@pytest.mark.asyncio
async def test_bulk_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/bulkDel", json=_load("bulk_delete"))

    result = await _api().inbound.bulk_delete([1, 2, 3])

    assert _request(httpx_mock).method == "POST"
    assert _json_body(httpx_mock) == {"ids": [1, 2, 3]}
    assert isinstance(result, InboundBulkDeleteResult)
    assert result.deleted == 2
    assert result.skipped[0].id == 3
    assert result.skipped[0].reason == "..."


@pytest.mark.asyncio
@pytest.mark.parametrize("enable", [True, False])
async def test_set_enable(httpx_mock: HTTPXMock, enable: bool):
    httpx_mock.add_response(method="POST", url=f"{BASE}/setEnable/1", json=RESPONSE_OK)

    assert await _api().inbound.set_enable(1, enable) is None

    assert _request(httpx_mock).method == "POST"
    assert _json_body(httpx_mock) == {"enable": enable}


@pytest.mark.asyncio
async def test_set_sub_sort_index(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/1/subSortIndex", json=RESPONSE_OK)

    assert await _api().inbound.set_sub_sort_index(1, -2) is None

    assert _request(httpx_mock).method == "POST"
    assert _json_body(httpx_mock) == {"subSortIndex": -2}


@pytest.mark.asyncio
async def test_reset_stats_by_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/1/resetTraffic", json=RESPONSE_OK)

    assert await _api().inbound.reset_stats_by_id(1) is None

    assert _request(httpx_mock).method == "POST"


@pytest.mark.asyncio
async def test_delete_all_clients(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/1/delAllClients", json=_load("delete_all_clients")
    )

    result = await _api().inbound.delete_all_clients(1)

    assert _request(httpx_mock).method == "POST"
    assert isinstance(result, InboundClientsDeleteResult)
    assert result.deleted == 12
    assert result.skipped[0].email == "bob"
    assert result.skipped[0].reason == "client not found"


@pytest.mark.asyncio
async def test_import_inbound(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/import", json=_load("import"))
    inbound = Inbound(
        enable=True,
        port=443,
        protocol="vless",
        settings=Settings(),
        sniffing=Sniffing(enabled=True),
        remark="imported",
        up=5,
        down=7,
        total=9,
    )

    created = await _api().inbound.import_inbound(inbound)

    request = _request(httpx_mock)
    assert request.method == "POST"
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    form = parse_qs(request.content.decode("utf-8"))
    assert list(form) == ["data"]
    payload = json.loads(form["data"][0])
    assert payload["remark"] == "imported"
    assert payload["port"] == 443
    assert payload["protocol"] == "vless"
    assert (payload["up"], payload["down"], payload["total"]) == (5, 7, 9)
    assert isinstance(payload["settings"], str)
    assert isinstance(payload["sniffing"], str)
    assert isinstance(created, Inbound)
    assert created.id == 7
    assert created.settings.clients[0].email == "alice"


@pytest.mark.asyncio
async def test_import_inbound_raw_json(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/import", json=_load("import"))
    raw = json.dumps({"protocol": "wireguard", "port": 51820, "settings": {"peers": []}})

    created = await _api().inbound.import_inbound(raw)

    assert parse_qs(_request(httpx_mock).content.decode("utf-8")) == {"data": [raw]}
    assert created.id == 7


@pytest.mark.asyncio
async def test_push_client_traffics(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/pushClientTraffics", json=RESPONSE_OK)
    client = Client(id="some-uuid", email="alice", enable=True, up=1024, down=2048)

    assert await _api().inbound.push_client_traffics("master-guid", [client]) is None

    assert _request(httpx_mock).method == "POST"
    assert _json_body(httpx_mock) == {
        "masterGuid": "master-guid",
        "traffics": [{"email": "alice", "up": 1024, "down": 2048}],
    }


@pytest.mark.asyncio
async def test_get_fallbacks(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/10/fallbacks", json=_load("get_fallbacks"))

    fallbacks = await _api().inbound.get_fallbacks(10)

    assert _request(httpx_mock).method == "GET"
    assert len(fallbacks) == 1
    fallback = fallbacks[0]
    assert isinstance(fallback, InboundFallback)
    assert fallback.id == 1
    assert fallback.master_id == 10
    assert fallback.child_id == 11
    assert fallback.path == "/vlws"
    assert fallback.xver == 2
    assert fallback.sort_order == 0


@pytest.mark.asyncio
async def test_set_fallbacks(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/10/fallbacks", json=RESPONSE_OK)
    fallbacks = [
        InboundFallback(id=1, master_id=10, child_id=11, path="/vlws", xver=2),
        InboundFallback(child_id=12, alpn="h2", dest="8443", sort_order=3),
    ]

    assert await _api().inbound.set_fallbacks(10, fallbacks) is None

    assert _request(httpx_mock).method == "POST"
    assert _json_body(httpx_mock) == {
        "fallbacks": [
            {"childId": 11, "path": "/vlws", "xver": 2},
            {"childId": 12, "alpn": "h2", "dest": "8443", "sortOrder": 3},
        ]
    }
