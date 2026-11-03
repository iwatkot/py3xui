import json
from datetime import datetime, timezone
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


def test_generate_uuid():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getNewUUID", json=load_response("new_uuid"))
        assert make_api().server.generate_uuid() == "550e8400-e29b-41d4-a716-446655440000"


def test_generate_mldsa65_keys():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getNewmldsa65", json=load_response("new_mldsa65"))
        keys = make_api().server.generate_mldsa65_keys()

    assert keys.seed == "mldsa65-seed"
    assert keys.verify == "mldsa65-verify"


def test_generate_mlkem768_keys():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getNewmlkem768", json=load_response("new_mlkem768"))
        keys = make_api().server.generate_mlkem768_keys()

    assert keys.seed == "mlkem768-seed"
    assert keys.client == "mlkem768-client"


def test_generate_vless_encryption():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getNewVlessEnc", json=load_response("new_vless_enc"))
        auths = make_api().server.generate_vless_encryption()

    assert [auth.id for auth in auths] == ["x25519", "x25519_random"]
    assert auths[0].label == "X25519, not Post-Quantum"
    assert auths[0].decryption == "mlkem768x25519plus.native.600s.dec"
    assert auths[0].encryption == "mlkem768x25519plus.native.0rtt.enc"


def test_generate_ech_cert():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/getNewEchCert", json=load_response("new_ech_cert"))
        cert = make_api().server.generate_ech_cert("example.com")
        assert form_fields(m.last_request) == {"sni": ["example.com"]}

    assert cert.ech_server_keys == "server-keys"
    assert cert.ech_config_list == "config-list"


def test_get_web_cert_files():
    with requests_mock.Mocker() as m:
        m.get(f"{SERVER_URL}/getWebCertFiles", json=load_response("web_cert_files"))
        files = make_api().server.get_web_cert_files()

    assert files.web_cert_file == "/root/cert/example.com/fullchain.pem"
    assert files.web_key_file == "/root/cert/example.com/privkey.pem"


def test_get_cert_hash_by_file():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/getCertHash", json=load_response("cert_hash"))
        hashes = make_api().server.get_cert_hash(cert_file="/root/cert.pem")
        assert form_fields(m.last_request) == {"certFile": ["/root/cert.pem"]}

    assert hashes == ["e8e2d3"]


def test_get_cert_hash_by_content():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/getCertHash", json=load_response("cert_hash"))
        make_api().server.get_cert_hash(cert_content="PEM")
        assert form_fields(m.last_request) == {"certContent": ["PEM"]}


def test_get_remote_cert_hash():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/getRemoteCertHash", json=load_response("cert_hash"))
        hashes = make_api().server.get_remote_cert_hash("cloudflare-dns.com")
        assert form_fields(m.last_request) == {
            "server": ["cloudflare-dns.com"],
            "allowPrivate": ["false"],
        }

    assert hashes == ["e8e2d3"]


def test_get_remote_cert_hash_private_blocked():
    response = {
        ApiFields.SUCCESS: False,
        ApiFields.MSG: "get remote cert hash (private address blocked)",
        ApiFields.OBJ: {"privateTarget": True},
    }
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/getRemoteCertHash", json=response)
        with pytest.raises(ValueError):
            make_api().server.get_remote_cert_hash("10.0.0.1")


def test_scan_reality_target():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/scanRealityTarget", json=load_response("reality_scan"))
        result = make_api().server.scan_reality_target(
            "www.cloudflare.com:443", sni="cloudflare.com", xver=1, allow_private=True
        )
        assert form_fields(m.last_request) == {
            "target": ["www.cloudflare.com:443"],
            "sni": ["cloudflare.com"],
            "xver": ["1"],
            "allowPrivate": ["true"],
        }

    assert result.target == "www.cloudflare.com:443"
    assert result.feasible is True
    assert result.private_target is False
    assert result.tls_version == "1.3"
    assert result.curve_id == "X25519"
    assert result.cert_chain_valid is True
    assert result.cert_chain_bytes == 3427
    assert result.not_after == "2026-08-01T00:00:00Z"
    assert result.server_names == ["www.cloudflare.com"]
    assert result.latency_ms == 180


def test_scan_reality_targets():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/scanRealityTargets", json=load_response("reality_scans"))
        results = make_api().server.scan_reality_targets(["www.cloudflare.com", "10.0.0.0/99"])
        assert form_fields(m.last_request) == {"targets": ["www.cloudflare.com,10.0.0.0/99"]}

    assert [result.feasible for result in results] == [True, False]
    assert results[1].server_names is None
    assert results[1].reason == "invalid CIDR: bad mask"


def test_scan_reality_targets_from_settings():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/scanRealityTargets", json=RESPONSE_OK)
        assert make_api().server.scan_reality_targets() == []
        assert form_fields(m.last_request) == {}


def test_get_logs():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/logs/20", json=load_response("logs"))
        lines = make_api().server.get_logs(20)
        assert form_fields(m.last_request) == {"level": ["info"], "syslog": ["false"]}

    assert lines == [
        "2025/01/01 12:00:00 INFO - Server started",
        "2025/01/01 12:00:01 INFO - Xray is running",
    ]


def test_get_logs_syslog():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/logs/20", json=RESPONSE_OK)
        assert make_api().server.get_logs(20, level="err", syslog=True) == []
        assert form_fields(m.last_request) == {"level": ["err"], "syslog": ["true"]}


def test_get_xray_logs():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/xraylogs/20", json=load_response("xray_logs"))
        entries = make_api().server.get_xray_logs(20, keyword="alice", show_blocked=False)
        assert form_fields(m.last_request) == {
            "filter": ["alice"],
            "showDirect": ["true"],
            "showBlocked": ["false"],
            "showProxy": ["true"],
        }

    assert len(entries) == 1
    assert entries[0].date_time == datetime(2025, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
    assert entries[0].from_address == "192.0.2.10:54321"
    assert entries[0].to_address == "example.com:443"
    assert entries[0].inbound == "inbound-443"
    assert entries[0].outbound == "proxy"
    assert entries[0].email == "alice@example.com"
    assert entries[0].event == 2


def test_get_xray_logs_without_access_log():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/xraylogs/20", json=RESPONSE_OK)
        assert make_api().server.get_xray_logs(20) == []


def test_get_amneziawg_logs():
    with requests_mock.Mocker() as m:
        m.post(f"{SERVER_URL}/amneziawglogs/20", json=load_response("amneziawg_logs"))
        logs = make_api().server.get_amneziawg_logs(20, keyword="peer")
        assert form_fields(m.last_request) == {"filter": ["peer"]}

    assert logs.running is True
    assert logs.events == ["2025/01/01 12:00:00 amneziawg: started interface awg1 for inbound 1"]
    assert logs.peers[0].interface == "awg1"
    assert logs.peers[0].inbound_id == 1
    assert logs.peers[0].allowed_ips == "10.8.1.2/32"
    assert logs.peers[0].handshake == 1735732800000
    assert logs.peers[0].online is True
