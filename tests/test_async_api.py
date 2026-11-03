import json
import logging
import os
import uuid

import pytest
from pytest_httpx import HTTPXMock

from py3xui import AsyncApi, Client, ClientDetails, Inbound
from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_server import XrayVersionUnavailableError
from py3xui.inbound import Settings, Sniffing, StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
CSRF_TOKEN = "test-csrf-token"
CSRF_RESPONSE = {ApiFields.SUCCESS: True, ApiFields.OBJ: CSRF_TOKEN}
EMAIL = "alhtim2x"
RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"

DETAILS_EMAIL = "alice+wg@example.com"
DETAILS_EMAIL_QUOTED = "alice%2Bwg%40example.com"


def _expected_round_trip_payload(record: dict) -> dict:
    """Returns what update() must send back for the record from get_client_details.json after
    total_gb is changed: every stored field, in the shape the update endpoint accepts."""
    expected = {
        key: value
        for key, value in record.items()
        if key not in {"id", "allowedIPs", "createdAt", "updatedAt"} and value not in ("", 0)
    }
    expected.update(
        {
            "id": record["uuid"],
            "allowedIPs": ["10.66.0.2/32", "fd00:66::2/128"],
            "created_at": record["createdAt"],
            "updated_at": record["updatedAt"],
            "totalGB": 50 * 1024**3,
        }
    )
    return expected


@pytest.mark.asyncio
async def test_from_env():
    os.environ["XUI_HOST"] = HOST
    os.environ["XUI_USERNAME"] = USERNAME
    os.environ["XUI_PASSWORD"] = PASSWORD

    api = AsyncApi.from_env()
    assert api.inbound.host == HOST, f"Expected {HOST}, got {api.inbound.host}"
    assert api.inbound.username == USERNAME, (
        f"Expected {USERNAME}, got {api.inbound.username}"
    )
    assert api.inbound.password == PASSWORD, (
        f"Expected {PASSWORD}, got {api.inbound.password}"
    )


@pytest.mark.asyncio
async def test_login_failed(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/csrf-token",
        json=CSRF_RESPONSE,
        status_code=200,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/login",
        json={ApiFields.SUCCESS: False},
        status_code=200,
    )

    api = AsyncApi(HOST, "username", "password")
    with pytest.raises(ValueError):
        await api.login()


@pytest.mark.asyncio
async def test_login_success(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/csrf-token",
        json=CSRF_RESPONSE,
        status_code=200,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/login",
        json={ApiFields.SUCCESS: True},
        status_code=200,
        headers={"Set-Cookie": f"3x-ui={SESSION}; Path=/"},
    )

    api = AsyncApi(HOST, "username", "password")
    await api.login()
    assert api.session == SESSION, f"Expected {SESSION}, got {api.session}"


@pytest.mark.asyncio
async def test_login_sends_csrf_header(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/csrf-token",
        json=CSRF_RESPONSE,
        status_code=200,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/login",
        json={ApiFields.SUCCESS: True},
        status_code=200,
        headers={"Set-Cookie": f"3x-ui={SESSION}; Path=/"},
    )

    api = AsyncApi(HOST, "username", "password")
    await api.login()

    login_request = httpx_mock.get_requests()[1]
    assert login_request.headers["X-CSRF-Token"] == CSRF_TOKEN


@pytest.mark.asyncio
async def test_get_client(httpx_mock: HTTPXMock):
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client.json")))

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/{EMAIL}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    client = await api.client.get_by_email(EMAIL)

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert isinstance(client, Client), f"Expected Client, got {type(client)}"
    assert client.email == EMAIL, f"Expected {EMAIL}, got {client.email}"
    assert client.id == 1, f"Expected 1, got {client.id}"


@pytest.mark.asyncio
async def test_get_client_nested_payload_shape(httpx_mock: HTTPXMock):
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: {
            "client": {
                "id": str(uuid.uuid4()),
                "email": EMAIL,
                "enable": True,
                "tgId": "1",
                "subId": "sub",
            },
            "inboundIds": [9],
        },
    }

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/{EMAIL}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    client = await api.client.get_by_email(EMAIL)

    assert isinstance(client, Client)
    assert client.inbound_id == 9


@pytest.mark.asyncio
async def test_get_ips(httpx_mock: HTTPXMock):
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: ApiFields.NO_IP_RECORD,
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/ips/{EMAIL}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    ips = await api.client.get_ips(EMAIL)

    assert ips == [], f"Expected [], got {ips}"


@pytest.mark.asyncio
async def test_get_ips_with_records(httpx_mock: HTTPXMock):
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: ["1.1.1.1"],
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/ips/{EMAIL}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    ips = await api.client.get_ips(EMAIL)

    assert ips == ["1.1.1.1"]


