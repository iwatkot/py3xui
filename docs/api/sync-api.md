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

## Inbounds API (3x-ui v3.11.0)

Additional methods of `api.inbound`:

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
