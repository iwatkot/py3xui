from py3xui.server.config import ServerConfig


def test_server_config_normalize_data_non_dict_passthrough():
    assert ServerConfig.normalize_data("raw") == "raw"


def test_server_config_normalize_data_non_list_inbounds_passthrough():
    payload = {"inbounds": {"id": 1}}
    assert ServerConfig.normalize_data(payload) == payload


def test_server_config_normalize_data_applies_inbound_defaults():
    payload = {
        "inbounds": [
            {
                "id": 1,
                "settings": {"clients": None},
                "streamSettings": None,
                "sniffing": None,
            },
            "skip-non-dict",
        ]
    }

    normalized = ServerConfig.normalize_data(payload)
    inbound = normalized["inbounds"][0]

    assert inbound["enable"] is True
    assert "streamSettings" not in inbound
    assert inbound["sniffing"] == {"enabled": False}
    assert inbound["settings"]["clients"] == []


def test_server_config_normalize_data_sets_client_enable_default():
    payload = {
        "inbounds": [
            {
                "id": 1,
                "settings": {"clients": [{"email": "a@b", "id": "uuid"}]},
            }
        ]
    }

    normalized = ServerConfig.normalize_data(payload)
    client = normalized["inbounds"][0]["settings"]["clients"][0]

    assert client["enable"] is True
