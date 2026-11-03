import json

import pytest
import requests_mock
from pytest_httpx import HTTPXMock

from py3xui import Api, AsyncApi, Inbound
from py3xui.api.api_base import ApiFields

HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
RESPONSE_OK = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}

WIREGUARD_SETTINGS = {
    "mtu": 1420,
    "secretKey": "fake-secret-key",
    "peers": [{"publicKey": "fake-peer-public-key", "allowedIPs": ["10.0.0.2/32"]}],
    "clients": [{"email": "wg@example.com", "enable": True, "id": "6f0f4c4e"}],
}
SHADOWSOCKS_SETTINGS = {
    "method": "2022-blake3-aes-256-gcm",
    "password": "fake-server-password",
    "network": "tcp,udp",
    "clients": [],
}
STREAM_SETTINGS = {
    "network": "tcp",
    "security": "none",
    "externalProxy": [{"dest": "example.com", "port": 443}],
    "sockopt": {"tcpFastOpen": True},
}
SNIFFING = {"enabled": True, "destOverride": ["http"], "ipsExcluded": ["10.0.0.0/8"]}
STORED_FIELDS = {
    "total": 107374182400,
    "subSortIndex": 3,
    "excludeFromSub": True,
    "trafficReset": "monthly",
    "trafficResetDay": 5,
    "disableFlow": True,
    "shareAddrStrategy": "custom",
    "shareAddr": "share.example.com",
    "tag": "in-443-custom",
    "nodeId": 2,
}
READ_ONLY_FIELDS = {
    "lastTrafficResetTime": 1735689600000,
    "originNodeGuid": "guid",
    "fallbackParent": {"masterId": 1},
}


def _inbound_json(settings: dict) -> dict:
    return {
        "id": 7,
        "enable": True,
        "port": 443,
        "protocol": "wireguard",
        "remark": "test",
        "settings": settings,
        "streamSettings": STREAM_SETTINGS,
        "sniffing": SNIFFING,
        **STORED_FIELDS,
        **READ_ONLY_FIELDS,
    }


def _assert_nothing_lost(payload: dict, settings: dict) -> None:
    for key, value in STORED_FIELDS.items():
        assert payload[key] == value, key
    for key in READ_ONLY_FIELDS:
        assert key not in payload, key
    sent_settings = json.loads(payload["settings"])
    for key, value in settings.items():
        assert sent_settings[key] == value, key
    sent_stream = json.loads(payload["streamSettings"])
    assert sent_stream["externalProxy"] == STREAM_SETTINGS["externalProxy"]
    assert sent_stream["sockopt"] == STREAM_SETTINGS["sockopt"]
    assert json.loads(payload["sniffing"])["ipsExcluded"] == SNIFFING["ipsExcluded"]


@pytest.mark.parametrize("settings", [WIREGUARD_SETTINGS, SHADOWSOCKS_SETTINGS])
def test_get_update_round_trip_keeps_all_fields(settings):
    url = f"{HOST}/panel/api/inbounds"
    with requests_mock.Mocker() as m:
        m.get(
            f"{url}/get/7",
            json={ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: _inbound_json(settings)},
        )
        m.post(f"{url}/update/7", json=RESPONSE_OK)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        inbound = api.inbound.get_by_id(7)
        api.inbound.update(7, inbound)

        _assert_nothing_lost(m.last_request.json(), settings)


@pytest.mark.asyncio
@pytest.mark.parametrize("settings", [WIREGUARD_SETTINGS, SHADOWSOCKS_SETTINGS])
async def test_async_get_update_round_trip_keeps_all_fields(httpx_mock: HTTPXMock, settings):
    url = f"{HOST}/panel/api/inbounds"
    httpx_mock.add_response(
        method="GET",
        url=f"{url}/get/7",
        json={ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: _inbound_json(settings)},
    )
    httpx_mock.add_response(method="POST", url=f"{url}/update/7", json=RESPONSE_OK)
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    inbound = await api.inbound.get_by_id(7)
    await api.inbound.update(7, inbound)

    request = httpx_mock.get_requests(method="POST")[-1]
    _assert_nothing_lost(json.loads(request.content.decode("utf-8")), settings)


def test_settings_clients_are_sent_without_default_values():
    inbound = Inbound.model_validate(
        {
            "enable": True,
            "port": 443,
            "protocol": "vless",
            "settings": {
                "clients": [{"email": "a@example.com", "enable": True, "id": "6f0f4c4e"}],
                "decryption": "none",
            },
            "sniffing": {"enabled": False},
        }
    )

    settings = json.loads(inbound.to_json()["settings"])

    assert settings["clients"] == [{"email": "a@example.com", "enable": True, "id": "6f0f4c4e"}]
    assert settings["decryption"] == "none"
