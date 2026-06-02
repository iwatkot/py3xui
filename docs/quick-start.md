# Quick Start

## Install

```bash
pip install py3xui
```

## Configure Credentials

Recommended environment variables:

```bash
XUI_HOST=http://your-host:2053
XUI_USERNAME=your-username
XUI_PASSWORD=your-password
```

## Sync Example

```python
from py3xui import Api

api = Api.from_env()
api.login()
print(api.server.get_status())
```

## Async Example

```python
import asyncio
from py3xui import AsyncApi

async def main() -> None:
    api = AsyncApi.from_env()
    await api.login()
    print(await api.server.get_status())

asyncio.run(main())
```

## Token Authentication

If your panel exposes token auth, set `XUI_TOKEN` and skip login:

```python
from py3xui import Api

api = Api("http://your-host:2053", token="your-token")
print(api.server.get_status())
```

## Next Steps

- [Authentication](authentication.md)
- [Examples](examples/README.md)
- [Synchronous API](api/sync-api.md)
- [Asynchronous API](api/async-api.md)
