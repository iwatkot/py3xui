import json
from urllib.parse import parse_qs

import pytest
import requests_mock

from py3xui import Api
from py3xui.api.api_base import ApiFields

RESPONSES_DIR = "tests/responses"
HOST = "http://localhost"
USERNAME = "admin"
PASSWORD = "admin"
SESSION = "abc123"
SERVER_URL = f"{HOST}/panel/api/server"
RESPONSE_OK = {ApiFields.SUCCESS: True, ApiFields.MSG: "", ApiFields.OBJ: None}
RESPONSE_FAILED = {ApiFields.SUCCESS: False, ApiFields.MSG: "failed", ApiFields.OBJ: None}


def make_api() -> Api:
    api = Api(HOST, USERNAME, PASSWORD)
    api.session = SESSION
    return api


def load_response(name: str) -> dict:
    with open(f"{RESPONSES_DIR}/server_{name}.json", encoding="utf-8") as file:
        return json.load(file)


def form_fields(request) -> dict:
    return parse_qs(request.text or "", keep_blank_values=True)


def json_body(request):
    return request.json()


def raw_body(request) -> bytes:
    return request.body


def test_get_fail2ban_status():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/fail2banStatus", json=load_response("fail2ban_status"))
        status = make_api().server.get_fail2ban_status()

    assert status.enabled is True
    assert status.installed is True
    assert status.usable is True
    assert status.windows is False


def test_get_cpu_history():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/cpuHistory/60", json=load_response("cpu_history"))
        points = make_api().server.get_cpu_history(60)

    assert [(point.t, point.cpu) for point in points] == [(1700000000, 12.5), (1700000060, 13.1)]


def test_get_history():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/history/mem/30", json=load_response("history"))
        points = make_api().server.get_history("mem", 30)

    assert [(point.t, point.v) for point in points] == [(1700000000, 12.5), (1700000002, 13.1)]


def test_get_history_empty():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/history/mem/30", json=RESPONSE_OK)
        assert make_api().server.get_history("mem", 30) == []


def test_get_history_failed():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/history/nope/30", json=RESPONSE_FAILED)
        with pytest.raises(ValueError):
            make_api().server.get_history("nope", 30)


def test_get_xray_metrics_state():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/xrayMetricsState", json=load_response("xray_metrics_state"))
        state = make_api().server.get_xray_metrics_state()

    assert state.enabled is False
    assert state.listen == ""
    assert state.reason == "metrics block is not configured"


def test_get_xray_metrics_history():
    with requests_mock.Mocker() as m:
        m.get(
            f"{SERVER_URL}/xrayMetricsHistory/xrAlloc/60",
            json=load_response("xray_metrics_history"),
        )
        points = make_api().server.get_xray_metrics_history("xrAlloc", 60)

    assert [(point.t, point.v) for point in points] == [(1700000000, 1048576.0)]


def test_get_xray_observatory():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/xrayObservatory", json=load_response("xray_observatory"))
        snapshots = make_api().server.get_xray_observatory()

    assert len(snapshots) == 1
    assert snapshots[0].tag == "proxy"
    assert snapshots[0].alive is True
    assert snapshots[0].delay == 120
    assert snapshots[0].last_seen_time == 1700000000
    assert snapshots[0].last_try_time == 1700000030
    assert snapshots[0].updated_at == 1700000031


def test_get_xray_observatory_history():
    with requests_mock.Mocker() as m:
        m.get(
            f"{SERVER_URL}/xrayObservatoryHistory/out%2Fbound/60",
            json=load_response("xray_observatory_history"),
        )
        points = make_api().server.get_xray_observatory_history("out/bound", 60)

    assert [(point.t, point.v) for point in points] == [(1700000000, 120.0)]


def test_get_panel_update_info():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getPanelUpdateInfo", json=load_response("panel_update_info"))
        info = make_api().server.get_panel_update_info()

    assert info.channel == "dev"
    assert info.current_version == "3.11.0-dev"
    assert info.latest_version == "dev+abc1234"
    assert info.current_commit == "def5678"
    assert info.latest_commit == "abc1234"
    assert info.update_available is True


def test_get_panel_update_info_failed():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getPanelUpdateInfo", json={ApiFields.SUCCESS: False})
        with pytest.raises(ValueError):
            make_api().server.get_panel_update_info()


def test_get_update_status():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getUpdateStatus", json=load_response("update_status"))
        status = make_api().server.get_update_status()

    assert status.run_id == "1735689600123456789"
    assert status.state == "success"
    assert status.exit_code == 0
    assert status.finished_at == 1735689612


def test_update_panel():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/updatePanel", json=load_response("update_panel"))
        run_id = make_api().server.update_panel()
        assert form_fields(m.last_request) == {}

    assert run_id == "1735689600123456789"


def test_update_panel_dev_channel():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/updatePanel", json=load_response("update_panel"))
        make_api().server.update_panel(dev=True)
        assert form_fields(m.last_request) == {"dev": ["true"]}


def test_set_update_channel():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/setUpdateChannel", json=RESPONSE_OK)
        make_api().server.set_update_channel(False)
        assert form_fields(m.last_request) == {"dev": ["false"]}


def test_stop_xray():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/stopXrayService", json=RESPONSE_OK)
        make_api().server.stop_xray()
        assert m.last_request.method == "POST"


def test_stop_xray_failed():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/stopXrayService", json=RESPONSE_FAILED)
        with pytest.raises(ValueError):
            make_api().server.stop_xray()


def test_restart_xray():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/restartXrayService", json=RESPONSE_OK)
        make_api().server.restart_xray()
        assert m.last_request.method == "POST"


def test_update_geofile_all():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/updateGeofile", json=RESPONSE_OK)
        make_api().server.update_geofile()
        assert m.last_request.method == "POST"


def test_update_geofile_by_name():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/updateGeofile/geoip.dat", json=RESPONSE_OK)
        make_api().server.update_geofile("geoip.dat")
        assert m.last_request.method == "POST"
