from urllib.parse import parse_qs

import pytest
import requests_mock
from pytest_httpx import HTTPXMock

from py3xui import Api, AsyncApi
from py3xui.api.api_base import ApiFields

HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
RESPONSE_OK = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}
FORM_DATA = {"enable": True, "remark": "test", "port": 443, "skipped": None}
FORM_EXPECTED = {"enable": ["true"], "remark": ["test"], "port": ["443"]}


def test_post_form_sends_form_fields():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/test", json=RESPONSE_OK)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        api.server._post_form(api.server._url("panel/api/test"), {}, FORM_DATA)

        request = m.last_request
        assert request.method == "POST"
        assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert parse_qs(request.text) == FORM_EXPECTED


def test_post_form_sends_multipart_with_files():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/test", json=RESPONSE_OK)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        api.server._post_form(
            api.server._url("panel/api/test"),
            {},
            {"keep": False},
            files={"file": ("backup.db", b"content")},
        )

        request = m.last_request
        assert request.headers["Content-Type"].startswith("multipart/form-data")
        assert b'name="keep"\r\n\r\nfalse' in request.body
        assert b'filename="backup.db"' in request.body


def test_post_form_requires_login():
    api = Api(HOST, USERNAME, PASSWORD)

    with pytest.raises(ValueError):
        api.server._post_form(api.server._url("panel/api/test"), {}, {})


def test_delete_sends_delete_request():
    with requests_mock.Mocker() as m:
        m.delete(f"{HOST}/panel/api/test/1", json=RESPONSE_OK)
        api = Api(HOST, USERNAME, PASSWORD)
        api.session = SESSION

        api.server._delete(api.server._url("panel/api/test/1"), {})

        assert m.last_request.method == "DELETE"


def test_delete_requires_login():
    api = Api(HOST, USERNAME, PASSWORD)

    with pytest.raises(ValueError):
        api.server._delete(api.server._url("panel/api/test/1"), {})


@pytest.mark.asyncio
async def test_async_post_form_sends_form_fields(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{HOST}/panel/api/test", json=RESPONSE_OK)
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    await api.server._post_form(api.server._url("panel/api/test"), {}, FORM_DATA)

    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert parse_qs(request.content.decode("utf-8")) == FORM_EXPECTED


@pytest.mark.asyncio
async def test_async_post_form_sends_multipart_with_files(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{HOST}/panel/api/test", json=RESPONSE_OK)
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    await api.server._post_form(
        api.server._url("panel/api/test"),
        {},
        {"keep": False},
        files={"file": ("backup.db", b"content")},
    )

    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["Content-Type"].startswith("multipart/form-data")
    assert b'name="keep"\r\n\r\nfalse' in request.content
    assert b'filename="backup.db"' in request.content


@pytest.mark.asyncio
async def test_async_post_form_requires_login():
    api = AsyncApi(HOST, USERNAME, PASSWORD)

    with pytest.raises(ValueError):
        await api.server._post_form(api.server._url("panel/api/test"), {}, {})


@pytest.mark.asyncio
async def test_async_delete_sends_delete_request(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="DELETE", url=f"{HOST}/panel/api/test/1", json=RESPONSE_OK)
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION

    await api.server._delete(api.server._url("panel/api/test/1"), {})

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "DELETE"


@pytest.mark.asyncio
async def test_async_delete_requires_login():
    api = AsyncApi(HOST, USERNAME, PASSWORD)

    with pytest.raises(ValueError):
        await api.server._delete(api.server._url("panel/api/test/1"), {})
