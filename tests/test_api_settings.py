import json

import pytest
import requests_mock

from py3xui import AllSetting, Api, ApiToken, TgBotCapabilities
from py3xui.api.api_base import ApiFields
from py3xui.setting.setting import AllSettingFields

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
TOKEN = "test-api-token"
SUCCESS = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}
FAILURE = {ApiFields.SUCCESS: False, ApiFields.MSG: "failed", ApiFields.OBJ: None}
OLD_VALUE = "old-value"
NEW_VALUE = "new-value"


def _fixture(name):
    with open(f"{RESPONSES_DIR}/settings_{name}.json", encoding="utf-8") as file:
        return json.load(file)


def _api():
    return Api(HOST, token=TOKEN)


def test_facade_propagates_auth():
    api = Api(HOST, "admin", "admin")
    api.session = "abc123"
    api.csrf_token = "csrf"
    api.cookie_name = "3x-ui"

    assert api.setting.session == "abc123"
    assert api.setting.csrf_token == "csrf"
    assert api.setting.cookie_name == "3x-ui"


def test_get_all():
    fixture = _fixture("all")
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/all", json=fixture)
        settings = _api().setting.get_all()

    assert m.last_request.method == "POST"
    assert isinstance(settings, AllSetting)
    assert settings.web_port == fixture[ApiFields.OBJ][AllSettingFields.WEB_PORT]
    assert settings.sub_enable is True
    assert settings.has_api_token is True
    assert settings.has_tg_bot_token is False
    # Every key of the panel response has a typed field.
    assert not settings.model_extra


def test_get_default_settings():
    fixture = _fixture("default_settings")
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/defaultSettings", json=fixture)
        defaults = _api().setting.get_default_settings()

    assert m.last_request.method == "POST"
    assert defaults == fixture[ApiFields.OBJ]


def test_get_factory_defaults():
    fixture = _fixture("factory_defaults")
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/factoryDefaults", json=fixture)
        defaults = _api().setting.get_factory_defaults()

    assert m.last_request.method == "POST"
    assert defaults == fixture[ApiFields.OBJ]
    assert defaults["webPort"] == "2053"


def test_update_round_trip():
    fixture = _fixture("all")
    obj = dict(fixture[ApiFields.OBJ], someNewKey="kept")
    settings = AllSetting.model_validate(obj)
    settings.sub_title = "My subscription"

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/update", json=SUCCESS)
        _api().setting.update(settings)

    body = m.last_request.json()
    assert m.last_request.method == "POST"
    assert body[AllSettingFields.WEB_PORT] == obj[AllSettingFields.WEB_PORT]
    assert body[AllSettingFields.SUB_TITLE] == "My subscription"
    assert body["someNewKey"] == "kept"
    # Read-only flags are not sent back and optional request fields stay out by default.
    assert not [key for key in body if key.startswith("has")]
    assert "twoFactorCode" not in body
    assert not [key for key in body if key.startswith("clear")]


def test_update_two_factor_code_and_clears():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/update", json=SUCCESS)
        _api().setting.update(
            AllSetting(web_port=2053),
            two_factor_code=123456,
            clear_tg_bot_token=True,
            clear_ldap_password=True,
            clear_smtp_password=True,
            clear_discord_bot_token=True,
        )

    assert m.last_request.json() == {
        "webPort": 2053,
        "twoFactorCode": "123456",
        "clearTgBotToken": True,
        "clearLdapPassword": True,
        "clearSmtpPassword": True,
        "clearDiscordBotToken": True,
    }


def test_update_failure_raises():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/update", json=FAILURE)
        with pytest.raises(ValueError):
            _api().setting.update(AllSetting())


def test_validate_regex():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/validateRegex", json=SUCCESS)
        assert _api().setting.validate_regex("(?m)^general-purpose$") is None

    assert m.last_request.method == "POST"
    assert m.last_request.json() == {"regex": "(?m)^general-purpose$"}


def test_validate_regex_invalid_raises():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/setting/validateRegex",
            json={ApiFields.SUCCESS: False, ApiFields.MSG: "missing closing )"},
        )
        with pytest.raises(ValueError, match="missing closing"):
            _api().setting.validate_regex("(")


