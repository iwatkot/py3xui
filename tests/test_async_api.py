import json
import os
import uuid

import pytest
import respx

from py3xui import AsyncApi, Client, Inbound
from py3xui.inbound import Settings, Sniffing, StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alhtim2x"


# region ClientApi tests


@pytest.mark.asyncio
async def test_get_client():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client.json")))

    with respx.mock:
        request = respx.get(f"{HOST}/panel/api/inbounds/getClientTraffics/{EMAIL}").respond(
            200, json=response_example
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        client = await api.client.get_by_email(EMAIL)

        assert request.called, "Mocked request was not called"
        assert isinstance(client, Client), f"Expected Client, got {type(client)}"
        assert client.email == EMAIL, f"Expected {EMAIL}, got {client.email}"
        assert client.id == 1, f"Expected 1, got {client.id}"


@pytest.mark.asyncio
async def test_get_ips():
    response_example = {"success": True, "msg": "", "obj": "No IP Record"}

    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/clientIps/{EMAIL}").respond(
            200, json=response_example
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        ips = await api.client.get_ips(EMAIL)

        assert request.called, "Mocked request was not called"
        assert ips == [], f"Expected None, got {ips}"


@pytest.mark.asyncio
async def test_add_clients():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/addClient").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.client.add(1, [client])

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_update_client():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/updateClient/{client.id}").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.client.update(client.id, client)

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_reset_client_ips():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/clearClientIps/{EMAIL}").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.client.reset_ips(EMAIL)

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_reset_client_stats():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/1/resetClientTraffic/{EMAIL}").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.client.reset_stats(1, EMAIL)

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_client():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/1/delClient/1").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.client.delete(1, "1")

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_depleted_clients():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/delDepletedClients/1").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.client.delete_depleted(1)

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_client_online():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/onlines").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.client.online()

        assert request.called, "Mocked request was not called"


# endregion
# region InboundApi tests


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
async def test_get_inbounds():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    with respx.mock:
        request = respx.get(f"{HOST}/panel/api/inbounds/list").respond(200, json=response_example)
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        inbounds = await api.inbound.get_list()

        assert request.called, "Mocked request was not called"
        assert len(inbounds) == 1, f"Expected 1, got {len(inbounds)}"
        inbound = inbounds[0]
        assert isinstance(inbound, Inbound), f"Expected Inbound, got {type(inbound)}"
        assert isinstance(
            inbound.stream_settings, StreamSettings
        ), f"Expected StreamSettings, got {type(inbound.stream_settings)}"
        assert isinstance(
            inbound.sniffing, Sniffing
        ), f"Expected Sniffing, got {type(inbound.sniffing)}"
        assert isinstance(
            inbound.client_stats[0], Client
        ), f"Expected ClientStats, got {type(inbound.client_stats[0])}"

        assert inbound.id == 1, f"Expected 1, got {inbound.id}"


@pytest.mark.asyncio
async def test_add_inbound():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/add").respond(200, json={"success": True})
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.inbound.add(_prepare_inbound())

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_inbound_success_():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/del/1").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.inbound.delete(1)

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_delete_inbound_failed():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/del/1").respond(
            200, json={"success": False, "msg": "Delete Failed: record not found"}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        with pytest.raises(ValueError):
            await api.inbound.delete(1)

        assert request.called, "Mocked request was not called"


@pytest.mark.asyncio
async def test_update_inbound():
    with respx.mock:
        request = respx.post(f"{HOST}/panel/api/inbounds/update/1").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.inbound.update(1, _prepare_inbound())

        assert request.called, "Mocked request was not called"


# endregion
# region DatabaseApi tests


@pytest.mark.asyncio
async def test_database_export():
    with respx.mock:
        request = respx.get(f"{HOST}/panel/api/inbounds/createbackup").respond(
            200, json={"success": True}
        )
        api = AsyncApi(HOST, USERNAME, PASSWORD)
        await api.database.export()

        assert request.called, "Mocked request was not called"


# endregion
