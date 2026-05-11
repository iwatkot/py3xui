import json
import os
import uuid

import pytest
import requests_mock

from py3xui import Api, Client, Inbound
from py3xui.api.api_base import ApiFields
from py3xui.api.api_server import XrayVersionUnavailableError
from py3xui.inbound import Settings, Sniffing, StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alhtim2x"
SESSION = "abc123"
CSRF_TOKEN = "test-csrf-token"
TOKEN = "test-api-token"
CSRF_RESPONSE = {ApiFields.SUCCESS: True, ApiFields.OBJ: CSRF_TOKEN}


def test_login_success():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/csrf-token", json=CSRF_RESPONSE, cookies={"3x-ui": SESSION})
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: True}, cookies={"3x-ui": SESSION})
        api = Api(HOST, "username", "password")
        api.login()
        assert api.client.session == SESSION, f"Expected {SESSION}, got {api.client.session}"
        assert api.csrf_token == CSRF_TOKEN, f"Expected {CSRF_TOKEN}, got {api.csrf_token}"
        assert api.inbound.csrf_token == CSRF_TOKEN
        assert m.request_history[1].headers["X-CSRF-Token"] == CSRF_TOKEN


def test_login_failed():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/csrf-token", json=CSRF_RESPONSE, cookies={"3x-ui": SESSION})
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: False})
        api = Api(HOST, "username", "password")
        with pytest.raises(ValueError):
            api.client.login()


def test_login_failed_without_csrf_token():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/csrf-token",
            json={ApiFields.SUCCESS: True, ApiFields.OBJ: None},
        )
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: True})
        api = Api(HOST, "username", "password")

        with pytest.raises(ValueError):
            api.login()

        assert len(m.request_history) == 1


def test_logged_in_requests_include_csrf_header():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/csrf-token", json=CSRF_RESPONSE, cookies={"3x-ui": SESSION})
        m.post(f"{HOST}/login", json={ApiFields.SUCCESS: True}, cookies={"3x-ui": SESSION})
        m.get(f"{HOST}/panel/api/inbounds/list", json=response_example)

        api = Api(HOST, "username", "password")
        api.login()
        api.inbound.get_list()

        assert m.request_history[2].headers["X-CSRF-Token"] == CSRF_TOKEN


def test_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("XUI_HOST", HOST)
    monkeypatch.setenv("XUI_USERNAME", USERNAME)
    monkeypatch.setenv("XUI_PASSWORD", PASSWORD)
    monkeypatch.delenv("XUI_TOKEN", raising=False)

    api = Api.from_env()
    assert api.inbound.host == HOST, f"Expected {HOST}, got {api.inbound.host}"
    assert api.inbound.username == USERNAME, f"Expected {USERNAME}, got {api.inbound.username}"
    assert api.inbound.password == PASSWORD, f"Expected {PASSWORD}, got {api.inbound.password}"
    assert api.inbound.token is None


def test_from_env_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("XUI_HOST", HOST)
    monkeypatch.setenv("XUI_TOKEN", TOKEN)
    monkeypatch.delenv("XUI_USERNAME", raising=False)
    monkeypatch.delenv("XUI_PASSWORD", raising=False)

    api = Api.from_env()
    assert api.inbound.host == HOST, f"Expected {HOST}, got {api.inbound.host}"
    assert api.inbound.username is None
    assert api.inbound.password is None
    assert api.inbound.token == TOKEN


def test_from_env_requires_credentials_without_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("XUI_HOST", HOST)
    monkeypatch.delenv("XUI_USERNAME", raising=False)
    monkeypatch.delenv("XUI_PASSWORD", raising=False)
    monkeypatch.delenv("XUI_TOKEN", raising=False)

    with pytest.raises(ValueError):
        Api.from_env()


def test_token_auth_uses_authorization_header():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/list", json=response_example)
        api = Api(HOST, token=TOKEN)
        inbounds = api.inbound.get_list()

        assert len(inbounds) == 1, f"Expected 1, got {len(inbounds)}"
        assert m.last_request.headers["Authorization"] == f"Bearer {TOKEN}"
        assert m.last_request.headers["Accept"] == "application/json"


def test_login_rejected_with_token():
    api = Api(HOST, token=TOKEN)

    with pytest.raises(RuntimeError):
        api.login()


def test_credentials_or_token_required():
    with pytest.raises(ValueError):
        Api(HOST)


def test_get_inbounds():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_inbounds.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/list", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        inbounds = api.inbound.get_list()
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
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.inbound.add(_prepare_inbound())


def test_delete_inbound_success_():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/del/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.inbound.delete(1)


def test_delete_inbound_failed():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/del/1",
            json={ApiFields.SUCCESS: False, ApiFields.MSG: "Delete Failed: record not found"},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        with pytest.raises(ValueError):
            api.inbound.delete(1)


def test_update_inbound():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/update/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.inbound.update(1, _prepare_inbound())


def test_get_client():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/getClientTraffics/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        client = api.client.get_by_email(EMAIL)
        assert isinstance(client, Client), f"Expected Client, got {type(client)}"

        assert client.email == EMAIL, f"Expected {EMAIL}, got {client.email}"
        assert client.id == 1, f"Expected 1, got {client.id}"
        assert client.inbound_id == 1, f"Expected 1, got {client.inbound_id}"


def test_get_client_ips():
    response_example = {"success": True, "msg": "", "obj": "No IP Record"}

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/clientIps/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        ips = api.client.get_ips(EMAIL)

        assert ips == [], f"Expected None, got {ips}"


def test_add_clients():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/addClient", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.add(1, [client])


