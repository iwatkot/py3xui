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

## Sub Balancers API (3x-ui v3.11.0)

Available as `api.sub_balancer`.

| Method | Route |
|---|---|
| `api.sub_balancer.get_list()` | `GET panel/api/sub-balancers` |
| `api.sub_balancer.add(balancer)` | `POST panel/api/sub-balancers` |
| `api.sub_balancer.update(balancer_id, balancer)` | `POST panel/api/sub-balancers/{id}` |
| `api.sub_balancer.delete(balancer_id)` | `POST panel/api/sub-balancers/{id}/del` |

`update` replaces the whole row: strategy, member weights and sort order that are not set are reset to their defaults, and only `enabled` keeps the stored value when it was not set. To change a single field, take the balancer from `get_list`, modify it and pass it back.

```python
balancer = py3xui.SubBalancer(remark="auto-fastest", inbound_ids=[1, 3])
created = api.sub_balancer.add(balancer)

created.enabled = False
api.sub_balancer.update(created.id, created)

api.sub_balancer.delete(created.id)
```
