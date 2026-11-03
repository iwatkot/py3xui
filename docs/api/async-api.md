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

## Nodes API (3x-ui v3.11.0)

Available as `api.node`. Method signatures are the same in the sync and async clients.

| Method | Route |
|---|---|
| `get_list()` | `GET /panel/api/nodes/list` |
| `get_by_id(node_id)` | `GET /panel/api/nodes/get/{id}` |
| `get_web_cert_files(node_id)` | `GET /panel/api/nodes/webCert/{id}` |
| `add(node)` | `POST /panel/api/nodes/add` |
| `update(node_id, node)` | `POST /panel/api/nodes/update/{id}` |
| `delete(node_id)` | `POST /panel/api/nodes/del/{id}` |
| `set_enable(node_id, enable)` | `POST /panel/api/nodes/setEnable/{id}` |
| `test(node)` | `POST /panel/api/nodes/test` |
| `get_cert_fingerprint(node)` | `POST /panel/api/nodes/certFingerprint` |
| `get_remote_inbounds(node)` | `POST /panel/api/nodes/inbounds` |
| `probe(node_id)` | `POST /panel/api/nodes/probe/{id}` |
| `update_panel(node_ids, dev=False)` | `POST /panel/api/nodes/updatePanel` |
| `get_history(node_id, metric, bucket)` | `GET /panel/api/nodes/history/{id}/{metric}/{bucket}` |
| `get_mtls_ca()` | `POST /panel/api/nodes/mtls/ca` |
| `set_mtls_trust_ca(ca_cert)` | `POST /panel/api/nodes/mtls/trustCA` |
| `reload_mtls_client()` | `POST /panel/api/nodes/mtls/reloadClient` |

`api_token` is write-only: the panel never returns it, so a read and update cycle keeps the stored token.

```python
node = await api.node.get_by_id(1)
node.remark = "Primary edge"
await api.node.update(node.id, node)
```
