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

## Settings API (3x-ui v3.11.0)

`api.setting` covers `panel/api/setting/*`.

```python
settings = api.setting.get_all()
settings.sub_title = "My subscription"
api.setting.update(settings)
```

- Reads: `get_all`, `get_default_settings`, `get_factory_defaults`, `get_default_xray_config`, `get_tg_bot_capabilities`.
- Changes: `update`, `update_user`, `restart_panel`, `validate_regex`.
- Tests: `test_smtp` (returns the result, also on failure), `test_tg_bot`, `test_discord`.

`update` replaces every setting, so start from `get_all()`. Secrets come back blank and a blank secret keeps the stored value; pass `clear_*` to remove one.
