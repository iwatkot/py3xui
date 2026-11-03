import json

import pytest
import requests_mock

from py3xui import (
    Api,
    Node,
    NodeHistoryPoint,
    NodeProbeResult,
    NodeRemoteInbound,
    NodeUpdateResult,
    NodeWebCertFiles,
)
from py3xui.api import NodeApi
from py3xui.api.api_base import ApiFields

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
def api_fixture() -> Api:
    return Api(HOST, token=TOKEN)


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


def test_facade_propagates_auth():
    api = Api(HOST, "username", "password")
    assert isinstance(api.node, NodeApi)
    assert api.node.host == HOST

    api.session = SESSION
    api.csrf_token = CSRF_TOKEN
    api.cookie_name = "custom-cookie"

    assert api.node.session == SESSION
    assert api.node.csrf_token == CSRF_TOKEN
    assert api.node.cookie_name == "custom-cookie"


def test_get_list(api: Api):
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/list", json=fixture("list"))
        nodes = api.node.get_list()

    assert m.call_count == 1
    assert len(nodes) == 1
    assert isinstance(nodes[0], Node)
    assert nodes[0].id == 1
    assert nodes[0].name == "edge-1"
    assert nodes[0].base_path == "/"
    assert nodes[0].has_api_token is True
    assert nodes[0].api_token is None
    assert nodes[0].cpu_pct == 12.5
    assert nodes[0].inbound_tags == ["in-443-tcp"]


def test_get_list_empty(api: Api):
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/list", json=EMPTY)
        assert not api.node.get_list()


def test_get_by_id(api: Api):
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/get/1", json=fixture("get"))
        node = api.node.get_by_id(1)

    assert node.id == 1
    assert node.address == "node.example.com"
    assert node.xray_state == "running"


def test_null_inbound_tags_are_parsed_as_empty_list(api: Api):
    response = fixture("get")
    response[ApiFields.OBJ]["inboundTags"] = None
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/get/1", json=response)
        node = api.node.get_by_id(1)

    assert node.inbound_tags == []


def test_get_web_cert_files(api: Api):
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/webCert/1", json=fixture("web_cert"))
        files = api.node.get_web_cert_files(1)

    assert isinstance(files, NodeWebCertFiles)
    assert files.web_cert_file == "/root/cert/example.com/fullchain.pem"
    assert files.web_key_file == "/root/cert/example.com/privkey.pem"


