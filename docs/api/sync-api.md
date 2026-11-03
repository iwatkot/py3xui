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

## Xray API (3x-ui v3.11.0)

`api.xray` wraps `/panel/api/xray/*`.

```python
settings = api.xray.get_settings()
traffic = api.xray.get_outbounds_traffic()
```

| Method | Endpoint | Returns |
|---|---|---|
| `get_settings()` | `POST /panel/api/xray/` | `XraySettings` |
| `get_default_config()` | `GET /panel/api/xray/getDefaultJsonConfig` | `dict` |
| `get_outbounds_traffic()` | `GET /panel/api/xray/getOutboundsTraffic` | `list[OutboundTraffic]` |
| `get_result()` | `GET /panel/api/xray/getXrayResult` | `str` |
| `update(config, outbound_test_url=None)` | `POST /panel/api/xray/update` | `None` |
| `reset_outbound_stats(tag)` | `POST /panel/api/xray/resetOutboundsTraffic` | `None` |
