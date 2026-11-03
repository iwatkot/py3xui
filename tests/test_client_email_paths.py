import pytest
import requests_mock
from pytest_httpx import HTTPXMock

from py3xui import Api, AsyncApi
from py3xui.api.api_base import ApiFields

HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
EMAIL = "alice+vpn@example.com"
QUOTED = "alice%2Bvpn%40example.com"
RESPONSE_OK = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}
NAME_WITHOUT_AT = "awg-1-lbg-7"
LIST_RESPONSE = {
    ApiFields.SUCCESS: True,
    ApiFields.MSG: "",
    ApiFields.OBJ: [{"id": 1, "uuid": "6f0f4c4e", "email": NAME_WITHOUT_AT}],
}


def _api():
    api = Api(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def _async_api():
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def test_emails_are_quoted_in_paths():
    url = f"{HOST}/panel/api/clients"
    with requests_mock.Mocker() as m:
        m.get(f"{url}/get/{QUOTED}", json=RESPONSE_OK)
        for route in ("ips", "clearIps", "resetTraffic", "del"):
            m.post(f"{url}/{route}/{QUOTED}", json=RESPONSE_OK)
        api = _api()

        api.client.get_by_email(EMAIL)
        api.client.get_ips(EMAIL)
        api.client.reset_ips(EMAIL)
        api.client.reset_stats(1, EMAIL)
        api.client.delete(1, EMAIL)

        assert m.call_count == 5


def test_delete_accepts_a_name_without_at():
    url = f"{HOST}/panel/api/clients"
    with requests_mock.Mocker() as m:
        m.get(f"{url}/list", json=LIST_RESPONSE)
        m.post(f"{url}/del/{NAME_WITHOUT_AT}", json=RESPONSE_OK)

        _api().client.delete(1, NAME_WITHOUT_AT)

        assert m.last_request.path.endswith(f"/del/{NAME_WITHOUT_AT}")


def test_delete_unknown_name_raises():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/list", json=LIST_RESPONSE)

        with pytest.raises(ValueError, match="Cannot resolve client email"):
            _api().client.delete(1, "unknown")


@pytest.mark.asyncio
async def test_async_emails_are_quoted_in_paths(httpx_mock: HTTPXMock):
    url = f"{HOST}/panel/api/clients"
    httpx_mock.add_response(method="GET", url=f"{url}/get/{QUOTED}", json=RESPONSE_OK)
    for route in ("ips", "clearIps", "resetTraffic", "del"):
        httpx_mock.add_response(method="POST", url=f"{url}/{route}/{QUOTED}", json=RESPONSE_OK)
    api = _async_api()

    await api.client.get_by_email(EMAIL)
    await api.client.get_ips(EMAIL)
    await api.client.reset_ips(EMAIL)
    await api.client.reset_stats(1, EMAIL)
    await api.client.delete(1, EMAIL)

    assert len(httpx_mock.get_requests()) == 5


@pytest.mark.asyncio
async def test_async_delete_accepts_a_name_without_at(httpx_mock: HTTPXMock):
    url = f"{HOST}/panel/api/clients"
    httpx_mock.add_response(method="GET", url=f"{url}/list", json=LIST_RESPONSE)
    httpx_mock.add_response(method="POST", url=f"{url}/del/{NAME_WITHOUT_AT}", json=RESPONSE_OK)

    await _async_api().client.delete(1, NAME_WITHOUT_AT)

    assert httpx_mock.get_requests(method="POST")[-1].url.path.endswith(NAME_WITHOUT_AT)


@pytest.mark.asyncio
async def test_async_delete_unknown_name_raises(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{HOST}/panel/api/clients/list", json=LIST_RESPONSE)

    with pytest.raises(ValueError, match="Cannot resolve client email"):
        await _async_api().client.delete(1, "unknown")