@pytest.mark.asyncio
async def test_add_clients(httpx_mock: HTTPXMock):
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/add",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.add(1, [client])

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_update_client(httpx_mock: HTTPXMock):
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/update/{client.email}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.update(client.id, client)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_update_client_normalizes_id_from_uuid(httpx_mock: HTTPXMock):
    client = Client(id=1, uuid=str(uuid.uuid4()), email="test", enable=True)
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/update/{client.email}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.update("legacy-id", client)

    request = httpx_mock.get_request()
    assert request is not None
    assert json.loads(request.content.decode("utf-8"))["id"] == client.uuid


@pytest.mark.asyncio
async def test_get_client_details(httpx_mock: HTTPXMock):
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client_details.json")))

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/{DETAILS_EMAIL_QUOTED}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    details = await api.client.get_details(DETAILS_EMAIL)

    assert isinstance(details, ClientDetails)
    assert details.inbound_ids == [3, 5]
    assert details.tunnel_allowed_ips == {3: "10.66.0.2/32", 5: "10.77.0.2/32"}
    assert details.used_traffic == 1073741824
    assert details.external_links[0]["value"] == "vless://example"

    client = details.client
    assert client.email == DETAILS_EMAIL
    assert client.uuid == "6f0f4c4e-7d4c-4b9e-9a51-2c1f4e8d7a10"
    assert client.group == "staff"
    assert client.allowed_ips == ["10.66.0.2/32", "fd00:66::2/128"]
    assert client.keep_alive == 25
    assert client.reverse == {"tag": "reverse-out"}
    assert client.limit_hwid == 3
    assert client.created_at == 1735689600000
    assert client.futureField == {"nested": [1, 2, 3]}  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_get_client_details_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/{EMAIL}",
        json={ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None},
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    assert await api.client.get_details(EMAIL) is None


@pytest.mark.asyncio
async def test_get_client_details_update_round_trip_keeps_all_fields(httpx_mock: HTTPXMock):
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client_details.json")))
    record = response_example[ApiFields.OBJ]["client"]

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/{DETAILS_EMAIL_QUOTED}",
        json=response_example,
        status_code=200,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/update/{DETAILS_EMAIL_QUOTED}",
        json={ApiFields.SUCCESS: True, ApiFields.MSG: "Client updated"},
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    details = await api.client.get_details(DETAILS_EMAIL)
    assert details is not None
    details.client.total_gb = 50 * 1024**3
    await api.client.update(details.client.uuid, details.client)

    request = httpx_mock.get_requests(method="POST")[-1]
    assert json.loads(request.content.decode("utf-8")) == _expected_round_trip_payload(record)


@pytest.mark.asyncio
async def test_get_client_details_missing_client_returns_none(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/{EMAIL}",
        json={ApiFields.SUCCESS: False, ApiFields.MSG: "Obtain (record not found)"},
    )
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    assert await api.client.get_details(EMAIL) is None


@pytest.mark.asyncio
async def test_get_client_details_other_panel_errors_are_raised(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/{EMAIL}",
        json={ApiFields.SUCCESS: False, ApiFields.MSG: "Obtain (database is locked)"},
    )
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    with pytest.raises(ValueError, match="database is locked"):
        await api.client.get_details(EMAIL)


@pytest.mark.asyncio
async def test_update_client_does_not_log_secrets(httpx_mock: HTTPXMock, caplog):
    client = Client(email="test", enable=True, private_key="private-key-value")
    logger = logging.getLogger("py3xui-test")
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/clients/update/test", json={ApiFields.SUCCESS: True}
    )
    api = AsyncApi(HOST, USERNAME, PASSWORD, logger=logger)
    api.session = SESSION

    with caplog.at_level(logging.INFO, logger="py3xui-test"):
        await api.client.update("id", client)

    assert "private-key-value" not in caplog.text


