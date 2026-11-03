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

## Sub Balancers API (3x-ui v3.11.0)

Available as `api.sub_balancer`.

| Method | Route |
|---|---|
| `await api.sub_balancer.get_list()` | `GET panel/api/sub-balancers` |
| `await api.sub_balancer.add(balancer)` | `POST panel/api/sub-balancers` |
| `await api.sub_balancer.update(balancer_id, balancer)` | `POST panel/api/sub-balancers/{id}` |
| `await api.sub_balancer.delete(balancer_id)` | `POST panel/api/sub-balancers/{id}/del` |

`update` replaces the whole row: strategy, member weights and sort order that are not set are reset to their defaults, and only `enabled` keeps the stored value when it was not set. To change a single field, take the balancer from `get_list`, modify it and pass it back.

```python
balancer = py3xui.SubBalancer(remark="auto-fastest", inbound_ids=[1, 3])
created = await api.sub_balancer.add(balancer)

created.enabled = False
await api.sub_balancer.update(created.id, created)

await api.sub_balancer.delete(created.id)
```
