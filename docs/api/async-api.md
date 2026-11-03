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

## Inbounds API (3x-ui v3.11.0)

Additional methods of `api.inbound` (same arguments and return types as the sync client, awaited):

- `get_list_slim()`: list inbounds with settings.clients stripped to email, enable and comment.
- `get_options()`: lightweight inbound projection (`list[InboundOption]`).
- `get_amneziawg_kernel_readiness()`: check whether the host can run kernel-mode AmneziaWG (`AmneziaWGReadiness`).
- `get_all_links()`: share links of all clients of all inbounds (`list[str]`).
- `bulk_delete(inbound_ids)`: delete several inbounds (`InboundBulkDeleteResult`).
- `set_enable(inbound_id, enable)`: enable or disable an inbound without sending its settings.
- `set_sub_sort_index(inbound_id, index)`: set the subscription sort order (0 is rejected by the panel).
- `reset_stats_by_id(inbound_id)`: reset the traffic of one inbound.
- `delete_all_clients(inbound_id)`: delete all clients and keep the inbound (`InboundClientsDeleteResult`).
- `import_inbound(inbound)`: import an `Inbound` or a raw JSON string (lossless), returns the created `Inbound`.
- `push_client_traffics(master_guid, traffics)`: push aggregated client traffic from a master panel.
- `get_fallbacks(inbound_id)`: fallback rules of a master inbound (`list[InboundFallback]`).
- `set_fallbacks(inbound_id, fallbacks)`: replace the fallback rules of a master inbound.
