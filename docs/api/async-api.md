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

## Xray API (3x-ui v3.11.0)

`api.xray` wraps `/panel/api/xray/*`.

```python
settings = await api.xray.get_settings()
traffic = await api.xray.get_outbounds_traffic()
```

| Method | Endpoint | Returns |
|---|---|---|
| `get_settings()` | `POST /panel/api/xray/` | `XraySettings` |
| `get_default_config()` | `GET /panel/api/xray/getDefaultJsonConfig` | `dict` |
| `get_outbounds_traffic()` | `GET /panel/api/xray/getOutboundsTraffic` | `list[OutboundTraffic]` |
| `get_result()` | `GET /panel/api/xray/getXrayResult` | `str` |
| `update(config, outbound_test_url=None)` | `POST /panel/api/xray/update` | `None` |
| `reset_outbound_stats(tag)` | `POST /panel/api/xray/resetOutboundsTraffic` | `None` |
| `warp_get_data()` | `POST /panel/api/xray/warp/data` | `dict` |
| `warp_delete()` | `POST /panel/api/xray/warp/del` | `None` |
| `warp_get_config()` | `POST /panel/api/xray/warp/config` | `dict` |
| `warp_register(private_key, public_key)` | `POST /panel/api/xray/warp/reg` | `dict` |
| `warp_register_masque()` | `POST /panel/api/xray/warp/regMasque` | `dict` |
| `warp_change_ip()` | `POST /panel/api/xray/warp/changeIp` | `dict` |
| `warp_set_license(license_key)` | `POST /panel/api/xray/warp/license` | `dict` |
| `warp_set_interval(interval)` | `POST /panel/api/xray/warp/interval` | `None` |
| `nord_get_countries()` | `POST /panel/api/xray/nord/countries` | `list[dict]` |
| `nord_get_servers(country_id)` | `POST /panel/api/xray/nord/servers` | `dict` |
| `nord_register(token)` | `POST /panel/api/xray/nord/reg` | `dict` |
| `nord_set_key(key)` | `POST /panel/api/xray/nord/setKey` | `dict` |
| `nord_get_data()` | `POST /panel/api/xray/nord/data` | `dict` |
| `nord_delete()` | `POST /panel/api/xray/nord/del` | `None` |
| `pia_get_countries()` | `POST /panel/api/xray/pia/countries` | `list[PiaCountry]` |
| `pia_get_servers(country_code)` | `POST /panel/api/xray/pia/servers` | `PiaServers` |
| `pia_register(username, password)` | `POST /panel/api/xray/pia/reg` | `PiaAccount` |
| `pia_get_data()` | `POST /panel/api/xray/pia/data` | `PiaAccount \| None` |
| `pia_delete()` | `POST /panel/api/xray/pia/del` | `None` |
| `pia_add_key(hostname)` | `POST /panel/api/xray/pia/addKey` | `PiaKey` |
