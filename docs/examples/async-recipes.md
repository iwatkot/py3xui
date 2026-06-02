# Asynchronous Recipes

## Minimal Async Script

```python
import asyncio
from py3xui import AsyncApi

async def main() -> None:
    api = AsyncApi.from_env()
    await api.login()
    print(await api.server.get_status())

asyncio.run(main())
```

## Concurrent Read Operations

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

## Async Client Lifecycle

```python
from uuid import uuid4
from py3xui import Client

inbound_id = 1
email = "client@example.com"

await api.client.add(inbound_id, [Client(id=str(uuid4()), email=email, enable=True)])
client = await api.client.get_by_email(email)

if client:
    client.total_gb = 5 * 1024 * 1024 * 1024
    await api.client.update(str(client.id), client)
    await api.client.delete(inbound_id, str(client.id))
```

## Async Error Handling

```python
try:
    await api.login()
    print(await api.server.get_status())
except ValueError as exc:
    print("API response error:", exc)
except Exception as exc:
    print("Unexpected failure:", exc)
```
