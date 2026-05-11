import os

import pytest

import py3xui.utils.env as env


def test_envs_success():
    os.environ["XUI_HOST"] = "http://localhost"
    os.environ["XUI_USERNAME"] = "admin"
    os.environ["XUI_PASSWORD"] = "admin"
    os.environ["XUI_TOKEN"] = "token"

    assert env.xui_host() == "http://localhost"
    assert env.xui_username() == "admin"
    assert env.xui_password() == "admin"
    assert env.xui_token() == "token"


def test_envs_failed():
    os.environ["ABCDEF"] = "http://localhost"
    os.environ.pop("XUI_HOST", None)
    os.environ.pop("XUI_USERNAME", None)
    os.environ.pop("XUI_PASSWORD", None)
    os.environ.pop("XUI_TOKEN", None)

    with pytest.raises(ValueError):
        env.xui_host()

    assert env.xui_token() is None
    assert env.xui_username() is None
    assert env.xui_password() is None

    with pytest.raises(ValueError):
        env.xui_username(raise_if_not_found=True)

    with pytest.raises(ValueError):
        env.xui_password(raise_if_not_found=True)
