import json

import pytest
from pytest_httpx import HTTPXMock

from py3xui import AsyncApi, Host, HostGroup
from py3xui.api.api_base import ApiFields

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
TOKEN = "test-api-token"
SESSION = "abc123"
CSRF_TOKEN = "test-csrf-token"
BASE = f"{HOST}/panel/api/hosts"
GROUP_ID = "1234567890123456"
OK_RESPONSE = {ApiFields.SUCCESS: True, ApiFields.MSG: "ok", ApiFields.OBJ: None}


def _load(name: str) -> dict:
    with open(f"{RESPONSES_DIR}/{name}.json", encoding="utf-8") as file:
        return json.load(file)


def _api() -> AsyncApi:
    return AsyncApi(HOST, token=TOKEN)


def _group() -> HostGroup:
    return HostGroup(
        inbound_ids=[1],
        remark="cdn-front",
        hosts=["cdn.example.com"],
        port=8443,
        security="same",
        tags=["CDN"],
    )


def _last_body(httpx_mock: HTTPXMock) -> dict:
    return json.loads(httpx_mock.get_requests()[-1].content)


GROUP_BODY = {
    "inboundIds": [1],
    "remark": "cdn-front",
    "hosts": ["cdn.example.com"],
    "port": 8443,
    "security": "same",
    "tags": ["CDN"],
}


@pytest.mark.asyncio
async def test_get_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/list", json=_load("hosts_groups"))

    groups = await _api().host.get_list()

    assert len(groups) == 2
    assert isinstance(groups[0], HostGroup)
    assert groups[0].group_id == GROUP_ID
    assert groups[0].inbound_ids == [1, 2]
    assert groups[0].hosts == ["cdn.example.com:8443", "cdn2.example.com:443"]
    assert groups[0].sni_shared_random is True
    assert groups[0].exclude_from_sub_types == ["mihomo"]
    assert groups[1].is_disabled is True
    assert groups[1].tags == []
    assert groups[1].snis == []
    assert groups[1].alpn == []
    assert groups[1].pinned_peer_cert_sha256 == []
    assert groups[1].exclude_from_sub_types == []
    assert groups[1].node_guids == []


@pytest.mark.asyncio
async def test_get_raw_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/raw", json=_load("hosts_rows"))

    hosts = await _api().host.get_raw_list()

    assert len(hosts) == 1
    assert isinstance(hosts[0], Host)
    assert hosts[0].id == 1
    assert hosts[0].inbound_id == 1
    assert hosts[0].group_id == GROUP_ID
    assert hosts[0].address == "cdn.example.com"
    assert hosts[0].vless_route == "443"
    assert hosts[0].created_at == 1700000000000
    assert hosts[0].updated_at == 1700000001000
    assert hosts[0].tags == []
    assert hosts[0].snis == []
    assert hosts[0].node_guids == []


@pytest.mark.asyncio
async def test_get_by_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/get/{GROUP_ID}", json=_load("hosts_group")
    )

    group = await _api().host.get_by_id(GROUP_ID)

    assert isinstance(group, HostGroup)
    assert group.group_id == GROUP_ID
    assert group.remark == "cdn-front"
    assert group.port == 8443


@pytest.mark.asyncio
async def test_get_by_id_quotes_group_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/get/a%2Fb", json=_load("hosts_group"))

    await _api().host.get_by_id("a/b")

    assert str(httpx_mock.get_requests()[-1].url) == f"{BASE}/get/a%2Fb"


@pytest.mark.asyncio
async def test_get_by_inbound(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/byInbound/1", json=_load("hosts_groups")
    )

    groups = await _api().host.get_by_inbound(1)

    assert [group.group_id for group in groups] == [GROUP_ID, "6543210987654321"]


@pytest.mark.asyncio
async def test_get_by_inbound_without_hosts(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/byInbound/1", json=OK_RESPONSE)

    assert await _api().host.get_by_inbound(1) == []


@pytest.mark.asyncio
async def test_get_tags(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/tags", json=_load("hosts_tags"))

    assert await _api().host.get_tags() == ["CDN", "EU", "FAST"]


@pytest.mark.asyncio
async def test_add(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/add", json=_load("hosts_rows"))

    hosts = await _api().host.add(_group())

    assert _last_body(httpx_mock) == GROUP_BODY
    assert hosts[0].id == 1
    assert isinstance(hosts[0], Host)


@pytest.mark.asyncio
async def test_update(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/update/{GROUP_ID}", json=_load("hosts_rows")
    )

    hosts = await _api().host.update(GROUP_ID, _group())

    assert _last_body(httpx_mock) == GROUP_BODY
    assert hosts[0].address == "cdn.example.com"


@pytest.mark.asyncio
async def test_update_keeps_unknown_fields_of_fetched_group(httpx_mock: HTTPXMock):
    fetched = _load("hosts_group")
    fetched[ApiFields.OBJ]["futureField"] = "kept"
    httpx_mock.add_response(method="GET", url=f"{BASE}/get/{GROUP_ID}", json=fetched)
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/update/{GROUP_ID}", json=_load("hosts_rows")
    )

    api = _api()
    group = await api.host.get_by_id(GROUP_ID)
    await api.host.update(GROUP_ID, group)

    assert _last_body(httpx_mock) == {
        "groupId": GROUP_ID,
        "inboundIds": [1],
        "hosts": ["cdn.example.com:8443"],
        "remark": "cdn-front",
        "tags": ["CDN"],
        "port": 8443,
        "security": "same",
        "randomCount": 1,
        "futureField": "kept",
    }


@pytest.mark.asyncio
async def test_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/del/{GROUP_ID}", json=OK_RESPONSE)

    assert await _api().host.delete(GROUP_ID) is None
    assert _last_body(httpx_mock) == {}


@pytest.mark.asyncio
async def test_set_enable(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/setEnable/{GROUP_ID}", json=OK_RESPONSE
    )

    assert await _api().host.set_enable(GROUP_ID, False) is None
    assert _last_body(httpx_mock) == {"enable": False}


@pytest.mark.asyncio
async def test_reorder(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/reorder", json=OK_RESPONSE)

    assert await _api().host.reorder(["a", "b"]) is None
    assert _last_body(httpx_mock) == {"ids": ["a", "b"]}


@pytest.mark.asyncio
async def test_bulk_add(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/bulk/add", json=_load("hosts_rows"))

    hosts = await _api().host.bulk_add(_group())

    assert _last_body(httpx_mock) == GROUP_BODY
    assert hosts[0].id == 1


@pytest.mark.asyncio
async def test_bulk_set_enable(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/bulk/setEnable", json=OK_RESPONSE)

    assert await _api().host.bulk_set_enable(["a", "b"], False) is None
    assert _last_body(httpx_mock) == {"ids": ["a", "b"], "enable": False}


@pytest.mark.asyncio
async def test_bulk_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/bulk/del", json=OK_RESPONSE)

    assert await _api().host.bulk_delete(["a", "b"]) is None
    assert _last_body(httpx_mock) == {"ids": ["a", "b"]}


def test_facade_propagates_auth():
    api = AsyncApi(HOST, "username", "password")

    api.session = SESSION
    api.csrf_token = CSRF_TOKEN
    api.cookie_name = "3x-ui"

    assert api.host.session == SESSION
    assert api.host.csrf_token == CSRF_TOKEN
    assert api.host.cookie_name == "3x-ui"
