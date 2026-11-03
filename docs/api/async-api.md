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

## Hosts API (3x-ui v3.11.0)

Available as `api.host`, with the same methods as the sync client:

- `get_list()`, `get_raw_list()`, `get_by_id(group_id)`, `get_by_inbound(inbound_id)`, `get_tags()`
- `add(host)`, `update(group_id, host)`, `delete(group_id)`, `set_enable(group_id, enable)`, `reorder(group_ids)`
- `bulk_add(host)`, `bulk_set_enable(group_ids, enable)`, `bulk_delete(group_ids)`

`update` replaces the group, so fetch it first and change only what is needed:

```python
group = await api.host.get_by_id("1234567890123456")
group.remark = "cdn-back"
await api.host.update(group.group_id, group)
```
