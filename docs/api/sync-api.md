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
