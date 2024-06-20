import json
import os
import uuid

import pytest
import requests_mock

from py3xui import Api, Client, Inbound
from py3xui.api.api_base import ApiFields
from py3xui.inbound import Settings, Sniffing, StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alhtim2x"


def test_login_success():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: True}, cookies={"session": SESSION})
        api = Api(HOST, "username", "password", skip_login=True)
        api.login()
        assert api.client.session == SESSION, f"Expected {SESSION}, got {api.client.session}"


def test_login_failed():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: True})
        api = Api(HOST, "username", "password", skip_login=True)
        with pytest.raises(ValueError):
            api.client.login()


def test_from_env():
    os.environ["XUI_HOST"] = HOST
    os.environ["XUI_USERNAME"] = USERNAME
    os.environ["XUI_PASSWORD"] = PASSWORD

    api = Api.from_env(skip_login=True)
    assert api.inbound.host == HOST, f"Expected {HOST}, got {api.host}"
    assert api.inbound.username == USERNAME, f"Expected {USERNAME}, got {api.username}"
    assert api.inbound.password == PASSWORD, f"Expected {PASSWORD}, got {api.password}"


def test_get_inbounds():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/list", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        inbounds = api.inbound.get_list()
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


def test_get_client():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/getClientTraffics/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        client = api.client.get_by_email(EMAIL)
        assert isinstance(client, Client), f"Expected Client, got {type(client)}"

        assert client.email == EMAIL, f"Expected {EMAIL}, got {client.email}"
        assert client.id == 1, f"Expected 1, got {client.id}"
        assert client.inbound_id == 1, f"Expected 1, got {client.inbound_id}"


def test_get_client_ips():
    response_example = {"success": True, "msg": "", "obj": "No IP Record"}

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/clientIps/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        ips = api.client.get_ips(EMAIL)

        assert ips == [], f"Expected None, got {ips}"


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


def test_add_inbound():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/add", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.inbound.add(_prepare_inbound())


def test_delete_inbound_success_():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/del/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.inbound.delete(1)


def test_delete_inbound_failed():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/del/1",
            json={ApiFields.SUCCESS: False, ApiFields.MSG: "Delete Failed: record not found"},
        )
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        with pytest.raises(ValueError):
            api.inbound.delete(1)


def test_update_inbound():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/update/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.inbound.update(1, _prepare_inbound())


def test_add_clients():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/addClient", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.client.add(1, [client])


def test_update_client():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/updateClient/{client.id}", json={ApiFields.SUCCESS: True}
        )
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.client.update(client.id, client)


def test_reset_client_ips():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/clearClientIps/{EMAIL}", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.client.reset_ips(EMAIL)


def test_reset_inbounds_stats():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/resetAllTraffics", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.inbound.reset_stats()


def test_reset_inbound_client_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/resetAllClientTraffics/1", json={ApiFields.SUCCESS: True}
        )
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.inbound.reset_client_stats(1)


def test_reset_client_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/1/resetClientTraffic/{EMAIL}",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.client.reset_stats(1, EMAIL)


def test_delete_client():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/1/delClient/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.client.delete(1, "1")


def test_delete_depleted_clients():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/delDepletedClients/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.client.delete_depleted(1)


def test_client_online():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/onlines", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.client.online()


def test_database_export():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/createbackup", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, skip_login=True)
        api.database.export()