def test_add(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/add", json=fixture("get"))
        created = api.node.add(new_node())

    assert m.last_request.json() == NEW_NODE_BODY
    assert created.id == 1
    assert created.api_token is None


def test_update(api: Api):
    node = new_node()
    node.remark = "Primary edge"
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/update/1", json=EMPTY)
        assert api.node.update(1, node) is None

    assert m.last_request.json() == {**NEW_NODE_BODY, "remark": "Primary edge"}


def test_update_read_cycle_keeps_stored_token(api: Api):
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/get/1", json=fixture("get"))
        m.post(f"{BASE}/update/1", json=EMPTY)
        node = api.node.get_by_id(1)
        node.remark = "changed"
        api.node.update(node.id, node)

    body = m.last_request.json()
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


def test_update_read_cycle_keeps_unknown_fields(api: Api):
    response = fixture("get")
    response[ApiFields.OBJ]["futureField"] = "keep-me"
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/get/1", json=response)
        m.post(f"{BASE}/update/1", json=EMPTY)
        api.node.update(1, api.node.get_by_id(1))

    assert m.last_request.json()["futureField"] == "keep-me"


def test_update_sends_disabled_state(api: Api):
    node = new_node()
    node.enable = False
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/update/1", json=EMPTY)
        api.node.update(1, node)

    assert m.last_request.json()["enable"] is False


def test_update_clear_api_token(api: Api):
    node = Node(name="n", address="a", port=1, enable=False, clear_api_token=True)
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/update/1", json=EMPTY)
        api.node.update(1, node)

    body = m.last_request.json()
    assert body["clearApiToken"] is True
    assert "apiToken" not in body


def test_api_token_is_hidden_from_repr():
    assert "fake-node-token" not in repr(new_node())


def test_update_failure_raises(api: Api):
    failure = {ApiFields.SUCCESS: False, ApiFields.MSG: "failed", ApiFields.OBJ: None}
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/update/1", json=failure)
        with pytest.raises(ValueError):
            api.node.update(1, new_node())


def test_delete(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/del/1", json=EMPTY)
        assert api.node.delete(1) is None

    assert m.call_count == 1
    assert m.last_request.method == "POST"


@pytest.mark.parametrize("enable", [True, False])
def test_set_enable(api: Api, enable: bool):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/setEnable/1", json=EMPTY)
        assert api.node.set_enable(1, enable) is None

    assert m.last_request.json() == {"enable": enable}


def test_test(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/test", json=fixture("probe"))
        result = api.node.test(new_node())

    assert m.last_request.json() == NEW_NODE_BODY
    assert isinstance(result, NodeProbeResult)
    assert result.status == "online"
    assert result.latency_ms == 42
    assert result.xray_version == "25.10.31"


def test_test_offline_node_does_not_raise(api: Api):
    response = {
        ApiFields.SUCCESS: True,
        ApiFields.OBJ: {"status": "offline", "error": "connection refused"},
    }
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/test", json=response)
        result = api.node.test(new_node())

    assert result.status == "offline"
    assert result.error == "connection refused"


def test_get_cert_fingerprint(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/certFingerprint", json=fixture("cert_fingerprint"))
        fingerprint = api.node.get_cert_fingerprint(new_node())

    assert m.last_request.json() == NEW_NODE_BODY
    assert fingerprint == "k3b1...base64-sha256...="


def test_get_remote_inbounds(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/inbounds", json=fixture("inbounds"))
        inbounds = api.node.get_remote_inbounds(new_node())

    assert m.last_request.json() == NEW_NODE_BODY
    assert len(inbounds) == 1
    assert isinstance(inbounds[0], NodeRemoteInbound)
    assert inbounds[0].id == 7
    assert inbounds[0].tag == "inbound-443"
    assert inbounds[0].protocol == "vless"
    assert inbounds[0].port == 443


def test_probe(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/probe/1", json=fixture("probe"))
        result = api.node.probe(1)

    assert isinstance(result, NodeProbeResult)
    assert result.status == "online"
    assert result.cpu_pct == 12.5


def test_update_panel(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/updatePanel", json=fixture("update_panel"))
        results = api.node.update_panel([1, 2])

    assert m.last_request.json() == {"ids": [1, 2], "dev": False}
    assert all(isinstance(result, NodeUpdateResult) for result in results)
    assert [result.ok for result in results] == [True, False]
    assert results[1].error == "node is offline"


def test_update_panel_dev_channel(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/updatePanel", json=fixture("update_panel"))
        api.node.update_panel([1], dev=True)

    assert m.last_request.json() == {"ids": [1], "dev": True}


def test_get_history(api: Api):
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/history/1/netUp/60", json=fixture("history"))
        points = api.node.get_history(1, "netUp", 60)

    assert m.last_request.url == f"{BASE}/history/1/netUp/60"
    assert points == [
        NodeHistoryPoint(t=1700000000, v=12.5),
        NodeHistoryPoint(t=1700000060, v=13.25),
    ]


def test_get_mtls_ca(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/mtls/ca", json=fixture("mtls_ca"))
        ca_cert = api.node.get_mtls_ca()

    assert ca_cert == "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n"


@pytest.mark.parametrize("ca_cert", ["-----BEGIN CERTIFICATE-----\nfake\n", ""])
def test_set_mtls_trust_ca(api: Api, ca_cert: str):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/mtls/trustCA", json=EMPTY)
        assert api.node.set_mtls_trust_ca(ca_cert) is None

    assert m.last_request.json() == {"caCert": ca_cert}


def test_reload_mtls_client(api: Api):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE}/mtls/reloadClient", json=EMPTY)
        assert api.node.reload_mtls_client() is None

    assert m.call_count == 1
