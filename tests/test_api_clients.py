import json
import os
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock

from py3xui import (
    Api,
    BulkAttachResult,
    BulkDetachResult,
    BulkResult,
    Client,
    ClientDetails,
    ClientEntry,
    ClientEntryTraffic,
    ClientExternalLink,
    ClientGroup,
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


def test_attach():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/{EMAIL_QUOTED}/attach", json=OK_RESPONSE)
        result = _api().client.attach(EMAIL, [7, 9])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"inboundIds": [7, 9]}
    assert result is None


def test_detach():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/{EMAIL_QUOTED}/detach", json=OK_RESPONSE)
        result = _api().client.detach(EMAIL, [5])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"inboundIds": [5]}
    assert result is None


def test_set_external_links():
    links = [
        ClientExternalLink(kind="link", value="vless://example", remark="DE", enable=True),
        ClientExternalLink(
            kind="subscription",
            value="https://provider.example/sub/abc",
            enable=False,
            expiry_time=1767225600000,
            name_prefix="[zjh] ",
        ),
    ]
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/{EMAIL_QUOTED}/externalLinks", json=OK_RESPONSE)
        result = _api().client.set_external_links(EMAIL, links)

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {
            "externalLinks": [
                {"kind": "link", "value": "vless://example", "remark": "DE", "enable": True},
                {
                    "kind": "subscription",
                    "value": "https://provider.example/sub/abc",
                    "enable": False,
                    "expiryTime": 1767225600000,
                    "namePrefix": "[zjh] ",
                },
            ]
        }
    assert result is None


def test_external_link_from_details_round_trip():
    details = _response("clients_get_by_tg_id")[ApiFields.OBJ][0]
    link = ClientExternalLink.model_validate(details["externalLinks"][0])

    assert link.remark == "backup"
    assert link.client_id == 42
    dumped = link.model_dump(by_alias=True, exclude_defaults=True)
    assert dumped["kind"] == "link"
    assert dumped["value"] == "vless://example"
    assert dumped["enable"] is True


def test_delete_orphans():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/delOrphans", json=_response("clients_del_orphans"))
        deleted = _api().client.delete_orphans()

        assert m.last_request.method == "POST"
    assert deleted == 0


def test_export_clients():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/export", json=_response("clients_export"))
        entries = _api().client.export_clients()

        assert m.last_request.method == "GET"
    assert len(entries) == 1
    assert isinstance(entries[0], ClientEntry)
    assert entries[0].client.email == "alice@example.com"
    assert entries[0].client.limit_hwid == 2
    assert entries[0].inbound_ids == [7, 9]
    assert isinstance(entries[0].traffic, ClientEntryTraffic)
    assert entries[0].traffic.down == 2097152
    assert entries[0].traffic.last_online == 1735680000000


def test_import_clients():
    entries = [
        ClientEntry(
            client=Client(email="alice@example.com", enable=False, limit_hwid=2),
            inbound_ids=[7],
            traffic=ClientEntryTraffic(up=10, down=20),
        ),
        ClientEntry(client=Client(email="bob@example.com", enable=True)),
    ]
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/import", json=_response("clients_import"))
        result = _api().client.import_clients(entries)

        assert m.last_request.method == "POST"
        body = m.last_request.json()
        assert set(body) == {"data"}
        assert json.loads(body["data"]) == [
            {
                "client": {"email": "alice@example.com", "enable": False, "limitHwid": 2},
                "inboundIds": [7],
                "traffic": {"up": 10, "down": 20},
            },
            {"client": {"email": "bob@example.com", "enable": True}},
        ]
    assert isinstance(result, BulkResult)
    assert result.count == 2
    assert result.skipped[0].email == "alice@example.com"
    assert result.skipped[0].reason == "email already in use: alice@example.com"


def test_export_import_round_trip():
    export = _response("clients_export")
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/export", json=export)
        m.post(f"{HOST}/panel/api/clients/import", json=_response("clients_import"))
        api = _api()
        api.client.import_clients(api.client.export_clients())

        sent = json.loads(m.last_request.json()["data"])
    # Zero values are left out: the panel reads an absent number as 0.
    expected = export[ApiFields.OBJ]
    del expected[0]["client"]["expiryTime"]
    del expected[0]["traffic"]["resetCount"]
    assert sent == expected


def test_bulk_adjust():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkAdjust", json=_response("clients_bulk_adjust"))
        result = _api().client.bulk_adjust(
            ["alice", "bob"], add_days=30, add_bytes=-5, flow="none", limit_hwid=0, ad_tag="none"
        )

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {
            "emails": ["alice", "bob"],
            "addDays": 30,
            "addBytes": -5,
            "flow": "none",
            "limitHwid": 0,
            "adTag": "none",
        }
    assert isinstance(result, BulkResult)
    assert result.count == 2
    assert result.skipped[0].email == "carol"
    assert result.skipped[0].reason == "unlimited expiry"


def test_bulk_adjust_leaves_out_unset_directives():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkAdjust", json=_response("clients_bulk_adjust"))
        _api().client.bulk_adjust(["alice"], add_days=1)

        assert m.last_request.json() == {"emails": ["alice"], "addDays": 1, "addBytes": 0}


