# Asynchronous API

## Create Client

```python
from py3xui import AsyncApi

api = AsyncApi("http://your-host:2053", "username", "password")
await api.login()
```

## Basic Health Check

```python
status = await api.server.get_status()
print("CPU:", status.cpu)
print("Memory:", status.mem.current, "/", status.mem.total)
```

## Typical Flow

```python
inbounds = await api.inbound.get_list()
client = await api.client.get_by_email("user@example.com")
online = await api.client.online()
status = await api.server.get_status()
```

## Concurrent Reads Example

```python
import asyncio

status_task = api.server.get_status()
inbounds_task = api.inbound.get_list()
online_task = api.client.online()

status, inbounds, online = await asyncio.gather(
	status_task,
	inbounds_task,
	online_task,
)

print(status.cpu, len(inbounds), len(online))
```

## Error Handling Pattern

```python
try:
	await api.login()
	print(await api.server.get_status())
except ValueError as exc:
	print("API response error:", exc)
except Exception as exc:
	print("Unexpected failure:", exc)
```

## Notes

- Use inside an event loop.
- Best for concurrent integrations and high-throughput workloads.

## More Examples

- [Common Tasks](../examples/common-tasks.md)
- [Asynchronous Recipes](../examples/async-recipes.md)

## Server API (3x-ui v3.11.0)

- `await api.server.get_fail2ban_status()`: availability of Fail2ban, which per-client IP limits depend on.
- `await api.server.get_cpu_history(bucket)`: legacy aggregated CPU history.
- `await api.server.get_history(metric, bucket)`: aggregated history of a system metric.
- `await api.server.get_xray_metrics_state()`: state of the Xray runtime metrics collection.
- `await api.server.get_xray_metrics_history(metric, bucket)`: aggregated history of an Xray metric.
- `await api.server.get_xray_observatory()`: latest Xray observatory results per outbound.
- `await api.server.get_xray_observatory_history(tag, bucket)`: delay history of an observatory outbound.
- `await api.server.get_panel_update_info()`: current and latest version of the panel.
- `await api.server.get_update_status()`: outcome of the most recent panel self-update.
- `await api.server.update_panel(dev=None)`: starts a panel self-update and returns the run ID.
- `await api.server.set_update_channel(dev)`: switches the update channel between stable and dev.
- `await api.server.stop_xray()` / `await api.server.restart_xray()`: Xray service control.
- `await api.server.update_geofile(file_name=None)`: updates one geofile, or all of them without an argument.
- `await api.server.generate_uuid()`: generates a new UUID.
- `await api.server.generate_mldsa65_keys()` / `await api.server.generate_mlkem768_keys()`: generate post-quantum key pairs.
- `await api.server.generate_vless_encryption()`: generates VLESS encryption options.
- `await api.server.generate_ech_cert(sni)`: generates an ECH key set.
- `await api.server.get_web_cert_files()`: paths of the web TLS files of the panel.
- `await api.server.get_cert_hash(cert_file=None, cert_content=None)`: SHA-256 hash of a certificate for pinning.
- `await api.server.get_remote_cert_hash(server, allow_private=False)`: SHA-256 hash of the certificate of a remote server.
- `await api.server.scan_reality_target(target, sni=None, xver=0, allow_private=False)`: probes a REALITY target.
- `await api.server.scan_reality_targets(targets=None)`: probes several REALITY targets.
