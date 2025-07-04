import json
import os
import uuid

import pytest
from pytest_httpx import HTTPXMock

from py3xui import AsyncApi, Client, Inbound
from py3xui.api.api_base import ApiFields
from py3xui.inbound import Settings, Sniffing, StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alhtim2x"
RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"


@pytest.mark.asyncio
async def test_from_env():
    os.environ["XUI_HOST"] = HOST
    os.environ["XUI_USERNAME"] = USERNAME
    os.environ["XUI_PASSWORD"] = PASSWORD

    api = AsyncApi.from_env()
    assert api.inbound.host == HOST, f"Expected {HOST}, got {api.host}"
    assert api.inbound.username == USERNAME, f"Expected {USERNAME}, got {api.username}"
    assert api.inbound.password == PASSWORD, f"Expected {PASSWORD}, got {api.password}"


@pytest.mark.asyncio
async def test_login_failed(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/login",
        json={ApiFields.SUCCESS: False},
        status_code=200,
    )

    api = AsyncApi(HOST, "username", "password")
    with pytest.raises(ValueError):
        await api.client.login()


@pytest.mark.asyncio
async def test_login_success(httpx_mock: HTTPXMock):
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
async def test_get_client(httpx_mock: HTTPXMock):
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client.json")))

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/inbounds/getClientTraffics/{EMAIL}",
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
async def test_get_ips(httpx_mock: HTTPXMock):
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: ApiFields.NO_IP_RECORD,
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/clientIps/{EMAIL}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    ips = await api.client.get_ips(EMAIL)

    assert ips == [], f"Expected [], got {ips}"


@pytest.mark.asyncio
async def test_add_clients(httpx_mock: HTTPXMock):
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/addClient",
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
        url=f"{HOST}/panel/api/inbounds/updateClient/{client.id}",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.update(client.id, client)

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_reset_client_ips(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/clearClientIps/{EMAIL}",
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
        url=f"{HOST}/panel/api/inbounds/1/resetClientTraffic/{EMAIL}",
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

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/1/delClient/1",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.delete(1, "1")

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_depleted_clients(httpx_mock: HTTPXMock):
    response_example = {ApiFields.SUCCESS: True}

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/inbounds/delDepletedClients/1",
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
        url=f"{HOST}/panel/api/inbounds/onlines",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.client.online()

    assert httpx_mock.get_request(), "Mocked request was not called"


@pytest.mark.asyncio
async def test_get_client_traffic_by_id(httpx_mock: HTTPXMock):
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client_traffic_by_id.json")))

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/inbounds/getClientTrafficsById/239708ef-487e-4945-829d-ad79a0ce067e",
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
    stream_settings = StreamSettings(security="reality", network="tcp", tcp_settings=tcp_settings)

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
    assert isinstance(
        inbound.stream_settings, (StreamSettings, str)
    ), f"Expected StreamSettings or str, got {type(inbound.stream_settings)}"

    assert isinstance(
        inbound.sniffing, Sniffing
    ), f"Expected Sniffing, got {type(inbound.sniffing)}"
    assert isinstance(
        inbound.client_stats[0], Client
    ), f"Expected ClientStats, got {type(inbound.client_stats[0])}"

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
    response_example = {ApiFields.SUCCESS: False, ApiFields.MSG: "Delete Failed: record not found"}

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
        method="GET",
        url=f"{HOST}/panel/api/inbounds/createbackup",
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
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_server_status.json")))

    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/server/status",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    status = await api.server.get_status()

    assert httpx_mock.get_request(), "Mocked request was not called"
    assert status.cpu == 5.2, f"Expected CPU 5.2, got {status.cpu}"
    assert (
        status.mem.current == 1024000
    ), f"Expected current memory usage 1024, got {status.mem.current}"
    assert status.mem.total == 8192000, f"Expected total memory 8192, got {status.mem.total}"


@pytest.mark.asyncio
async def test_get_db(httpx_mock: HTTPXMock, tmp_path):
    """
    Test for checking database backup retrieval
    """
    db_content = b"fake database content"
    save_path = tmp_path / "backup.db"

    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/server/getDb",
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
        url=f"{HOST}/server/getDb",
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
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbound_by_id.json")))

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
    assert inbound.remark == "test-inbound", f"Expected 'test-inbound', got {inbound.remark}"
    assert inbound.port == 37316, f"Expected 37316, got {inbound.port}"
    assert inbound.protocol == "vless", f"Expected 'vless', got {inbound.protocol}"
    assert inbound.enable is True, f"Expected True, got {inbound.enable}"
    assert isinstance(
        inbound.client_stats[0], Client
    ), f"Expected Client, got {type(inbound.client_stats[0])}"


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
        url=f"{HOST}/panel/api/inbounds/resetAllClientTraffics/1",
        json=response_example,
        status_code=200,
    )

    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    await api.inbound.reset_client_stats(1)

    assert httpx_mock.get_request(), "Mocked request was not called"