def test_bulk_enable():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkEnable", json=_response("clients_bulk_enable"))
        result = _api().client.bulk_enable(["alice", "bob"])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"]}
    assert result.count == 2
    assert result.skipped[0].reason == "client not found"


def test_bulk_disable():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkDisable", json=_response("clients_bulk_disable"))
        result = _api().client.bulk_disable(["alice", "bob"])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"]}
    assert result.count == 2


def test_bulk_delete():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkDel", json=_response("clients_bulk_del"))
        result = _api().client.bulk_delete(["alice", "bob"], keep_traffic=True)

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"], "keepTraffic": True}
    assert result.count == 2
    assert result.skipped[0].email == "carol"


def test_bulk_add():
    entries = [
        ClientEntry(
            client=Client(email="alice@example.com", enable=True, limit_hwid=2),
            inbound_ids=[7],
        ),
        ClientEntry(client=Client(email="bob@example.com", enable=False), inbound_ids=[7, 9]),
    ]
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkCreate", json=_response("clients_bulk_create"))
        result = _api().client.bulk_add(entries)

        assert m.last_request.method == "POST"
        assert m.last_request.json() == [
            {
                "client": {"email": "alice@example.com", "enable": True, "limitHwid": 2},
                "inboundIds": [7],
            },
            {"client": {"email": "bob@example.com", "enable": False}, "inboundIds": [7, 9]},
        ]
    assert result.count == 2
    assert result.skipped[0].reason == "email already in use"


def test_bulk_attach():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkAttach", json=_response("clients_bulk_attach"))
        result = _api().client.bulk_attach(["alice", "bob"], [7, 9])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"], "inboundIds": [7, 9]}
    assert isinstance(result, BulkAttachResult)
    assert result.attached == ["alice", "bob"]
    assert result.skipped == ["bob"]
    assert result.errors == []


def test_bulk_attach_null_lists():
    response = {
        ApiFields.SUCCESS: True,
        ApiFields.OBJ: {"attached": None, "skipped": None, "errors": None},
    }
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkAttach", json=response)
        result = _api().client.bulk_attach([], [])

    assert result == BulkAttachResult()


def test_bulk_detach():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/bulkDetach", json=_response("clients_bulk_detach"))
        result = _api().client.bulk_detach(["alice", "bob"], [7, 9])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"], "inboundIds": [7, 9]}
    assert isinstance(result, BulkDetachResult)
    assert result.detached == ["alice", "bob"]
    assert result.skipped == []


def test_bulk_reset_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/bulkResetTraffic",
            json=_response("clients_bulk_reset_traffic"),
        )
        affected = _api().client.bulk_reset_stats(["alice", "bob"])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"]}
    assert affected == 2


def test_get_groups():
    with requests_mock.Mocker() as m:
        m.get(f"{HOST}/panel/api/clients/groups", json=_response("clients_groups"))
        groups = _api().client.get_groups()

        assert m.last_request.method == "GET"
    assert len(groups) == 2
    assert isinstance(groups[0], ClientGroup)
    assert groups[0].name == "customer-a"
    assert groups[0].client_count == 5
    assert groups[0].traffic_used == 3072
    assert groups[0].down == 2048
    assert groups[1].client_count == 0


def test_get_group_emails():
    with requests_mock.Mocker() as m:
        m.get(
            f"{HOST}/panel/api/clients/groups/customer%20a%2F1/emails",
            json=_response("clients_group_emails"),
        )
        emails = _api().client.get_group_emails("customer a/1")

        assert m.last_request.method == "GET"
        assert m.last_request.path == "/panel/api/clients/groups/customer%20a%2f1/emails"
    assert emails == ["alice", "bob", "carol"]


def test_add_group():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/groups/create", json=_response("clients_group_create"))
        result = _api().client.add_group("customer-a")

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"name": "customer-a"}
    assert result is None


def test_rename_group():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/groups/rename", json=_response("clients_group_rename"))
        affected = _api().client.rename_group("customer-a", "tier-1")

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"oldName": "customer-a", "newName": "tier-1"}
    assert affected == 5


def test_delete_group():
    with requests_mock.Mocker() as m:
        m.post(f"{HOST}/panel/api/clients/groups/delete", json=_response("clients_group_delete"))
        affected = _api().client.delete_group("customer-a")

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"name": "customer-a"}
    assert affected == 5


def test_reset_group_stats():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/groups/resetTraffic",
            json=_response("clients_group_reset_traffic"),
        )
        result = _api().client.reset_group_stats("customer-a")

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"name": "customer-a"}
    assert result is None


def test_bulk_add_to_group():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/groups/bulkAdd", json=_response("clients_group_bulk_add")
        )
        affected = _api().client.bulk_add_to_group("customer-a", ["alice", "bob"])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"], "group": "customer-a"}
    assert affected == 2


def test_bulk_remove_from_group():
    with requests_mock.Mocker() as m:
        m.post(
            f"{HOST}/panel/api/clients/groups/bulkRemove",
            json=_response("clients_group_bulk_remove"),
        )
        affected = _api().client.bulk_remove_from_group(["alice", "bob"])

        assert m.last_request.method == "POST"
        assert m.last_request.json() == {"emails": ["alice", "bob"]}
    assert affected == 2
