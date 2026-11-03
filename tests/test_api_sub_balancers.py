import json
import os
from urllib.parse import parse_qs

import requests_mock

from py3xui import Api, SubBalancer
from py3xui.api import SubBalancerApi

HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
RESPONSES_DIR = os.path.join(os.path.dirname(__file__), "responses")
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"


def load_response(name: str) -> dict:
    with open(os.path.join(RESPONSES_DIR, f"{name}.json"), encoding="utf-8") as file:
        return json.load(file)


def make_api() -> Api:
    api = Api(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def test_get_list():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/sub-balancers", json=load_response("sub_balancers_list"))

        balancers = make_api().sub_balancer.get_list()

        assert m.last_request.method == "GET"
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


def test_get_list_null_obj():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/sub-balancers", json={"success": True, "msg": "", "obj": None})

        assert make_api().sub_balancer.get_list() == []


def test_add():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/sub-balancers", json=load_response("sub_balancers_item"))

        created = make_api().sub_balancer.add(
            SubBalancer(remark="auto-fastest", inbound_ids=[1, 3])
        )

        request = m.last_request
        assert request.method == "POST"
        assert request.headers["Content-Type"] == FORM_CONTENT_TYPE
        assert parse_qs(request.text) == {
            "remark": ["auto-fastest"],
            "strategy": ["random"],
            "inboundIds": ["1", "3"],
            "sortOrder": ["1"],
        }
        assert created.id == 1
        assert created.enabled is True


def test_add_disabled_with_weights():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/sub-balancers", json=load_response("sub_balancers_item"))

        make_api().sub_balancer.add(
            SubBalancer(
                remark="auto-fastest",
                strategy="leastLoad",
                inbound_ids=[1, 3],
                member_weights={3: 0.5},
                sort_order=2,
                enabled=False,
            )
        )

        form = parse_qs(m.last_request.text)
        assert form["strategy"] == ["leastLoad"]
        assert form["sortOrder"] == ["2"]
        assert form["enabled"] == ["false"]
        assert json.loads(form["memberWeights"][0]) == {"3": 0.5}


def test_update_keeps_stored_enabled_when_not_set():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/sub-balancers/7", json=load_response("sub_balancers_item"))

        updated = make_api().sub_balancer.update(7, SubBalancer(remark="new", inbound_ids=[2]))

        request = m.last_request
        assert request.method == "POST"
        assert request.headers["Content-Type"] == FORM_CONTENT_TYPE
        assert parse_qs(request.text) == {
            "remark": ["new"],
            "strategy": ["random"],
            "inboundIds": ["2"],
            "sortOrder": ["1"],
        }
        assert updated.id == 1


def test_update_explicit_enabled_true():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/sub-balancers/7", json=load_response("sub_balancers_item"))

        make_api().sub_balancer.update(
            7, SubBalancer(remark="new", inbound_ids=[2], enabled=True)
        )

        assert parse_qs(m.last_request.text)["enabled"] == ["true"]


def test_update_round_trip_keeps_all_fields():
    balancer = SubBalancer.model_validate(load_response("sub_balancers_list")["obj"][0])
    balancer.remark = "renamed"

    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/sub-balancers/1", json=load_response("sub_balancers_item"))

        make_api().sub_balancer.update(balancer.id, balancer)

        form = parse_qs(m.last_request.text)
        assert form["remark"] == ["renamed"]
        assert form["strategy"] == ["leastLoad"]
        assert form["inboundIds"] == ["1", "3"]
        assert form["sortOrder"] == ["2"]
        assert form["enabled"] == ["false"]
        assert json.loads(form["memberWeights"][0]) == {"3": 0.5}


def test_delete():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/sub-balancers/7/del", json=load_response("sub_balancers_delete"))

        assert make_api().sub_balancer.delete(7) is None

        request = m.last_request
        assert request.method == "POST"
        assert not request.text


def test_model_keeps_unknown_fields():
    data = {"remark": "a", "inboundIds": [1], "futureField": "x"}

    balancer = SubBalancer.model_validate(data)

    assert balancer.model_dump(by_alias=True)["futureField"] == "x"


def test_facade_propagates_auth():
    api = Api(HOST, USERNAME, PASSWORD)

    assert isinstance(api.sub_balancer, SubBalancerApi)

    api.session = SESSION
    api.csrf_token = "csrf"
    api.cookie_name = "cookie"

    assert api.sub_balancer.session == SESSION
    assert api.sub_balancer.csrf_token == "csrf"
    assert api.sub_balancer.cookie_name == "cookie"
