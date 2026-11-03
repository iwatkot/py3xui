import json
import logging
import os
import uuid

import pytest
import requests_mock

from py3xui import Api, Client, ClientDetails, Inbound
from py3xui.api.api_base import ApiFields
from py3xui.api.api_server import XrayVersionUnavailableError
from py3xui.inbound import Settings, Sniffing, StreamSettings

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alhtim2x"
CSRF_TOKEN = "test-csrf-token"
TOKEN = "test-api-token"
CSRF_RESPONSE = {ApiFields.SUCCESS: True, ApiFields.OBJ: CSRF_TOKEN}

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


def test_login_success():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/csrf-token", json=CSRF_RESPONSE, cookies={"3x-ui": SESSION})
        m.post(
            f"{HOST}/login", json={ApiFields.SUCCESS: True}, cookies={"3x-ui": SESSION}
        )
        api = Api(HOST, "username", "password")
        api.login()
        assert api.client.session == SESSION, (
            f"Expected {SESSION}, got {api.client.session}"
        )
        assert api.csrf_token == CSRF_TOKEN, (
            f"Expected {CSRF_TOKEN}, got {api.csrf_token}"
        )
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
        m.post(
            f"{HOST}/login", json={ApiFields.SUCCESS: True}, cookies={"3x-ui": SESSION}
        )
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
    assert api.inbound.username == USERNAME, (
        f"Expected {USERNAME}, got {api.inbound.username}"
    )
    assert api.inbound.password == PASSWORD, (
        f"Expected {PASSWORD}, got {api.inbound.password}"
    )
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
            json={
                ApiFields.SUCCESS: False,
                ApiFields.MSG: "Delete Failed: record not found",
            },
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
        m.get(
            f"{HOST}/panel/api/clients/get/{EMAIL}",
            json=response_example,
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        client = api.client.get_by_email(EMAIL)
        assert isinstance(client, Client), f"Expected Client, got {type(client)}"

        assert client.email == EMAIL, f"Expected {EMAIL}, got {client.email}"
        assert client.id == 1, f"Expected 1, got {client.id}"
        assert client.inbound_id == 1, f"Expected 1, got {client.inbound_id}"


def test_get_client_nested_payload_shape():
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

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/get/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        client = api.client.get_by_email(EMAIL)

        assert isinstance(client, Client)
        assert client.inbound_id == 9


def test_get_client_ips_with_records():
    response_example = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: ["1.1.1.1"]}

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/ips/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        ips = api.client.get_ips(EMAIL)

        assert ips == ["1.1.1.1"]


def test_get_client_ips():
    response_example = {"success": True, "msg": "", "obj": "No IP Record"}

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/ips/{EMAIL}", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        ips = api.client.get_ips(EMAIL)

        assert ips == [], f"Expected None, got {ips}"


def test_add_clients():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/add", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.add(1, [client])


def test_update_client():
    client = Client(id=str(uuid.uuid4()), email="test", enable=True)
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/update/{client.email}",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.update(client.id, client)


def test_update_client_normalizes_id_from_uuid():
    client = Client(id=1, uuid=str(uuid.uuid4()), email="test", enable=True)
    response_ok = {ApiFields.SUCCESS: True}

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/update/{client.email}", json=response_ok)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.update("legacy-id", client)

        payload = m.last_request.json()
        assert payload["id"] == client.uuid


def test_get_client_details():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client_details.json")))

    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/get/{DETAILS_EMAIL_QUOTED}",
            json=response_example,
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        details = api.client.get_details(DETAILS_EMAIL)

        assert m.last_request.method == "GET"
        assert isinstance(details, ClientDetails)
        assert details.inbound_ids == [3, 5]
        assert details.tunnel_allowed_ips == {3: "10.66.0.2/32", 5: "10.77.0.2/32"}
        assert details.used_traffic == 1073741824
        assert details.external_links[0]["value"] == "vless://example"

        client = details.client
        assert client.email == DETAILS_EMAIL
        assert client.uuid == "6f0f4c4e-7d4c-4b9e-9a51-2c1f4e8d7a10"
        assert client.group == "staff"
        assert client.private_key.startswith("fake-private")
        assert client.allowed_ips == ["10.66.0.2/32", "fd00:66::2/128"]
        assert client.keep_alive == 25
        assert client.reverse == {"tag": "reverse-out"}
        assert client.limit_hwid == 3
        assert client.traffic_reset == "monthly"
        assert client.created_at == 1735689600000
        assert client.futureField == {"nested": [1, 2, 3]}  # type: ignore[attr-defined]


