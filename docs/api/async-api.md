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

## Settings API (3x-ui v3.11.0)

`api.setting` covers `panel/api/setting/*`, with the same methods and arguments as the sync client.

```python
settings = await api.setting.get_all()
settings.sub_title = "My subscription"
await api.setting.update(settings)
```

- Reads: `get_all`, `get_default_settings`, `get_factory_defaults`, `get_default_xray_config`, `get_tg_bot_capabilities`.
- Changes: `update`, `update_user`, `restart_panel`, `validate_regex`.
- Tests: `test_smtp` (returns the result, also on failure), `test_tg_bot`, `test_discord`.

`update` replaces every setting, so start from `get_all()`. Secrets come back blank and a blank secret keeps the stored value; pass `clear_*` to remove one.

API tokens: `get_api_tokens`, `add_api_token` (the only call that returns the token value), `delete_api_token` and `set_api_token_enabled`. The last two need the stored scope of the token in `expected_scope`; a mismatch is rejected by the panel.
