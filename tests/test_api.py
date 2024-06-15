import pytest
import requests_mock
from requests.exceptions import ConnectionError

from py3xui import Api
from py3xui.api.api import ApiFields


def test_init():
    host = "http://localhost"
    username = "admin"
    password = "admin"
    api = Api(host, username, password, skip_login=True)
    assert api.host == host, f"Expected {host}, got {api.host}"
    assert api.username == username, f"Expected {username}, got {api.username}"
    assert api.password == password, f"Expected {password}, got {api.password}"
    assert api.max_retries == 3, f"Expected 3, got {api.max_retries}"
    assert api.session is None, f"Expected None, got {api.session}"


def test_login_success():
    session = "abc123"
    host = "http://localhost"
    with requests_mock.Mocker() as m:
        m.post(f"{host}/login", json={ApiFields.SUCCESS: True}, cookies={"session": session})
        api = Api(host, "username", "password", skip_login=True)
        api.login()
        assert api.session == session, f"Expected {session}, got {api.session}"


def test_login_failed():
    host = "http://localhost"
    with requests_mock.Mocker() as m:
        m.post(f"{host}/login", json={ApiFields.SUCCESS: True})
        api = Api(host, "username", "password", skip_login=True)
        with pytest.raises(ValueError):
            api.login()

    with pytest.raises(ConnectionError):
        api = Api(host, "username", "password")
