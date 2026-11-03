import json

import pytest
from pytest_httpx import HTTPXMock

from py3xui import AllSetting, AsyncApi, TgBotCapabilities
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
    return AsyncApi(HOST, token=TOKEN)


def _body(httpx_mock):
    return json.loads(httpx_mock.get_request().content)


def test_facade_propagates_auth():
    api = AsyncApi(HOST, "admin", "admin")
    api.session = "abc123"
    api.csrf_token = "csrf"
    api.cookie_name = "3x-ui"

    assert api.setting.session == "abc123"
    assert api.setting.csrf_token == "csrf"
    assert api.setting.cookie_name == "3x-ui"


@pytest.mark.asyncio
async def test_get_all(httpx_mock: HTTPXMock):
    fixture = _fixture("all")
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/all", json=fixture
    )
    settings = await _api().setting.get_all()

    assert isinstance(settings, AllSetting)
    assert settings.web_port == fixture[ApiFields.OBJ][AllSettingFields.WEB_PORT]
    assert settings.sub_enable is True
    assert settings.has_api_token is True
    assert settings.has_tg_bot_token is False
    # Every key of the panel response has a typed field.
    assert not settings.model_extra


@pytest.mark.asyncio
async def test_get_default_settings(httpx_mock: HTTPXMock):
    fixture = _fixture("default_settings")
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/defaultSettings", json=fixture
    )
    assert await _api().setting.get_default_settings() == fixture[ApiFields.OBJ]


@pytest.mark.asyncio
async def test_get_factory_defaults(httpx_mock: HTTPXMock):
    fixture = _fixture("factory_defaults")
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/factoryDefaults", json=fixture
    )
    defaults = await _api().setting.get_factory_defaults()

    assert defaults == fixture[ApiFields.OBJ]
    assert defaults["webPort"] == "2053"


@pytest.mark.asyncio
async def test_update_round_trip(httpx_mock: HTTPXMock):
    fixture = _fixture("all")
    obj = dict(fixture[ApiFields.OBJ], someNewKey="kept")
    settings = AllSetting.model_validate(obj)
    settings.sub_title = "My subscription"
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/update", json=SUCCESS
    )

    await _api().setting.update(settings)

    body = _body(httpx_mock)
    assert body[AllSettingFields.WEB_PORT] == obj[AllSettingFields.WEB_PORT]
    assert body[AllSettingFields.SUB_TITLE] == "My subscription"
    assert body["someNewKey"] == "kept"
    # Read-only flags are not sent back and optional request fields stay out by default.
    assert not [key for key in body if key.startswith("has")]
    assert "twoFactorCode" not in body
    assert not [key for key in body if key.startswith("clear")]


@pytest.mark.asyncio
async def test_update_two_factor_code_and_clears(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/update", json=SUCCESS
    )

    await _api().setting.update(
        AllSetting(web_port=2053),
        two_factor_code=123456,
        clear_tg_bot_token=True,
        clear_ldap_password=True,
        clear_smtp_password=True,
        clear_discord_bot_token=True,
    )

    assert _body(httpx_mock) == {
        "webPort": 2053,
        "twoFactorCode": "123456",
        "clearTgBotToken": True,
        "clearLdapPassword": True,
        "clearSmtpPassword": True,
        "clearDiscordBotToken": True,
    }


@pytest.mark.asyncio
async def test_update_failure_raises(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/update", json=FAILURE
    )
    with pytest.raises(ValueError):
        await _api().setting.update(AllSetting())


@pytest.mark.asyncio
async def test_validate_regex(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/validateRegex", json=SUCCESS
    )
    assert await _api().setting.validate_regex("(?m)^general-purpose$") is None
    assert _body(httpx_mock) == {"regex": "(?m)^general-purpose$"}


@pytest.mark.asyncio
async def test_validate_regex_invalid_raises(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/setting/validateRegex",
        json={ApiFields.SUCCESS: False, ApiFields.MSG: "missing closing )"},
    )
    with pytest.raises(ValueError, match="missing closing"):
        await _api().setting.validate_regex("(")


@pytest.mark.asyncio
async def test_update_user(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/updateUser", json=SUCCESS
    )
    await _api().setting.update_user("admin", OLD_VALUE, "newadmin", NEW_VALUE)

    assert _body(httpx_mock) == {
        "oldUsername": "admin",
        "oldPassword": OLD_VALUE,
        "newUsername": "newadmin",
        "newPassword": NEW_VALUE,
    }


@pytest.mark.asyncio
async def test_update_user_two_factor_code(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/updateUser", json=SUCCESS
    )
    await _api().setting.update_user(
        "admin", OLD_VALUE, "newadmin", NEW_VALUE, 123456
    )

    assert _body(httpx_mock)["twoFactorCode"] == "123456"


@pytest.mark.asyncio
async def test_restart_panel(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/restartPanel", json=SUCCESS
    )
    assert await _api().setting.restart_panel() is None


@pytest.mark.asyncio
async def test_test_smtp(httpx_mock: HTTPXMock):
    fixture = _fixture("test_smtp")
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/testSmtp", json=fixture
    )
    assert await _api().setting.test_smtp() == fixture


@pytest.mark.asyncio
async def test_test_smtp_failure_is_returned(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/setting/testSmtp",
        json=_fixture("test_smtp_failed"),
    )
    result = await _api().setting.test_smtp()

    assert result["success"] is False
    assert result["stage"] == "connect"


@pytest.mark.asyncio
async def test_test_tg_bot(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/testTgBot", json=SUCCESS
    )
    assert await _api().setting.test_tg_bot() is None


@pytest.mark.asyncio
async def test_get_tg_bot_capabilities(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/setting/tgBotCapabilities",
        json=_fixture("tg_bot_capabilities"),
    )
    capabilities = await _api().setting.get_tg_bot_capabilities()

    assert capabilities == TgBotCapabilities(
        inline_enabled=True, group_privacy=False, username="xui_bot", running=True
    )


@pytest.mark.asyncio
async def test_test_discord(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/setting/testDiscord", json=SUCCESS
    )
    assert await _api().setting.test_discord() is None


@pytest.mark.asyncio
async def test_get_default_xray_config(httpx_mock: HTTPXMock):
    fixture = _fixture("default_xray_config")
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/setting/getDefaultJsonConfig",
        json=fixture,
    )
    assert await _api().setting.get_default_xray_config() == fixture[ApiFields.OBJ]
