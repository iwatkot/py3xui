import json
from datetime import datetime, timezone
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from py3xui import AsyncApi, InboundClientIpEntry, InboundClientIps
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


@pytest.mark.asyncio
async def test_generate_uuid(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getNewUUID",
        json=load_response("new_uuid"),
    )
    assert await make_api().server.generate_uuid() == "550e8400-e29b-41d4-a716-446655440000"


@pytest.mark.asyncio
async def test_generate_mldsa65_keys(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getNewmldsa65",
        json=load_response("new_mldsa65"),
    )
    keys = await make_api().server.generate_mldsa65_keys()

    assert keys.seed == "mldsa65-seed"
    assert keys.verify == "mldsa65-verify"


@pytest.mark.asyncio
async def test_generate_mlkem768_keys(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getNewmlkem768",
        json=load_response("new_mlkem768"),
    )
    keys = await make_api().server.generate_mlkem768_keys()

    assert keys.seed == "mlkem768-seed"
    assert keys.client == "mlkem768-client"


@pytest.mark.asyncio
async def test_generate_vless_encryption(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getNewVlessEnc",
        json=load_response("new_vless_enc"),
    )
    auths = await make_api().server.generate_vless_encryption()

    assert [auth.id for auth in auths] == ["x25519", "x25519_random"]
    assert auths[0].label == "X25519, not Post-Quantum"
    assert auths[0].decryption == "mlkem768x25519plus.native.600s.dec"
    assert auths[0].encryption == "mlkem768x25519plus.native.0rtt.enc"


@pytest.mark.asyncio
async def test_generate_ech_cert(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/getNewEchCert",
        json=load_response("new_ech_cert"),
    )
    cert = await make_api().server.generate_ech_cert("example.com")
    assert form_fields(httpx_mock.get_request()) == {"sni": ["example.com"]}

    assert cert.ech_server_keys == "server-keys"
    assert cert.ech_config_list == "config-list"


@pytest.mark.asyncio
async def test_get_web_cert_files(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getWebCertFiles",
        json=load_response("web_cert_files"),
    )
    files = await make_api().server.get_web_cert_files()

    assert files.web_cert_file == "/root/cert/example.com/fullchain.pem"
    assert files.web_key_file == "/root/cert/example.com/privkey.pem"


@pytest.mark.asyncio
async def test_get_cert_hash_by_file(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/getCertHash",
        json=load_response("cert_hash"),
    )
    hashes = await make_api().server.get_cert_hash(cert_file="/root/cert.pem")
    assert form_fields(httpx_mock.get_request()) == {"certFile": ["/root/cert.pem"]}

    assert hashes == ["e8e2d3"]


@pytest.mark.asyncio
async def test_get_cert_hash_by_content(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/getCertHash",
        json=load_response("cert_hash"),
    )
    await make_api().server.get_cert_hash(cert_content="PEM")
    assert form_fields(httpx_mock.get_request()) == {"certContent": ["PEM"]}


@pytest.mark.asyncio
async def test_get_remote_cert_hash(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/getRemoteCertHash",
        json=load_response("cert_hash"),
    )
    hashes = await make_api().server.get_remote_cert_hash("cloudflare-dns.com")
    assert form_fields(httpx_mock.get_request()) == {
        "server": ["cloudflare-dns.com"],
        "allowPrivate": ["false"],
    }

    assert hashes == ["e8e2d3"]


@pytest.mark.asyncio
async def test_get_remote_cert_hash_private_blocked(httpx_mock: HTTPXMock):
    response = {
        ApiFields.SUCCESS: False,
        ApiFields.MSG: "get remote cert hash (private address blocked)",
        ApiFields.OBJ: {"privateTarget": True},
    }
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/getRemoteCertHash", json=response)
    with pytest.raises(ValueError):
        await make_api().server.get_remote_cert_hash("10.0.0.1")


