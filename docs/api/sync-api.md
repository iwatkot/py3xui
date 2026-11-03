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

## Client Details and Safe Updates

`get_details()` returns the full client payload: the client, every inbound it is attached to,
external links, used traffic and tunnel addresses. The panel replaces the client on update, so
edit the returned `details.client` and pass it back: all its fields, including ones py3xui does
not declare, are sent with the update.

```python
details = api.client.get_details("user@example.com")

if details:
	print(details.inbound_ids, details.tunnel_allowed_ips)
	details.client.total_gb = 50 * 1024 * 1024 * 1024
	api.client.update(details.client.uuid, details.client)
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

## Clients API (3x-ui v3.11.0)

All methods live on `api.client`.

- `get_list_paged(page, page_size, *, search, statuses, protocols, inbound_ids, groups, sort, order, expiry_from, expiry_to, usage_from, usage_to, auto_renew, has_tg_id, has_comment)`: one page of clients, filtered and sorted by the panel.
- `get_details_by_sub_id(sub_id)`: full details of all clients with a subscription ID. The panel reports an unknown ID as an error, so this raises `ValueError`.
- `get_details_by_tg_id(tg_id)`: full details of all clients with a Telegram ID.
- `get_renewal_preview(expiry_time, *, reset, reset_day, reset_weekday, reset_max, reset_count)`: auto-renewal dates, nothing is saved.
- `get_traffic(email)`: traffic counters of a client, `None` if there are none.
- `get_sub_links(sub_id)`: share links of a subscription.
- `get_links(email)`: share links of a client.
- `get_happ_link(client_id)`: encrypted Happ link, by client record ID.
