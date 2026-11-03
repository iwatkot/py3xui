import json
import os
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock

from py3xui import (
    Api,
    ClientDetails,
    ClientPage,
    ClientRenewalPreview,
    ClientTraffic,
)
from py3xui.api.api_base import ApiFields

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"

EMAIL = "alice+wg@example.com"
EMAIL_QUOTED = "alice%2Bwg%40example.com"
SUB_ID = "fake-sub-id"
OK_RESPONSE = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}


def _response(name: str) -> dict:
    with open(os.path.join(RESPONSES_DIR, f"{name}.json"), encoding="utf-8") as file:
        return json.load(file)


def _api() -> Api:
    api = Api(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def _query(request) -> dict[str, list[str]]:
    return parse_qs(urlparse(request.url).query)


def test_get_list_paged():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/list/paged", json=_response("clients_list_paged"))
        page = _api().client.get_list_paged(
            page=2,
            page_size=50,
            search="alice",
            statuses=["online", "depleted"],
            inbound_ids=[3, 5],
            groups=["staff"],
            sort="expiryTime",
            order="descend",
            expiry_from=1,
            auto_renew=False,
            has_tg_id=True,
        )

        assert m.last_request.method == "GET"
        assert _query(m.last_request) == {
            "page": ["2"],
            "pageSize": ["50"],
            "search": ["alice"],
            "filter": ["online,depleted"],
            "inbound": ["3,5"],
            "group": ["staff"],
            "sort": ["expiryTime"],
            "order": ["descend"],
            "expiryFrom": ["1"],
            "autoRenew": ["off"],
            "hasTgId": ["yes"],
        }
    assert isinstance(page, ClientPage)
    assert page.total == 2000
    assert page.filtered == 47
    assert page.page_size == 25
    assert page.groups == ["staff", "trial"]
    assert page.summary.online_count == 1
    assert page.summary.deactive == ["bob@example.com"]
    assert page.items[0].email == "alice@example.com"
    assert page.items[0].inbound_ids == [3, 5]
    assert page.items[0].traffic is None
    assert page.items[1].traffic is not None
    assert page.items[1].traffic.up == 1048576


def test_get_list_paged_defaults():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/list/paged", json=_response("clients_list_paged"))
        _api().client.get_list_paged()

        assert _query(m.last_request) == {"page": ["1"], "pageSize": ["25"]}


def test_get_details_by_sub_id():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/get/subId/{SUB_ID}",
            json=_response("clients_get_by_sub_id"),
        )
        details = _api().client.get_details_by_sub_id(SUB_ID)

        assert m.last_request.method == "GET"
    assert len(details) == 2
    assert all(isinstance(item, ClientDetails) for item in details)
    assert details[0].client.email == EMAIL
    assert details[1].client.id == 43
    assert details[1].inbound_ids == [7]
    assert details[1].external_links == []


def test_get_details_by_sub_id_not_found():
    response = {ApiFields.SUCCESS: False, ApiFields.MSG: "record not found", ApiFields.OBJ: None}
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/get/subId/{SUB_ID}", json=response)

        with pytest.raises(ValueError, match="record not found"):
            _api().client.get_details_by_sub_id(SUB_ID)


def test_get_details_by_tg_id():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/get/tgId/123456789",
            json=_response("clients_get_by_tg_id"),
        )
        details = _api().client.get_details_by_tg_id(123456789)

        assert m.last_request.method == "GET"
    assert len(details) == 1
    assert details[0].client.tg_id == 123456789


def test_get_renewal_preview():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/renewalPreview",
            json=_response("clients_renewal_preview"),
        )
        preview = _api().client.get_renewal_preview(1893456000000, reset_day=1, reset_max=3)

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {
            "expiryTime": 1893456000000,
            "reset": 0,
            "resetDay": 1,
            "resetWeekday": 0,
            "resetMax": 3,
            "resetCount": 0,
        }
    assert isinstance(preview, ClientRenewalPreview)
    assert preview.time_zone == "UTC"
    assert preview.next_expiry == "2030-02-01T00:00:00Z"
    assert preview.suggested_expiry_time == 1893456000000
    assert preview.renewals == 1
    assert preview.can_renew is True


def test_get_traffic():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/traffic/{EMAIL_QUOTED}",
            json=_response("clients_traffic"),
        )
        traffic = _api().client.get_traffic(EMAIL)

        assert m.last_request.method == "GET"
    assert isinstance(traffic, ClientTraffic)
    assert traffic.id == 14825
    assert traffic.inbound_id == 1
    assert traffic.sub_id == "i7tvdpeffi0hvvf1"
    assert traffic.down == 2097152
    assert traffic.last_online == 1735680000000


def test_get_traffic_not_found():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/traffic/{EMAIL_QUOTED}", json=OK_RESPONSE)

        assert _api().client.get_traffic(EMAIL) is None


def test_get_sub_links():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/subLinks/{SUB_ID}",
            json=_response("clients_sub_links"),
        )
        links = _api().client.get_sub_links(SUB_ID)

        assert m.last_request.method == "GET"
    assert links == _response("clients_sub_links")[ApiFields.OBJ]


def test_get_links():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/links/{EMAIL_QUOTED}", json=_response("clients_links"))
        links = _api().client.get_links(EMAIL)

        assert m.last_request.method == "GET"
    assert links == ["vless://uuid@host:443?...#user1"]


def test_get_happ_link():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/happLink/42", json=_response("clients_happ_link"))
        link = _api().client.get_happ_link(42)

        assert m.last_request.method == "POST"
    assert link == "happ://crypt5/example"
