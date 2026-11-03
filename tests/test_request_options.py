import pytest
import requests_mock
from pytest_httpx import HTTPXMock

from py3xui import Api, AsyncApi
from py3xui.api.api_base import ApiFields

HOST = "http://localhost"
TOKEN = "test-api-token"
EMAIL = "test"
URL = f"{HOST}/panel/api/clients/clearIps/{EMAIL}"
RESPONSE_OK = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}
GROUPS = ("client", "inbound", "database", "server")


def test_timeout_is_sent_with_requests():
    with requests_mock.Mocker() as m:
        m.post(URL, json=RESPONSE_OK)

        Api(HOST, token=TOKEN, timeout=15).client.reset_ips(EMAIL)

        assert m.last_request.timeout == 15


def test_default_timeout_is_not_set():
    with requests_mock.Mocker() as m:
        m.post(URL, json=RESPONSE_OK)

        Api(HOST, token=TOKEN).client.reset_ips(EMAIL)

        assert m.last_request.timeout is None


def test_facade_settings_reach_all_groups():
    api = Api(HOST, token=TOKEN, timeout=15)
    api.max_retries = 1

    assert api.timeout == 15
    assert api.max_retries == 1
    for group in GROUPS:
        assert getattr(api, group).timeout == 15
        assert getattr(api, group).max_retries == 1


@pytest.mark.asyncio
async def test_async_timeout_is_sent_with_requests(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=URL, json=RESPONSE_OK)

    await AsyncApi(HOST, token=TOKEN, timeout=15).client.reset_ips(EMAIL)

    request = httpx_mock.get_request()
    assert request is not None
    assert request.extensions["timeout"]["read"] == 15


@pytest.mark.asyncio
async def test_async_facade_settings_reach_all_groups():
    api = AsyncApi(HOST, token=TOKEN, timeout=15)
    api.max_retries = 1

    assert api.timeout == 15
    assert api.max_retries == 1
    for group in GROUPS:
        assert getattr(api, group).timeout == 15
        assert getattr(api, group).max_retries == 1