@pytest.mark.asyncio
async def test_scan_reality_target(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/scanRealityTarget",
        json=load_response("reality_scan"),
    )
    result = await make_api().server.scan_reality_target(
        "www.cloudflare.com:443", sni="cloudflare.com", xver=1, allow_private=True
    )
    assert form_fields(httpx_mock.get_request()) == {
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


@pytest.mark.asyncio
async def test_scan_reality_targets(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/scanRealityTargets",
        json=load_response("reality_scans"),
    )
    results = await make_api().server.scan_reality_targets(["www.cloudflare.com", "10.0.0.0/99"])
    assert form_fields(httpx_mock.get_request()) == {"targets": ["www.cloudflare.com,10.0.0.0/99"]}

    assert [result.feasible for result in results] == [True, False]
    assert results[1].server_names is None
    assert results[1].reason == "invalid CIDR: bad mask"


@pytest.mark.asyncio
async def test_scan_reality_targets_from_settings(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/scanRealityTargets", json=RESPONSE_OK)
    assert await make_api().server.scan_reality_targets() == []
    assert form_fields(httpx_mock.get_request()) == {}


@pytest.mark.asyncio
async def test_get_logs(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/logs/20", json=load_response("logs"))
    lines = await make_api().server.get_logs(20)
    assert form_fields(httpx_mock.get_request()) == {"level": ["info"], "syslog": ["false"]}

    assert lines == [
        "2025/01/01 12:00:00 INFO - Server started",
        "2025/01/01 12:00:01 INFO - Xray is running",
    ]


@pytest.mark.asyncio
async def test_get_logs_syslog(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/logs/20", json=RESPONSE_OK)
    assert await make_api().server.get_logs(20, level="err", syslog=True) == []
    assert form_fields(httpx_mock.get_request()) == {"level": ["err"], "syslog": ["true"]}


@pytest.mark.asyncio
async def test_get_xray_logs(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/xraylogs/20",
        json=load_response("xray_logs"),
    )
    entries = await make_api().server.get_xray_logs(20, keyword="alice", show_blocked=False)
    assert form_fields(httpx_mock.get_request()) == {
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


@pytest.mark.asyncio
async def test_get_xray_logs_without_access_log(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/xraylogs/20", json=RESPONSE_OK)
    assert await make_api().server.get_xray_logs(20) == []


@pytest.mark.asyncio
async def test_get_amneziawg_logs(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{SERVER_URL}/amneziawglogs/20",
        json=load_response("amneziawg_logs"),
    )
    logs = await make_api().server.get_amneziawg_logs(20, keyword="peer")
    assert form_fields(httpx_mock.get_request()) == {"filter": ["peer"]}

    assert logs.running is True
    assert logs.events == ["2025/01/01 12:00:00 amneziawg: started interface awg1 for inbound 1"]
    assert logs.peers[0].interface == "awg1"
    assert logs.peers[0].inbound_id == 1
    assert logs.peers[0].allowed_ips == "10.8.1.2/32"
    assert logs.peers[0].handshake == 1735732800000
    assert logs.peers[0].online is True


@pytest.mark.asyncio
async def test_get_migration(httpx_mock: HTTPXMock, tmp_path):
    save_path = tmp_path / "migration.dump"
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/getMigration",
        content=b"migration content",
        headers={"Content-Type": "application/octet-stream"},
    )
    await make_api().server.get_migration(str(save_path))

    assert save_path.read_bytes() == b"migration content"


@pytest.mark.asyncio
async def test_get_migration_failed(httpx_mock: HTTPXMock, tmp_path):
    save_path = tmp_path / "migration.dump"
    httpx_mock.add_response(method="GET", url=f"{SERVER_URL}/getMigration", json=RESPONSE_FAILED)
    with pytest.raises(ValueError):
        await make_api().server.get_migration(str(save_path))

    assert not save_path.exists()


@pytest.mark.asyncio
async def test_import_db(httpx_mock: HTTPXMock, tmp_path):
    file_path = tmp_path / "backup.db"
    file_path.write_bytes(b"database content")
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/importDB", json=RESPONSE_OK)
    await make_api().server.import_db(str(file_path))
    body = raw_body(httpx_mock.get_request())
    assert httpx_mock.get_request().headers["Content-Type"].startswith("multipart/form-data")

    assert b'name="keepHostSettings"\r\n\r\ntrue' in body
    assert b'name="db"; filename="backup.db"' in body
    assert b"database content" in body


@pytest.mark.asyncio
async def test_import_db_replace_host_settings(httpx_mock: HTTPXMock, tmp_path):
    file_path = tmp_path / "backup.db"
    file_path.write_bytes(b"database content")
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/importDB", json=RESPONSE_OK)
    await make_api().server.import_db(str(file_path), keep_host_settings=False)
    assert b'name="keepHostSettings"\r\n\r\nfalse' in raw_body(httpx_mock.get_request())


@pytest.mark.asyncio
async def test_import_db_failed(httpx_mock: HTTPXMock, tmp_path):
    file_path = tmp_path / "backup.db"
    file_path.write_bytes(b"not a database")
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/importDB", json=RESPONSE_FAILED)
    with pytest.raises(ValueError):
        await make_api().server.import_db(str(file_path))


@pytest.mark.asyncio
async def test_get_descendants(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/descendants",
        json=load_response("descendants"),
    )
    nodes = await make_api().server.get_descendants()

    assert len(nodes) == 1
    assert nodes[0].guid == "c3d4"
    assert nodes[0].parent_guid == "a1b2"
    assert nodes[0].port == 2053
    assert nodes[0].last_heartbeat == 1735689600
    assert nodes[0].latency_ms == 42
    assert nodes[0].panel_version == "3.11.0"
    assert nodes[0].xray_version == "25.10.31"
    assert nodes[0].xray_state == "running"
    assert nodes[0].xray_error == ""


@pytest.mark.asyncio
async def test_get_client_ips(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{SERVER_URL}/clientIps",
        json=load_response("client_ips"),
    )
    records = await make_api().server.get_client_ips()

    assert [record.client_email for record in records] == [
        "alice@example.com",
        "bob@example.com",
        "carol@example.com",
    ]
    assert records[0].id == 1
    assert records[0].ips[0].ip == "192.0.2.10"
    assert records[0].ips[0].timestamp == 1735689600
    assert records[1].ips is None
    assert records[2].ips[0].ip == "198.51.100.7"
    assert records[2].ips[0].timestamp == 0


@pytest.mark.asyncio
async def test_push_client_ips(httpx_mock: HTTPXMock):
    entry = InboundClientIpEntry(ip="192.0.2.10", timestamp=1735689600)
    record = InboundClientIps(client_email="alice@example.com", ips=[entry])
    httpx_mock.add_response(method="POST", url=f"{SERVER_URL}/clientIps", json=RESPONSE_OK)
    await make_api().server.push_client_ips([record])
    assert json_body(httpx_mock.get_request()) == [
        {
            "clientEmail": "alice@example.com",
            "ips": [{"ip": "192.0.2.10", "timestamp": 1735689600}],
        }
    ]
