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
node = api.node.get_by_id(1)
node.remark = "Primary edge"
api.node.update(node.id, node)
```
