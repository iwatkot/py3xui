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

## Client Details and Safe Updates

`get_details()` returns the full client payload: the client, every inbound it is attached to,
external links, used traffic and tunnel addresses. The panel replaces the client on update, so
edit the returned `details.client` and pass it back: all its fields, including ones py3xui does
not declare, are sent with the update.

```python
details = await api.client.get_details("user@example.com")

if details:
	print(details.inbound_ids, details.tunnel_allowed_ips)
	details.client.total_gb = 50 * 1024 * 1024 * 1024
	await api.client.update(details.client.uuid, details.client)
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

## Clients API (3x-ui v3.11.0)

All methods live on `api.client` and match the sync API in names, arguments and return types.

- `get_list_paged(page, page_size, *, search, statuses, protocols, inbound_ids, groups, sort, order, expiry_from, expiry_to, usage_from, usage_to, auto_renew, has_tg_id, has_comment)`: one page of clients, filtered and sorted by the panel.
- `get_details_by_sub_id(sub_id)`: full details of all clients with a subscription ID. The panel reports an unknown ID as an error, so this raises `ValueError`.
- `get_details_by_tg_id(tg_id)`: full details of all clients with a Telegram ID.
- `get_renewal_preview(expiry_time, *, reset, reset_day, reset_weekday, reset_max, reset_count)`: auto-renewal dates, nothing is saved.
- `get_traffic(email)`: traffic counters of a client, `None` if there are none.
- `get_sub_links(sub_id)`: share links of a subscription.
- `get_links(email)`: share links of a client.
- `get_happ_link(client_id)`: encrypted Happ link, by client record ID.
- `attach(email, inbound_ids)`: attaches a client to more inbounds.
- `detach(email, inbound_ids)`: detaches a client from inbounds, the client is kept.
- `set_external_links(email, links)`: replaces all external links and subscriptions of a client.
- `delete_orphans()`: deletes clients without inbounds, returns the number of deleted clients.
- `export_clients()`: all clients with their inbounds and usage counters.
- `import_clients(entries)`: imports the result of `export_clients`, existing emails are skipped.
- `bulk_adjust(emails, add_days, add_bytes, *, flow, limit_hwid, ad_tag)`: shifts the expiry and traffic limit of many clients, optionally sets flow, device limit and ad tag.
- `bulk_enable(emails)` / `bulk_disable(emails)`: enables or disables many clients.
- `bulk_delete(emails, keep_traffic)`: deletes many clients.
- `bulk_add(entries)`: creates many clients, each with its own inbounds.
- `bulk_attach(emails, inbound_ids)` / `bulk_detach(emails, inbound_ids)`: attaches many clients to inbounds or detaches them.
- `bulk_reset_stats(emails)`: resets the traffic counters of many clients, returns their number.
- `get_groups()`: all client groups with member counts and traffic.
- `get_group_emails(name)`: emails of the clients of a group.
- `add_group(name)`: creates an empty group.
- `rename_group(old_name, new_name)`: renames a group, returns the number of affected clients.
- `delete_group(name)`: deletes a group, the clients are kept. Returns the number of affected clients.
- `reset_group_stats(name)`: resets the traffic counter of a group, client counters are not changed.
- `bulk_add_to_group(group, emails)` / `bulk_remove_from_group(emails)`: sets or clears the group of many clients, returns the number of affected clients.
