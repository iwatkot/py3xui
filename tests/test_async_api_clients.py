import json
import os

import httpx
import pytest
from pytest_httpx import HTTPXMock

from py3xui import (
    AsyncApi,
    BulkAttachResult,
    BulkDetachResult,
    BulkResult,
    Client,
    ClientDetails,
    ClientEntry,
    ClientEntryTraffic,
    ClientExternalLink,
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


def _api() -> AsyncApi:
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def _json_body(request: httpx.Request):
    return json.loads(request.content)


@pytest.mark.asyncio
async def test_get_list_paged(httpx_mock: HTTPXMock):
    params = {
        "page": "2",
        "pageSize": "50",
        "search": "alice",
        "filter": "online,depleted",
        "inbound": "3,5",
        "group": "staff",
        "sort": "expiryTime",
        "order": "descend",
        "expiryFrom": "1",
        "autoRenew": "off",
        "hasTgId": "yes",
    }
    httpx_mock.add_response(
        method="GET",
        url=httpx.URL(f"{HOST}/panel/api/clients/list/paged", params=params),
        json=_response("clients_list_paged"),
    )

    page = await _api().client.get_list_paged(
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

    assert isinstance(page, ClientPage)
    assert page.total == 2000
    assert page.filtered == 47
    assert page.summary.online_count == 1
    assert page.items[0].inbound_ids == [3, 5]
    assert page.items[1].traffic is not None
    assert page.items[1].traffic.up == 1048576


@pytest.mark.asyncio
async def test_get_list_paged_defaults(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/list/paged?page=1&pageSize=25",
        json=_response("clients_list_paged"),
    )

    page = await _api().client.get_list_paged()

    assert page.groups == ["staff", "trial"]


@pytest.mark.asyncio
async def test_get_details_by_sub_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/subId/{SUB_ID}",
        json=_response("clients_get_by_sub_id"),
    )

    details = await _api().client.get_details_by_sub_id(SUB_ID)

    assert len(details) == 2
    assert all(isinstance(item, ClientDetails) for item in details)
    assert details[0].client.email == EMAIL
    assert details[1].client.id == 43
    assert details[1].external_links == []


@pytest.mark.asyncio
async def test_get_details_by_sub_id_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/subId/{SUB_ID}",
        json={ApiFields.SUCCESS: False, ApiFields.MSG: "record not found", ApiFields.OBJ: None},
    )

    with pytest.raises(ValueError, match="record not found"):
        await _api().client.get_details_by_sub_id(SUB_ID)


@pytest.mark.asyncio
async def test_get_details_by_tg_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/get/tgId/123456789",
        json=_response("clients_get_by_tg_id"),
    )

    details = await _api().client.get_details_by_tg_id(123456789)

    assert len(details) == 1
    assert details[0].client.tg_id == 123456789


@pytest.mark.asyncio
async def test_get_renewal_preview(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/renewalPreview",
        json=_response("clients_renewal_preview"),
    )

    preview = await _api().client.get_renewal_preview(1893456000000, reset_day=1, reset_max=3)

    assert _json_body(httpx_mock.get_request()) == {
        "expiryTime": 1893456000000,
        "reset": 0,
        "resetDay": 1,
        "resetWeekday": 0,
        "resetMax": 3,
        "resetCount": 0,
    }
    assert isinstance(preview, ClientRenewalPreview)
    assert preview.next_expiry == "2030-02-01T00:00:00Z"
    assert preview.can_renew is True


@pytest.mark.asyncio
async def test_get_traffic(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/traffic/{EMAIL_QUOTED}",
        json=_response("clients_traffic"),
    )

    traffic = await _api().client.get_traffic(EMAIL)

    assert isinstance(traffic, ClientTraffic)
    assert traffic.id == 14825
    assert traffic.sub_id == "i7tvdpeffi0hvvf1"
    assert traffic.last_online == 1735680000000


@pytest.mark.asyncio
async def test_get_traffic_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/traffic/{EMAIL_QUOTED}",
        json=OK_RESPONSE,
    )

    assert await _api().client.get_traffic(EMAIL) is None


@pytest.mark.asyncio
async def test_get_sub_links(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/subLinks/{SUB_ID}",
        json=_response("clients_sub_links"),
    )

    links = await _api().client.get_sub_links(SUB_ID)

    assert links == _response("clients_sub_links")[ApiFields.OBJ]


@pytest.mark.asyncio
async def test_get_links(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{HOST}/panel/api/clients/links/{EMAIL_QUOTED}",
        json=_response("clients_links"),
    )

    links = await _api().client.get_links(EMAIL)

    assert links == ["vless://uuid@host:443?...#user1"]


@pytest.mark.asyncio
async def test_get_happ_link(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/happLink/42",
        json=_response("clients_happ_link"),
    )

    link = await _api().client.get_happ_link(42)

    assert link == "happ://crypt5/example"


@pytest.mark.asyncio
async def test_attach(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/clients/{EMAIL_QUOTED}/attach", json=OK_RESPONSE
    )

    result = await _api().client.attach(EMAIL, [7, 9])

    assert _json_body(httpx_mock.get_request()) == {"inboundIds": [7, 9]}
    assert result is None


@pytest.mark.asyncio
async def test_detach(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/clients/{EMAIL_QUOTED}/detach", json=OK_RESPONSE
    )

    result = await _api().client.detach(EMAIL, [5])

    assert _json_body(httpx_mock.get_request()) == {"inboundIds": [5]}
    assert result is None


