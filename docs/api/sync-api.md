# Synchronous API

## Create Client

```python
from py3xui import Api

api = Api("http://your-host:2053", "username", "password")
api.login()
```

## Basic Health Check

```python
status = api.server.get_status()
print("CPU:", status.cpu)
print("Memory:", status.mem.current, "/", status.mem.total)
```

## Typical Flow

```python
inbounds = api.inbound.get_list()
client = api.client.get_by_email("user@example.com")
online = api.client.online()
status = api.server.get_status()
```

## Client Lifecycle Example

```python
from uuid import uuid4
from py3xui import Client

inbound_id = 1
email = "demo@example.com"

api.client.add(inbound_id, [Client(id=str(uuid4()), email=email, enable=True)])
client = api.client.get_by_email(email)

if client:
	client.total_gb = 10 * 1024 * 1024 * 1024
	api.client.update(str(client.id), client)

api.client.reset_ips(email)
api.client.reset_stats(inbound_id, email)
api.client.delete(inbound_id, str(client.id) if client else email)
```

## Error Handling Pattern

```python
try:
	api.login()
	print(api.server.get_status())
except ValueError as exc:
	print("API response error:", exc)
except Exception as exc:
	print("Unexpected failure:", exc)
```

## Notes

- Calls are blocking.
- Suitable for scripts, cron jobs, and simple service integrations.

## More Examples

- [Common Tasks](../examples/common-tasks.md)
- [Synchronous Recipes](../examples/sync-recipes.md)

## Server API (3x-ui v3.11.0)

- `api.server.get_fail2ban_status()`: availability of Fail2ban, which per-client IP limits depend on.
- `api.server.get_cpu_history(bucket)`: legacy aggregated CPU history.
- `api.server.get_history(metric, bucket)`: aggregated history of a system metric.
- `api.server.get_xray_metrics_state()`: state of the Xray runtime metrics collection.
- `api.server.get_xray_metrics_history(metric, bucket)`: aggregated history of an Xray metric.
- `api.server.get_xray_observatory()`: latest Xray observatory results per outbound.
- `api.server.get_xray_observatory_history(tag, bucket)`: delay history of an observatory outbound.
- `api.server.get_panel_update_info()`: current and latest version of the panel.
- `api.server.get_update_status()`: outcome of the most recent panel self-update.
- `api.server.update_panel(dev=None)`: starts a panel self-update and returns the run ID.
- `api.server.set_update_channel(dev)`: switches the update channel between stable and dev.
- `api.server.stop_xray()` / `api.server.restart_xray()`: Xray service control.
- `api.server.update_geofile(file_name=None)`: updates one geofile, or all of them without an argument.
- `api.server.generate_uuid()`: generates a new UUID.
- `api.server.generate_mldsa65_keys()` / `api.server.generate_mlkem768_keys()`: generate post-quantum key pairs.
- `api.server.generate_vless_encryption()`: generates VLESS encryption options.
- `api.server.generate_ech_cert(sni)`: generates an ECH key set.
- `api.server.get_web_cert_files()`: paths of the web TLS files of the panel.
- `api.server.get_cert_hash(cert_file=None, cert_content=None)`: SHA-256 hash of a certificate for pinning.
- `api.server.get_remote_cert_hash(server, allow_private=False)`: SHA-256 hash of the certificate of a remote server.
- `api.server.scan_reality_target(target, sni=None, xver=0, allow_private=False)`: probes a REALITY target.
- `api.server.scan_reality_targets(targets=None)`: probes several REALITY targets.
- `api.server.get_logs(count, level="info", syslog=False)`: last lines of the panel log.
- `api.server.get_xray_logs(count, keyword="", show_direct=True, show_blocked=True, show_proxy=True)`: last lines of the Xray access log.
- `api.server.get_amneziawg_logs(count, keyword="")`: live AmneziaWG activity and log lines.
- `api.server.get_migration(save_path)`: saves a cross-engine migration file.
- `api.server.import_db(file_path, keep_host_settings=True)`: restores the panel database from a file.
- `api.server.get_descendants()`: summaries of the nodes managed by the panel.
- `api.server.get_client_ips()`: recently active IP addresses of all the clients.
- `api.server.push_client_ips(client_ips)`: merges recently active IP addresses into the panel database.