def test_get_client_details_not_found():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/get/{EMAIL}",
            json={ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        assert api.client.get_details(EMAIL) is None


def test_get_client_details_update_round_trip_keeps_all_fields():
    response_example = json.load(open(os.path.join(RESPONSES_DIR, "get_client_details.json")))
    record = response_example[ApiFields.OBJ]["client"]

    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/get/{DETAILS_EMAIL_QUOTED}",
            json=response_example,
        )
        m.post(
            f"{HOST}/panel/api/clients/update/{DETAILS_EMAIL_QUOTED}",
            json={ApiFields.SUCCESS: True, ApiFields.MSG: "Client updated"},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        details = api.client.get_details(DETAILS_EMAIL)
        assert details is not None
        details.client.total_gb = 50 * 1024**3
        api.client.update(details.client.uuid, details.client)

        assert m.last_request.method == "POST"
        assert m.last_request.json() == _expected_round_trip_payload(record)


def test_client_model_dump_keeps_unknown_fields():
    client = Client.model_validate(
        {"email": "test", "enable": True, "limitHwid": 2, "someNewField": "value"}
    )

    dumped = client.model_dump(by_alias=True, exclude_defaults=True)

    assert dumped == {"email": "test", "enable": True, "limitHwid": 2, "someNewField": "value"}


def test_get_client_details_missing_client_returns_none():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/get/{EMAIL}",
            json={ApiFields.SUCCESS: False, ApiFields.MSG: "Obtain (record not found)"},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        assert api.client.get_details(EMAIL) is None


def test_get_client_details_other_panel_errors_are_raised():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/get/{EMAIL}",
            json={ApiFields.SUCCESS: False, ApiFields.MSG: "Obtain (database is locked)"},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(ValueError, match="database is locked"):
            api.client.get_details(EMAIL)


def test_update_client_does_not_log_secrets(caplog):
    client = Client(email="test", enable=True, private_key="private-key-value")
    logger = logging.getLogger("py3xui-test")
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/update/test", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD, logger=logger)
        api.session = SESSION

        with caplog.at_level(logging.INFO, logger="py3xui-test"):
            api.client.update("id", client)

    assert "private-key-value" not in caplog.text


def test_client_ignores_reverse_that_is_not_an_object():
    client = Client.model_validate({"email": "test", "enable": True, "reverse": "not json"})

    assert client.reverse is None
    assert "reverse" not in client.model_dump(by_alias=True, exclude_defaults=True)


def test_reset_client_ips():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/clearIps/{EMAIL}",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.reset_ips(EMAIL)


def test_reset_inbounds_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/inbounds/resetAllTraffics",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.inbound.reset_stats()


def test_reset_inbound_client_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/resetAllTraffics",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.inbound.reset_client_stats(1)


def test_reset_client_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/resetTraffic/{EMAIL}",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.reset_stats(1, EMAIL)


def test_delete_client():
    response_clients = json.load(open(os.path.join(RESPONSES_DIR, "get_client_traffic_by_id.json")))
    response_clients[ApiFields.OBJ][0]["uuid"] = "d76eb6ed-0697-4cd5-a8c5-8cfeb4d1b209"
    client_uuid = response_clients[ApiFields.OBJ][0]["uuid"]
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/list", json=response_clients)
        m.post(
            f"{HOST}/panel/api/clients/del/test", json={ApiFields.SUCCESS: True}
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.delete(1, client_uuid)


def test_delete_client_by_email_skips_lookup():
    email = "user@example.com"
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/del/{email}", json={ApiFields.SUCCESS: True})

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.delete(1, email)

        assert len(m.request_history) == 1


def test_delete_client_unresolvable_identifier_raises():
    response_clients = {ApiFields.SUCCESS: True, ApiFields.OBJ: [{"id": 2, "uuid": "u2", "email": "e2"}]}

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/list", json=response_clients)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(ValueError):
            api.client.delete(1, "unknown-id")


def test_delete_depleted_clients():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/delDepleted",
            json={ApiFields.SUCCESS: True},
        )
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.delete_depleted(1)


def test_client_online():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/onlines", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.client.online()


def test_client_online_empty_obj_returns_empty_list():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/onlines",
            json={ApiFields.SUCCESS: True, ApiFields.OBJ: None},
        )

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        assert api.client.online() == []


def test_get_client_traffic_by_id():
    response_example = json.load(
        open(os.path.join(RESPONSES_DIR, "get_client_traffic_by_id.json"))
    )
    response_example[ApiFields.OBJ][0]["uuid"] = "239708ef-487e-4945-829d-ad79a0ce067e"
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/list",
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
        m.post(f"{HOST}/panel/api/backuptotgbot", json={ApiFields.SUCCESS: True})
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION
        api.database.export()


def test_get_status():
    """
    Test for get_status() method of ServerApi class
    """
    response_example = json.load(
        open(os.path.join(RESPONSES_DIR, "get_server_status.json"))
    )

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/status", json=response_example)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        status = api.server.get_status()

        assert status.cpu == 5.2, f"Expected CPU 5.2%, got {status.cpu}%"
        assert status.mem.current == 1024000, (
            f"Expected current memory 1024000, got {status.mem.current}"
        )
        assert status.mem.total == 8192000, (
            f"Expected total memory 8192000, got {status.mem.total}"
        )


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
        assert saved_content == test_content, (
            f"Expected {test_content}, got {saved_content}"
        )

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
        m.get(
            f"{HOST}/panel/api/server/getXrayVersion",
            json=response_example_xray_available,
        )

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
        m.get(
            f"{HOST}/panel/api/server/getXrayVersion",
            json=response_example_xray_unavailable,
        )

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
        m.post(
            f"{HOST}/panel/api/server/installXray/1.5.0",
            json=response_example,
            status_code=400,
        )

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
        m.post(
            f"{HOST}/panel/api/server/updateGeofile",
            json={ApiFields.SUCCESS: False},
            status_code=400,
        )

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        with pytest.raises(Exception):
            api.server.update_geofile()

        assert m.called, "Mocked request was not called"


def test_get_server_config():
    """
    Test for getting server config
    """
    response_example = json.load(
        open(os.path.join(RESPONSES_DIR, "get_server_config.json"))
    )

    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/server/getConfigJson", json=response_example)

        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        config = api.server.get_server_config()

        assert config is not None, "Expected config, got None"
        assert isinstance(config.inbounds, list), (
            f"Expected list of inbounds, got {type(config.inbounds)}"
        )
        assert config.log.access == "none", (
            f"Expected access log 'none', got {config.log.access}"
        )


# endregion