def test_update_user():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/updateUser", json=SUCCESS)
        _api().setting.update_user("admin", OLD_VALUE, "newadmin", NEW_VALUE)

    assert m.last_request.method == "POST"
    assert m.last_request.json() == {
        "oldUsername": "admin",
        "oldPassword": OLD_VALUE,
        "newUsername": "newadmin",
        "newPassword": NEW_VALUE,
    }


def test_update_user_two_factor_code():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/updateUser", json=SUCCESS)
        _api().setting.update_user("admin", OLD_VALUE, "newadmin", NEW_VALUE, 123456)

    assert m.last_request.json()["twoFactorCode"] == "123456"


def test_restart_panel():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/restartPanel", json=SUCCESS)
        assert _api().setting.restart_panel() is None

    assert m.last_request.method == "POST"


def test_test_smtp():
    fixture = _fixture("test_smtp")
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/testSmtp", json=fixture)
        result = _api().setting.test_smtp()

    assert m.last_request.method == "POST"
    assert result == fixture


def test_test_smtp_failure_is_returned():
    fixture = _fixture("test_smtp_failed")
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/testSmtp", json=fixture)
        result = _api().setting.test_smtp()

    assert result["success"] is False
    assert result["stage"] == "connect"


def test_test_tg_bot():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/testTgBot", json=SUCCESS)
        assert _api().setting.test_tg_bot() is None

    assert m.last_request.method == "POST"


def test_get_tg_bot_capabilities():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/setting/tgBotCapabilities",
            json=_fixture("tg_bot_capabilities"),
        )
        capabilities = _api().setting.get_tg_bot_capabilities()

    assert m.last_request.method == "POST"
    assert capabilities == TgBotCapabilities(
        inline_enabled=True, group_privacy=False, username="xui_bot", running=True
    )


def test_test_discord():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/testDiscord", json=SUCCESS)
        assert _api().setting.test_discord() is None

    assert m.last_request.method == "POST"


def test_get_default_xray_config():
    fixture = _fixture("default_xray_config")
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/setting/getDefaultJsonConfig", json=fixture)
        config = _api().setting.get_default_xray_config()

    assert m.last_request.method == "GET"
    assert config == fixture[ApiFields.OBJ]


def test_get_api_tokens():
    fixture = _fixture("api_tokens")
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/setting/apiTokens", json=fixture)
        tokens = _api().setting.get_api_tokens()

    assert m.last_request.method == "GET"
    assert tokens == [
        ApiToken(
            id=1,
            name="central-panel-a",
            enabled=True,
            created_at=1736000000,
            scope="node-admin",
            expires_at=0,
        )
    ]
    assert tokens[0].token == ""


def test_add_api_token():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/setting/apiTokens/create",
            json=_fixture("api_token_created"),
        )
        token = _api().setting.add_api_token(
            "central-panel-a", "node-admin", 1798761600000
        )

    assert m.last_request.method == "POST"
    assert m.last_request.json() == {
        "name": "central-panel-a",
        "scope": "node-admin",
        "expiresAt": 1798761600000,
    }
    assert token.id == 2
    assert token.token == "new-token-string"


def test_add_api_token_defaults():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/setting/apiTokens/create",
            json=_fixture("api_token_created"),
        )
        _api().setting.add_api_token("central-panel-a")

    assert m.last_request.json() == {
        "name": "central-panel-a",
        "scope": "admin",
        "expiresAt": 0,
    }


def test_delete_api_token():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/apiTokens/delete/2", json=SUCCESS)
        assert _api().setting.delete_api_token(2, "node-sync") is None

    assert m.last_request.method == "POST"
    assert m.last_request.json() == {"expectedScope": "node-sync"}


def test_delete_api_token_scope_mismatch_raises():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/setting/apiTokens/delete/2",
            json={
                ApiFields.SUCCESS: False,
                ApiFields.MSG: "token not found with expected scope",
            },
        )
        with pytest.raises(ValueError, match="expected scope"):
            _api().setting.delete_api_token(2, "admin")


def test_set_api_token_enabled():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/setting/apiTokens/setEnabled/2", json=SUCCESS)
        assert _api().setting.set_api_token_enabled(2, False, "node-sync") is None

    assert m.last_request.method == "POST"
    assert m.last_request.json() == {"enabled": False, "expectedScope": "node-sync"}
