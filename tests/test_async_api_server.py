import json
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from py3xui import AsyncApi
from py3xui.api.api_base import ApiFields

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
SERVER_URL = f"{HOST}/panel/api/server"
RESPONSE_OK = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}
RESPONSE_FAILED = {ApiFields.SUCCESS: False, ApiFields.MSG: "failed", ApiFields.OBJ: None}


def make_api() -> AsyncApi:
    api = AsyncApi(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def load_response(name: str) -> dict:
    with open(f"{RESPONSES_DIR}/server_{name}.json", encoding="utf-8") as file:
        return json.load(file)


def form_fields(request) -> dict:
    return parse_qs(request.content.decode("utf-8"), keep_blank_values=True)


def json_body(request):
    return json.loads(request.content)


def raw_body(request) -> bytes:
    return request.content


@pytest.mark.asyncio
async def test_get_fail2ban_status(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/fail2banStatus",
        json=load_response("fail2ban_status"),
    )
    status = await make_api().server.get_fail2ban_status()

    assert status.enabled is True
    assert status.installed is True
    assert status.usable is True
    assert status.windows is False


@pytest.mark.asyncio
async def test_get_cpu_history(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/cpuHistory/60",
        json=load_response("cpu_history"),
    )
    points = await make_api().server.get_cpu_history(60)

    assert [(point.t, point.cpu) for point in points] == [(1700000000, 12.5), (1700000060, 13.1)]


@pytest.mark.asyncio
async def test_get_history(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/history/mem/30",
        json=load_response("history"),
    )
    points = await make_api().server.get_history("mem", 30)

    assert [(point.t, point.v) for point in points] == [(1700000000, 12.5), (1700000002, 13.1)]


@pytest.mark.asyncio
async def test_get_history_empty(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{SERVER_URL}/history/mem/30", json=RESPONSE_OK)
    assert await make_api().server.get_history("mem", 30) == []


@pytest.mark.asyncio
async def test_get_history_failed(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{SERVER_URL}/history/nope/30", json=RESPONSE_FAILED)
    with pytest.raises(ValueError):
        await make_api().server.get_history("nope", 30)


@pytest.mark.asyncio
async def test_get_xray_metrics_state(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/xrayMetricsState",
        json=load_response("xray_metrics_state"),
    )
    state = await make_api().server.get_xray_metrics_state()

    assert state.enabled is False
    assert state.listen == ""
    assert state.reason == "metrics block is not configured"


@pytest.mark.asyncio
async def test_get_xray_metrics_history(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/xrayMetricsHistory/xrAlloc/60",
        json=load_response("xray_metrics_history"),
    )
    points = await make_api().server.get_xray_metrics_history("xrAlloc", 60)

    assert [(point.t, point.v) for point in points] == [(1700000000, 1048576.0)]


@pytest.mark.asyncio
async def test_get_xray_observatory(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/xrayObservatory",
        json=load_response("xray_observatory"),
    )
    snapshots = await make_api().server.get_xray_observatory()

    assert len(snapshots) == 1
    assert snapshots[0].tag == "proxy"
    assert snapshots[0].alive is True
    assert snapshots[0].delay == 120
    assert snapshots[0].last_seen_time == 1700000000
    assert snapshots[0].last_try_time == 1700000030
    assert snapshots[0].updated_at == 1700000031


@pytest.mark.asyncio
async def test_get_xray_observatory_history(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/xrayObservatoryHistory/out%2Fbound/60",
        json=load_response("xray_observatory_history"),
    )
    points = await make_api().server.get_xray_observatory_history("out/bound", 60)

    assert [(point.t, point.v) for point in points] == [(1700000000, 120.0)]


@pytest.mark.asyncio
async def test_get_panel_update_info(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getPanelUpdateInfo",
        json=load_response("panel_update_info"),
    )
    info = await make_api().server.get_panel_update_info()

    assert info.channel == "dev"
    assert info.current_version == "3.11.0-dev"
    assert info.latest_version == "dev+abc1234"
    assert info.current_commit == "def5678"
    assert info.latest_commit == "abc1234"
    assert info.update_available is True


@pytest.mark.asyncio
async def test_get_panel_update_info_failed(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getPanelUpdateInfo",
        json={ApiFields.SUCCESS: False},
    )
    with pytest.raises(ValueError):
        await make_api().server.get_panel_update_info()


@pytest.mark.asyncio
async def test_get_update_status(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getUpdateStatus",
        json=load_response("update_status"),
    )
    status = await make_api().server.get_update_status()

    assert status.run_id == "1735689600123456789"
    assert status.state == "success"
    assert status.exit_code == 0
    assert status.finished_at == 1735689612


@pytest.mark.asyncio
async def test_update_panel(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/updatePanel",
        json=load_response("update_panel"),
    )
    run_id = await make_api().server.update_panel()
    assert form_fields(httpx_mock.get_request()) == {}

    assert run_id == "1735689600123456789"


@pytest.mark.asyncio
async def test_update_panel_dev_channel(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/updatePanel",
        json=load_response("update_panel"),
    )
    await make_api().server.update_panel(dev=True)
    assert form_fields(httpx_mock.get_request()) == {"dev": ["true"]}


@pytest.mark.asyncio
async def test_set_update_channel(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/setUpdateChannel", json=RESPONSE_OK)
    await make_api().server.set_update_channel(False)
    assert form_fields(httpx_mock.get_request()) == {"dev": ["false"]}


@pytest.mark.asyncio
async def test_stop_xray(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/stopXrayService", json=RESPONSE_OK)
    await make_api().server.stop_xray()
    assert httpx_mock.get_request().method == "POST"


@pytest.mark.asyncio
async def test_stop_xray_failed(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/stopXrayService",
        json=RESPONSE_FAILED,
    )
    with pytest.raises(ValueError):
        await make_api().server.stop_xray()


@pytest.mark.asyncio
async def test_restart_xray(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/restartXrayService", json=RESPONSE_OK)
    await make_api().server.restart_xray()
    assert httpx_mock.get_request().method == "POST"


@pytest.mark.asyncio
async def test_update_geofile_all(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/updateGeofile", json=RESPONSE_OK)
    await make_api().server.update_geofile()
    assert httpx_mock.get_request().method == "POST"


@pytest.mark.asyncio
async def test_update_geofile_by_name(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/updateGeofile/geoip.dat",
        json=RESPONSE_OK,
    )
    await make_api().server.update_geofile("geoip.dat")
    assert httpx_mock.get_request().method == "POST"
