# Quick Start

## Install

```bash
pip install py3xui
```

## Sync Example

```python
from py3xui import Api

api = Api("http://your-host:2053", "username", "password")
api.login()
print(api.server.get_status())
```

## Async Example

```python
import asyncio
from py3xui import AsyncApi

async def main() -> None:
    api = AsyncApi("http://your-host:2053", "username", "password")
    await api.login()
    print(await api.server.get_status())

asyncio.run(main())
```
