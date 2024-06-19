import os

import pytest

import py3xui.utils.env as env


def test_envs_success():
    os.environ["XUI_HOST"] = "http://localhost"
    os.environ["XUI_USERNAME"] = "admin"
    os.environ["XUI_PASSWORD"] = "admin"

    assert env.xui_host() == "http://localhost"
    assert env.xui_username() == "admin"
    assert env.xui_password() == "admin"


def test_envs_failed():
    os.environ["ABCDEF"] = "http://localhost"
    os.environ.pop("XUI_HOST", None)

    with pytest.raises(ValueError):
        env.xui_host()