@pytest.mark.asyncio
async def test_reset_client_ips(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/clearIps/{EMAIL}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.reset_ips(EMAIL)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_reset_client_stats(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/resetTraffic/{EMAIL}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.reset_stats(1, EMAIL)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_client(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}
    response_clients = json.load(open(os.path.join(RESPONSES_DIR, "get_client_traffic_by_id.json")))
    response_clients[ApiFields.OBJ][0]["uuid"] = "d76eb6ed-0697-4cd5-a8c5-8cfeb4d1b209"
    client_uuid = response_clients[ApiFields.OBJ][0]["uuid"]

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/list",
        json=response_clients,
        status_code=200,
    )

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/del/test",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.delete(1, client_uuid)

    assert len(httpx_mock.get_requests()) == 2


@pytest.mark.asyncio
async def test_delete_client_by_email_skips_lookup(httpx_mock: HTTPXMock):
    email = "user@example.com"
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/del/{email}",
        json={ApiFields.SUCCESS: True},
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.delete(1, email)

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_delete_client_unresolvable_identifier_raises(httpx_mock: HTTPXMock):
    response_clients = {
        ApiFields.SUCCESS: True,
        ApiFields.OBJ: [{"id": 2, "uuid": "u2", "email": "e2"}],
    }

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/list",
        json=response_clients,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    with pytest.raises(ValueError):
        await api.client.delete(1, "unknown-id")


@pytest.mark.asyncio
async def test_delete_depleted_clients(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/delDepleted",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.delete_depleted(1)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_client_online(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/onlines",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.online()

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_client_online_empty_obj_returns_empty_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/onlines",
        json={ApiFields.SUCCESS: True, ApiFields.OBJ: None},
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    assert await api.client.online() == []


@pytest.mark.asyncio
async def test_get_client_traffic_by_id(httpx_mock: HTTPXMock):
    response_example = json.load(
        open(os.path.join(RESPONSES_DIR, "get_client_traffic_by_id.json"))
    )
    response_example[ApiFields.OBJ][0]["uuid"] = "239708ef-487e-4945-829d-ad79a0ce067e"

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/list",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    clients = await api.client.get_traffic_by_id("239708ef-487e-4945-829d-ad79a0ce067e")

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert len(clients) == 1, f"Expected 1, got {len(clients)}"

    client = clients[0]

    assert isinstance(client, Client), f"Expected Client, got {type(client)}"
    assert client.email == "test", f"Expected test, got {client.email}"
    assert client.id == 1, f"Expected 1, got {client.id}"


def _prepare_inbound() -> Inbound:
    settings = Settings()
    sniffing = Sniffing(enabled=True)

    tcp_settings = {
        "acceptProxyProtocol": False,
        "header": {"type": "none"},
    }
    stream_settings = StreamSettings(
        security="reality", network="tcp", tcp_settings=tcp_settings
    )

    inbound = Inbound(
        enable=True,
        port=999,
        protocol="vless",
        settings=settings,
        stream_settings=stream_settings,
        sniffing=sniffing,
    )

    return inbound


@pytest.mark.asyncio
async def test_get_inbounds(httpx_mock: HTTPXMock):
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/inbounds/list",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    inbounds = await api.inbound.get_list()

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert len(inbounds) == 1, f"Expected 1, got {len(inbounds)}"
    inbound = inbounds[0]
    assert isinstance(inbound, Inbound), f"Expected Inbound, got {type(inbound)}"
    assert isinstance(inbound.stream_settings, (StreamSettings, str)), (
        f"Expected StreamSettings or str, got {type(inbound.stream_settings)}"
    )

    assert isinstance(inbound.sniffing, Sniffing), (
        f"Expected Sniffing, got {type(inbound.sniffing)}"
    )
    assert isinstance(inbound.client_stats[0], Client), (
        f"Expected ClientStats, got {type(inbound.client_stats[0])}"
    )

    assert inbound.id == 1, f"Expected 1, got {inbound.id}"


@pytest.mark.asyncio
async def test_add_inbound(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/add",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.inbound.add(_prepare_inbound())

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_inbound_success(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/del/1",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.inbound.delete(1)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_inbound_failed(httpx_mock: HTTPXMock):
    response_example = {
        ApiFields.SUCCESS: False,
        ApiFields.MSG: "Delete Failed: record not found",
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/del/1",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    with pytest.raises(ValueError):
        await api.inbound.delete(1)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_update_inbound(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/update/1",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.inbound.update(1, _prepare_inbound())

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_database_export(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/backuptotgbot",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.database.export()

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_get_server_status(httpx_mock: HTTPXMock):
    """
    Test for checking server status retrieval
    """
    response_example = json.load(
        open(os.path.join(RESPONSES_DIR, "get_server_status.json"))
    )

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/server/status",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    status = await api.server.get_status()

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert status.cpu == 5.2, f"Expected CPU 5.2, got {status.cpu}"
    assert status.mem.current == 1024000, (
        f"Expected current memory usage 1024, got {status.mem.current}"
    )
    assert status.mem.total == 8192000, (
        f"Expected total memory 8192, got {status.mem.total}"
    )


@pytest.mark.asyncio
async def test_generate_reality_keys(httpx_mock: HTTPXMock):
    """
    Test for generating Reality (X25519) keys
    """
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: {"privateKey": "priv", "publicKey": "pub"},
    }

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/server/getNewX25519Cert",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    keys = await api.server.generate_reality_keys()

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert keys.private_key == "priv", f"Expected 'priv', got {keys.private_key}"
    assert keys.public_key == "pub", f"Expected 'pub', got {keys.public_key}"


@pytest.mark.asyncio
async def test_get_db(httpx_mock: HTTPXMock, tmp_path):
    """
    Test for checking database backup retrieval
    """
    db_content = b"fake database content"
    save_path = tmp_path / "backup.db"

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/server/getDb",
        content=db_content,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.server.get_db(str(save_path))

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert save_path.exists(), "Backup file was not created"
    assert save_path.read_bytes() == db_content, "Backup file content does not match"


@pytest.mark.asyncio
async def test_get_db_failed(httpx_mock: HTTPXMock, tmp_path):
    """
    Test for checking error handling during database backup retrieval
    """
    save_path = tmp_path / "backup.db"

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/server/getDb",
        json={ApiFields.SUCCESS: False, ApiFields.MSG: "Failed to get DB backup"},
        status_code=500,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    with pytest.raises(Exception):
        await api.server.get_db(str(save_path))

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert not save_path.exists(), "Backup file should not have been created"


@pytest.mark.asyncio
async def test_get_inbound_by_id(httpx_mock: HTTPXMock):
    response_example = json.load(
        open(os.path.join(RESPONSES_DIR, "get_inbound_by_id.json"))
    )

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/inbounds/get/1",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    inbound = await api.inbound.get_by_id(1)

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert isinstance(inbound, Inbound), f"Expected Inbound, got {type(inbound)}"
    assert inbound.id == 1, f"Expected 1, got {inbound.id}"
    assert inbound.remark == "test-inbound", (
        f"Expected 'test-inbound', got {inbound.remark}"
    )
    assert inbound.port == 37316, f"Expected 37316, got {inbound.port}"
    assert inbound.protocol == "vless", f"Expected 'vless', got {inbound.protocol}"
    assert inbound.enable is True, f"Expected True, got {inbound.enable}"
    assert isinstance(inbound.client_stats[0], Client), (
        f"Expected Client, got {type(inbound.client_stats[0])}"
    )


@pytest.mark.asyncio
async def test_reset_inbounds_stats(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/resetAllTraffics",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.inbound.reset_stats()

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_reset_inbound_client_stats(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/resetAllTraffics",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.inbound.reset_client_stats(1)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_get_xray_version_available(httpx_mock: HTTPXMock):
    """
    Test for getting Xray version that is available
    """
    response_example_xray_available = {  # When xray can be installed
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: ["1.5.0"],
    }

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/server/getXrayVersion",
        json=response_example_xray_available,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    xray_versions: list[str] = await api.server.get_xray_version()

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert xray_versions == response_example_xray_available[ApiFields.OBJ]


@pytest.mark.asyncio
async def test_get_xray_version_unavailable(httpx_mock: HTTPXMock):
    """
    Test for getting Xray version that is unavailable
    """
    response_example_xray_unavailable = {  # When xray cannot be installed
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: None,
    }

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/server/getXrayVersion",
        json=response_example_xray_unavailable,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    with pytest.raises(XrayVersionUnavailableError):
        await api.server.get_xray_version()

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_install_new_xray_version_unavailable(httpx_mock: HTTPXMock):
    """
    Test for installing new Xray version
    """
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: None,
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/server/installXray/1.5.0",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.server.install_new_xray_version("1.5.0")

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_install_new_xray_version_failed(httpx_mock: HTTPXMock):
    """
    Test for installing new Xray version that is unavailable
    """
    response_example = {
        ApiFields.SUCCESS: False,
        ApiFields.MSG: "",
        ApiFields.OBJ: None,
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/server/installXray/1.5.0",
        json=response_example,
        status_code=400,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    with pytest.raises(Exception):
        await api.server.install_new_xray_version("1.5.0")

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_update_geofile(httpx_mock: HTTPXMock):
    """
    Test for updating geofile successfully
    """
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/server/updateGeofile",
        json={ApiFields.SUCCESS: True},
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    await api.server.update_geofile()

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_update_geofile_failed(httpx_mock: HTTPXMock):
    """
    Test for updating geofile failure
    """

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/server/updateGeofile",
        json={ApiFields.SUCCESS: False},
        status_code=400,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    with pytest.raises(Exception):
        await api.server.update_geofile()

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_get_server_config(httpx_mock: HTTPXMock):
    """
    Test for getting server config
    """
    response_example = json.load(
        open(os.path.join(RESPONSES_DIR, "get_server_config.json"))
    )

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/server/getConfigJson",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    config = await api.server.get_server_config()

    assert config is not None, "Expected config, got None"
    assert isinstance(config.inbounds, list), (
        f"Expected list of inbounds, got {type(config.inbounds)}"
    )
    assert config.log.access == "none", (
        f"Expected access log 'none', got {config.log.access}"
    )