@pytest.mark.asyncio
async def test_set_external_links(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/{EMAIL_QUOTED}/externalLinks",
        json=OK_RESPONSE,
    )
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

    result = await _api().client.set_external_links(EMAIL, links)

    assert _json_body(httpx_mock.get_request()) == {
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


@pytest.mark.asyncio
async def test_delete_orphans(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/delOrphans",
        json=_response("clients_del_orphans"),
    )

    assert await _api().client.delete_orphans() == 0


@pytest.mark.asyncio
async def test_export_clients(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET", url=f"{HOST}/panel/api/clients/export", json=_response("clients_export")
    )

    entries = await _api().client.export_clients()

    assert len(entries) == 1
    assert isinstance(entries[0], ClientEntry)
    assert entries[0].client.limit_hwid == 2
    assert entries[0].inbound_ids == [7, 9]
    assert isinstance(entries[0].traffic, ClientEntryTraffic)
    assert entries[0].traffic.down == 2097152


@pytest.mark.asyncio
async def test_import_clients(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST", url=f"{HOST}/panel/api/clients/import", json=_response("clients_import")
    )
    entries = [
        ClientEntry(
            client=Client(email="alice@example.com", enable=False, limit_hwid=2),
            inbound_ids=[7],
            traffic=ClientEntryTraffic(up=10, down=20),
        ),
        ClientEntry(client=Client(email="bob@example.com", enable=True)),
    ]

    result = await _api().client.import_clients(entries)

    body = _json_body(httpx_mock.get_request())
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


@pytest.mark.asyncio
async def test_bulk_adjust(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkAdjust",
        json=_response("clients_bulk_adjust"),
    )

    result = await _api().client.bulk_adjust(
        ["alice", "bob"], add_days=30, add_bytes=-5, flow="none", limit_hwid=0, ad_tag="none"
    )

    assert _json_body(httpx_mock.get_request()) == {
        "emails": ["alice", "bob"],
        "addDays": 30,
        "addBytes": -5,
        "flow": "none",
        "limitHwid": 0,
        "adTag": "none",
    }
    assert isinstance(result, BulkResult)
    assert result.count == 2
    assert result.skipped[0].reason == "unlimited expiry"


@pytest.mark.asyncio
async def test_bulk_adjust_leaves_out_unset_directives(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkAdjust",
        json=_response("clients_bulk_adjust"),
    )

    await _api().client.bulk_adjust(["alice"], add_days=1)

    assert _json_body(httpx_mock.get_request()) == {
        "emails": ["alice"],
        "addDays": 1,
        "addBytes": 0,
    }


@pytest.mark.asyncio
async def test_bulk_enable(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkEnable",
        json=_response("clients_bulk_enable"),
    )

    result = await _api().client.bulk_enable(["alice", "bob"])

    assert _json_body(httpx_mock.get_request()) == {"emails": ["alice", "bob"]}
    assert result.count == 2


@pytest.mark.asyncio
async def test_bulk_disable(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkDisable",
        json=_response("clients_bulk_disable"),
    )

    result = await _api().client.bulk_disable(["alice", "bob"])

    assert _json_body(httpx_mock.get_request()) == {"emails": ["alice", "bob"]}
    assert result.count == 2


@pytest.mark.asyncio
async def test_bulk_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkDel",
        json=_response("clients_bulk_del"),
    )

    result = await _api().client.bulk_delete(["alice", "bob"], keep_traffic=True)

    assert _json_body(httpx_mock.get_request()) == {
        "emails": ["alice", "bob"],
        "keepTraffic": True,
    }
    assert result.count == 2


@pytest.mark.asyncio
async def test_bulk_add(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkCreate",
        json=_response("clients_bulk_create"),
    )
    entries = [
        ClientEntry(
            client=Client(email="alice@example.com", enable=True, limit_hwid=2),
            inbound_ids=[7],
        ),
        ClientEntry(client=Client(email="bob@example.com", enable=False), inbound_ids=[7, 9]),
    ]

    result = await _api().client.bulk_add(entries)

    assert _json_body(httpx_mock.get_request()) == [
        {
            "client": {"email": "alice@example.com", "enable": True, "limitHwid": 2},
            "inboundIds": [7],
        },
        {"client": {"email": "bob@example.com", "enable": False}, "inboundIds": [7, 9]},
    ]
    assert result.count == 2


@pytest.mark.asyncio
async def test_bulk_attach(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkAttach",
        json=_response("clients_bulk_attach"),
    )

    result = await _api().client.bulk_attach(["alice", "bob"], [7, 9])

    assert _json_body(httpx_mock.get_request()) == {
        "emails": ["alice", "bob"],
        "inboundIds": [7, 9],
    }
    assert isinstance(result, BulkAttachResult)
    assert result.attached == ["alice", "bob"]
    assert result.skipped == ["bob"]


@pytest.mark.asyncio
async def test_bulk_detach(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkDetach",
        json=_response("clients_bulk_detach"),
    )

    result = await _api().client.bulk_detach(["alice", "bob"], [7, 9])

    assert _json_body(httpx_mock.get_request()) == {
        "emails": ["alice", "bob"],
        "inboundIds": [7, 9],
    }
    assert isinstance(result, BulkDetachResult)
    assert result.detached == ["alice", "bob"]


@pytest.mark.asyncio
async def test_bulk_reset_stats(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{HOST}/panel/api/clients/bulkResetTraffic",
        json=_response("clients_bulk_reset_traffic"),
    )

    affected = await _api().client.bulk_reset_stats(["alice", "bob"])

    assert _json_body(httpx_mock.get_request()) == {"emails": ["alice", "bob"]}
    assert affected == 2
