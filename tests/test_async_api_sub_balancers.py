import json
import os
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from py3xui import AsyncApi, SubBalancer
from py3xui.async_api import AsyncSubBalancerApi

HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "responses")
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


def load_response(name: str) -> dict:
    with open(os.path.join(RESPONSES_DIR, f"{name}.json"), encoding="utf-8") as file:
        return json.load(file)


def make_api() -> AsyncApi:
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def last_form(httpx_mock: HTTPXMock) -> dict[str, list[str]]:
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert request.headers["Content-Type"] == FORM_CONTENT_TYPE
    return parse_qs(request.content.decode())


@pytest.mark.asyncio
async def test_get_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/sub-balancers",
        json=load_response("sub_balancers_list"),
    )

    balancers = await make_api().sub_balancer.get_list()

    assert [balancer.id for balancer in balancers] == [1, 2]
    first = balancers[0]
    assert isinstance(first, SubBalancer)
    assert first.remark == "auto-fastest"
    assert first.strategy == "leastLoad"
    assert first.inbound_ids == [1, 3]
    assert first.member_weights == {3: 0.5}
    assert first.sort_order == 2
    assert first.enabled is False
    assert first.created_at == 1710000000000
    assert first.updated_at == 1710000000001
    assert balancers[1].member_weights == {}


@pytest.mark.asyncio
async def test_get_list_null_obj(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/sub-balancers",
        json={"success": True, "msg": "", "obj": None},
    )

    assert await make_api().sub_balancer.get_list() == []


@pytest.mark.asyncio
async def test_add(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/sub-balancers",
        json=load_response("sub_balancers_item"),
    )

    created = await make_api().sub_balancer.add(
        SubBalancer(remark="auto-fastest", inbound_ids=[1, 3])
    )

    assert last_form(httpx_mock) == {
        "remark": ["auto-fastest"],
        "strategy": ["random"],
        "inboundIds": ["1", "3"],
        "sortOrder": ["1"],
    }
    assert created.id == 1
    assert created.enabled is True


@pytest.mark.asyncio
async def test_add_disabled_with_weights(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/sub-balancers",
        json=load_response("sub_balancers_item"),
    )

    await make_api().sub_balancer.add(
        SubBalancer(
            remark="auto-fastest",
            strategy="leastLoad",
            inbound_ids=[1, 3],
            member_weights={3: 0.5},
            sort_order=2,
            enabled=False,
        )
    )

    form = last_form(httpx_mock)
    assert form["strategy"] == ["leastLoad"]
    assert form["sortOrder"] == ["2"]
    assert form["enabled"] == ["false"]
    assert json.loads(form["memberWeights"][0]) == {"3": 0.5}


@pytest.mark.asyncio
async def test_update_keeps_stored_enabled_when_not_set(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/sub-balancers/7",
        json=load_response("sub_balancers_item"),
    )

    updated = await make_api().sub_balancer.update(7, SubBalancer(remark="new", inbound_ids=[2]))

    assert last_form(httpx_mock) == {
        "remark": ["new"],
        "strategy": ["random"],
        "inboundIds": ["2"],
        "sortOrder": ["1"],
    }
    assert updated.id == 1


@pytest.mark.asyncio
async def test_update_explicit_enabled_true(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/sub-balancers/7",
        json=load_response("sub_balancers_item"),
    )

    await make_api().sub_balancer.update(
        7, SubBalancer(remark="new", inbound_ids=[2], enabled=True)
    )

    assert last_form(httpx_mock)["enabled"] == ["true"]


@pytest.mark.asyncio
async def test_update_round_trip_keeps_all_fields(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/sub-balancers/1",
        json=load_response("sub_balancers_item"),
    )
    balancer = SubBalancer.model_validate(load_response("sub_balancers_list")["obj"][0])
    balancer.remark = "renamed"

    await make_api().sub_balancer.update(balancer.id, balancer)

    form = last_form(httpx_mock)
    assert form["remark"] == ["renamed"]
    assert form["strategy"] == ["leastLoad"]
    assert form["inboundIds"] == ["1", "3"]
    assert form["sortOrder"] == ["2"]
    assert form["enabled"] == ["false"]
    assert json.loads(form["memberWeights"][0]) == {"3": 0.5}


@pytest.mark.asyncio
async def test_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/sub-balancers/7/del",
        json=load_response("sub_balancers_delete"),
    )

    assert await make_api().sub_balancer.delete(7) is None

    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"
    assert not request.content


def test_facade_propagates_auth():
    api = AsyncApi(HOST, USERNAME, PASSWORD)

    assert isinstance(api.sub_balancer, AsyncSubBalancerApi)

    api.session = SESSION
    api.csrf_token = "csrf"
    api.cookie_name = "cookie"

    assert api.sub_balancer.session == SESSION
    assert api.sub_balancer.csrf_token == "csrf"
    assert api.sub_balancer.cookie_name == "cookie"