def test_update_client():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/updateClient/{client.id}", json={ApiFields.SUCCESS: True}
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.update(client.id, client)


def test_reset_client_ips():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/clearClientIps/{EMAIL}", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.reset_ips(EMAIL)


def test_reset_inbounds_stats():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/resetAllTraffics", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.inbound.reset_stats()


def test_reset_inbound_client_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/resetAllClientTraffics/1", json={ApiFields.SUCCESS: True}
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.inbound.reset_client_stats(1)


def test_reset_client_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/1/resetClientTraffic/{EMAIL}",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.reset_stats(1, EMAIL)


def test_delete_client():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/1/delClient/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.delete(1, "1")


def test_delete_depleted_clients():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/delDepletedClients/1", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.delete_depleted(1)


def test_client_online():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/inbounds/onlines", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.online()


def test_get_client_traffic_by_id():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client_traffic_by_id.json")))
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/inbounds/getClientTrafficsById/239708ef-487e-4945-829d-ad79a0ce067e",
            json=response_example,
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        clients = api.client.get_traffic_by_id("239708ef-487e-4945-829d-ad79a0ce067e")

        assert len(clients) == 1, f"Expected 1, got {len(clients)}"

        client = clients[0]

        assert isinstance(client, Client), f"Expected Client, got {type(client)}"
        assert client.email == "test", f"Expected test, got {client.email}"
        assert client.id == 1, f"Expected 1, got {client.id}"


def test_database_export():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/inbounds/createbackup", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.database.export()


def test_get_status():
    """
    Test for get_status() method of ServerApi class
    """
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_server_status.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/status", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        status = api.server.get_status()

        assert status.cpu == 5.2, f"Expected CPU 5.2%, got {status.cpu}%"
        assert (
            status.mem.current == 1024000
        ), f"Expected current memory 1024000, got {status.mem.current}"
        assert status.mem.total == 8192000, f"Expected total memory 8192000, got {status.mem.total}"


def test_get_db():
    """
    Test for get_db() method of ServerApi class
    """
    test_content = b"test database content"
    save_path = "test_backup.db"

    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/server/getDb",
            content=test_content,
            headers={"Content-Type": "application/octet-stream"},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        api.server.get_db(save_path)

        # Check saved file contents
        with open(save_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == test_content, f"Expected {test_content}, got {saved_content}"

        # Remove test file
        import os

        os.remove(save_path)


def test_get_db_failed():
    """
    Test error handling when getting DB backup fails
    """
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/getDb", status_code=500)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(Exception):
            api.server.get_db("failed_backup.db")


def test_generate_reality_keys():
    """
    Test for generating Reality (X25519) keys
    """
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: {"privateKey": "priv", "publicKey": "pub"},
    }

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/getNewX25519Cert", json=response_example)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        keys = api.server.generate_reality_keys()

        assert m.called, "Mocked request was not called"
        assert keys.private_key == "priv", f"Expected 'priv', got {keys.private_key}"
        assert keys.public_key == "pub", f"Expected 'pub', got {keys.public_key}"


def test_get_xray_version_available():
    """
    Test for getting Xray version that is available
    """
    response_example_xray_available = {  # When xray can be installed
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: ["1.5.0"],
    }

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/getXrayVersion", json=response_example_xray_available)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        xray_versions: list[str] = api.server.get_xray_version()

        assert m.called, "Mocked request was not called"
        assert xray_versions == response_example_xray_available[ApiFields.OBJ]


def test_get_xray_version_unavailable():
    """
    Test for getting Xray version that is unavailable
    """
    response_example_xray_unavailable = {  # When xray cannot be installed
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: None,
    }

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/getXrayVersion", json=response_example_xray_unavailable)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(XrayVersionUnavailableError):
            api.server.get_xray_version()

        assert m.called, "Mocked request was not called"


def test_install_new_xray_version_unavailable():
    """
    Test for installing new Xray version
    """
    response_example = {
        ApiFields.SUCCESS: True,
        ApiFields.MSG: "",
        ApiFields.OBJ: None,
    }

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/server/installXray/1.5.0", json=response_example)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(ValueError):
            api.server.install_new_xray_version("1.5.0")

        assert m.called, "Mocked request was not called"


def test_install_new_xray_version_failed():
    """
    Test for installing new Xray version that is unavailable
    """
    response_example = {
        ApiFields.SUCCESS: False,
        ApiFields.MSG: "",
        ApiFields.OBJ: None,
    }

    with requests_mock.Mocker() as m:
        # 
        m.post(f"{HOST}/panel/api/server/installXray/1.5.0", json=response_example, status_code=400)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(Exception):
            api.server.install_new_xray_version("1.5.0")

        assert m.called, "Mocked request was not called"


def test_update_geofile():
    """
    Test for updating geofile successfully
    """
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/server/updateGeofile", json={ApiFields.SUCCESS: True})

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        api.server.update_geofile()

        assert m.called, "Mocked request was not called"

def test_update_geofile_failed():
    """
    Test for updating geofile failure
    """
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/server/updateGeofile", json={ApiFields.SUCCESS: False}, status_code=400)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(Exception):
            api.server.update_geofile()

        assert m.called, "Mocked request was not called"


def test_get_server_config():
    """
    Test for getting server config
    """
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_server_config.json")))

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/getConfigJson", json=response_example)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        config = api.server.get_server_config()

        assert config is not None, "Expected config, got None"
        assert isinstance(config.inbounds, list), f"Expected list of inbounds, got {type(config.inbounds)}"
        assert config.log.access == "none", f"Expected access log 'none', got {config.log.access}"

# endregion
