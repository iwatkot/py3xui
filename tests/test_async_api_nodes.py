import json

import pytest
from pytest_httpx import HTTPXMock

from py3xui import (
    AsyncApi,
    Node,
    NodeHistoryPoint,
    NodeProbeResult,
    NodeRemoteInbound,
    NodeUpdateResult,
    NodeWebCertFiles,
)
from py3xui.api.api_base import ApiFields
from py3xui.async_api import AsyncNodeApi

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
TOKEN = "test-api-token"
SESSION = "abc123"
CSRF_TOKEN = "test-csrf-token"
BASE = f"{HOST}/panel/api/nodes"
EMPTY = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}


def fixture(name: str) -> dict:
    with open(f"{RESPONSES_DIR}/nodes_{name}.json", encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture(name="api")
def api_fixture() -> AsyncApi:
    return AsyncApi(HOST, token=TOKEN)


def new_node() -> Node:
    return Node(
        name="de-fra-1",
        address="node1.example.com",
        port=2053,
        enable=True,
        api_token="fake-node-token",
    )


NEW_NODE_BODY = {
    "name": "de-fra-1",
    "address": "node1.example.com",
    "port": 2053,
    "enable": True,
    "apiToken": "fake-node-token",
}


def request_body(httpx_mock: HTTPXMock) -> dict:
    requests = httpx_mock.get_requests()
    return json.loads(requests[-1].content)


def test_facade_propagates_auth():
    api = AsyncApi(HOST, "username", "password")
    assert isinstance(api.node, AsyncNodeApi)
    assert api.node.host == HOST

    api.session = SESSION
    api.csrf_token = CSRF_TOKEN
    api.cookie_name = "custom-cookie"

    assert api.node.session == SESSION
    assert api.node.csrf_token == CSRF_TOKEN
    assert api.node.cookie_name == "custom-cookie"


@pytest.mark.asyncio
async def test_get_list(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/list", json=fixture("list"))

    nodes = await api.node.get_list()

    assert len(nodes) == 1
    assert isinstance(nodes[0], Node)
    assert nodes[0].id == 1
    assert nodes[0].name == "edge-1"
    assert nodes[0].base_path == "/"
    assert nodes[0].has_api_token is True
    assert nodes[0].api_token is None
    assert nodes[0].cpu_pct == 12.5
    assert nodes[0].inbound_tags == ["in-443-tcp"]


@pytest.mark.asyncio
async def test_get_list_empty(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/list", json=EMPTY)

    assert not await api.node.get_list()


@pytest.mark.asyncio
async def test_get_by_id(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/get/1", json=fixture("get"))

    node = await api.node.get_by_id(1)

    assert node.id == 1
    assert node.address == "node.example.com"
    assert node.xray_state == "running"


@pytest.mark.asyncio
async def test_null_inbound_tags_are_parsed_as_empty_list(api: AsyncApi, httpx_mock: HTTPXMock):
    response = fixture("get")
    response[ApiFields.OBJ]["inboundTags"] = None
    httpx_mock.add_response(method="GET", url=f"{BASE}/get/1", json=response)

    node = await api.node.get_by_id(1)

    assert node.inbound_tags == []


@pytest.mark.asyncio
async def test_get_web_cert_files(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/webCert/1", json=fixture("web_cert"))

    files = await api.node.get_web_cert_files(1)

    assert isinstance(files, NodeWebCertFiles)
    assert files.web_cert_file == "/root/cert/example.com/fullchain.pem"
    assert files.web_key_file == "/root/cert/example.com/privkey.pem"


@pytest.mark.asyncio
async def test_add(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/add", json=fixture("get"))

    created = await api.node.add(new_node())

    assert request_body(httpx_mock) == NEW_NODE_BODY
    assert created.id == 1
    assert created.api_token is None


@pytest.mark.asyncio
async def test_update(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/update/1", json=EMPTY)
    node = new_node()
    node.remark = "Primary edge"

    assert await api.node.update(1, node) is None

    assert request_body(httpx_mock) == {**NEW_NODE_BODY, "remark": "Primary edge"}


@pytest.mark.asyncio
async def test_update_read_cycle_keeps_stored_token(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{BASE}/get/1", json=fixture("get"))
    httpx_mock.add_response(method="POST", url=f"{BASE}/update/1", json=EMPTY)

    node = await api.node.get_by_id(1)
    node.remark = "changed"
    await api.node.update(node.id, node)

    body = request_body(httpx_mock)
    assert "apiToken" not in body
    assert "clearApiToken" not in body
    assert body["remark"] == "changed"
    assert body["id"] == 1
    assert body["name"] == "edge-1"
    assert body["address"] == "node.example.com"
    assert body["port"] == 2053
    assert body["enable"] is True
    assert body["basePath"] == "/"
    assert body["inboundTags"] == ["in-443-tcp"]


@pytest.mark.asyncio
async def test_update_read_cycle_keeps_unknown_fields(api: AsyncApi, httpx_mock: HTTPXMock):
    response = fixture("get")
    response[ApiFields.OBJ]["futureField"] = "keep-me"
    httpx_mock.add_response(method="GET", url=f"{BASE}/get/1", json=response)
    httpx_mock.add_response(method="POST", url=f"{BASE}/update/1", json=EMPTY)

    await api.node.update(1, await api.node.get_by_id(1))

    assert request_body(httpx_mock)["futureField"] == "keep-me"


@pytest.mark.asyncio
async def test_update_sends_disabled_state(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/update/1", json=EMPTY)
    node = new_node()
    node.enable = False

    await api.node.update(1, node)

    assert request_body(httpx_mock)["enable"] is False


@pytest.mark.asyncio
async def test_update_clear_api_token(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/update/1", json=EMPTY)
    node = Node(name="n", address="a", port=1, enable=False, clear_api_token=True)

    await api.node.update(1, node)

    body = request_body(httpx_mock)
    assert body["clearApiToken"] is True
    assert "apiToken" not in body


@pytest.mark.asyncio
async def test_update_failure_raises(api: AsyncApi, httpx_mock: HTTPXMock):
    failure = {ApiFields.SUCCESS: False, ApiFields.MSG: "failed", ApiFields.OBJ: None}
    httpx_mock.add_response(method="POST", url=f"{BASE}/update/1", json=failure)

    with pytest.raises(ValueError):
        await api.node.update(1, new_node())


@pytest.mark.asyncio
async def test_delete(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/del/1", json=EMPTY)

    assert await api.node.delete(1) is None

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("enable", [True, False])
async def test_set_enable(api: AsyncApi, httpx_mock: HTTPXMock, enable: bool):
    httpx_mock.add_response(method="POST", url=f"{BASE}/setEnable/1", json=EMPTY)

    assert await api.node.set_enable(1, enable) is None

    assert request_body(httpx_mock) == {"enable": enable}


@pytest.mark.asyncio
async def test_test(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/test", json=fixture("probe"))

    result = await api.node.test(new_node())

    assert request_body(httpx_mock) == NEW_NODE_BODY
    assert isinstance(result, NodeProbeResult)
    assert result.status == "online"
    assert result.latency_ms == 42
    assert result.xray_version == "25.10.31"


@pytest.mark.asyncio
async def test_test_offline_node_does_not_raise(api: AsyncApi, httpx_mock: HTTPXMock):
    response = {
        ApiFields.SUCCESS: True,
        ApiFields.OBJ: {"status": "offline", "error": "connection refused"},
    }
    httpx_mock.add_response(method="POST", url=f"{BASE}/test", json=response)

    result = await api.node.test(new_node())

    assert result.status == "offline"
    assert result.error == "connection refused"


@pytest.mark.asyncio
async def test_get_cert_fingerprint(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/certFingerprint", json=fixture("cert_fingerprint")
    )

    fingerprint = await api.node.get_cert_fingerprint(new_node())

    assert request_body(httpx_mock) == NEW_NODE_BODY
    assert fingerprint == "k3b1...base64-sha256...="


@pytest.mark.asyncio
async def test_get_remote_inbounds(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/inbounds", json=fixture("inbounds"))

    inbounds = await api.node.get_remote_inbounds(new_node())

    assert request_body(httpx_mock) == NEW_NODE_BODY
    assert len(inbounds) == 1
    assert isinstance(inbounds[0], NodeRemoteInbound)
    assert inbounds[0].id == 7
    assert inbounds[0].tag == "inbound-443"
    assert inbounds[0].protocol == "vless"
    assert inbounds[0].port == 443


@pytest.mark.asyncio
async def test_probe(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/probe/1", json=fixture("probe"))

    result = await api.node.probe(1)

    assert isinstance(result, NodeProbeResult)
    assert result.status == "online"
    assert result.cpu_pct == 12.5


@pytest.mark.asyncio
async def test_update_panel(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/updatePanel", json=fixture("update_panel")
    )

    results = await api.node.update_panel([1, 2])

    assert request_body(httpx_mock) == {"ids": [1, 2], "dev": False}
    assert all(isinstance(result, NodeUpdateResult) for result in results)
    assert [result.ok for result in results] == [True, False]
    assert results[1].error == "node is offline"


@pytest.mark.asyncio
async def test_update_panel_dev_channel(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/updatePanel", json=fixture("update_panel")
    )

    await api.node.update_panel([1], dev=True)

    assert request_body(httpx_mock) == {"ids": [1], "dev": True}


@pytest.mark.asyncio
async def test_get_history(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/history/1/netUp/60", json=fixture("history")
    )

    points = await api.node.get_history(1, "netUp", 60)

    assert points == [
        NodeHistoryPoint(t=1700000000, v=12.5),
        NodeHistoryPoint(t=1700000060, v=13.25),
    ]


@pytest.mark.asyncio
async def test_get_mtls_ca(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/mtls/ca", json=fixture("mtls_ca"))

    ca_cert = await api.node.get_mtls_ca()

    assert ca_cert == "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n"


@pytest.mark.asyncio
@pytest.mark.parametrize("ca_cert", ["-----BEGIN CERTIFICATE-----\nfake\n", ""])
async def test_set_mtls_trust_ca(api: AsyncApi, httpx_mock: HTTPXMock, ca_cert: str):
    httpx_mock.add_response(method="POST", url=f"{BASE}/mtls/trustCA", json=EMPTY)

    assert await api.node.set_mtls_trust_ca(ca_cert) is None

    assert request_body(httpx_mock) == {"caCert": ca_cert}


@pytest.mark.asyncio
async def test_reload_mtls_client(api: AsyncApi, httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{BASE}/mtls/reloadClient", json=EMPTY)

    assert await api.node.reload_mtls_client() is None

    assert len(httpx_mock.get_requests()) == 1
