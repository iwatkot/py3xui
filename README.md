<div align="center" markdown>
<img src="https://github.com/iwatkot/py3xui/assets/118521851/42c5d579-6202-4a9e-88f3-2d844fdd95b6">

Sync and Async Object-oriented Python SDK for the 3x-ui API.

<p align="center">
    <a href="#Overview">Overview</a> •
    <a href="#Compatibility-table">Compatibility Table</a> •
    <a href="#Quick-Start">Quick Start</a> •
    <a href="#Examples">Examples</a> •
    <a href="#Bugs-and-Feature-Requests">Bugs and Feature Requests</a> •
    <a href="https://pypi.org/project/py3xui/">PyPI</a>
</p>

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/iwatkot/py3xui)](https://github.com/iwatkot/py3xui/releases)
[![GitHub issues](https://img.shields.io/github/issues/iwatkot/py3xui)](https://github.com/iwatkot/py3xui/issues)
[![Build Status](https://github.com/iwatkot/py3xui/actions/workflows/checks.yml/badge.svg)](https://github.com/iwatkot/py3xui/actions)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/py3xui)](https://pypi.org/project/py3xui/)<br>
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py3xui)](https://pypi.org/project/py3xui/)
[![PyPI - Version](https://img.shields.io/pypi/v/py3xui)](https://pypi.org/project/py3xui/)
[![Maintainability](https://api.codeclimate.com/v1/badges/c03ca2bca0191cb4a2ae/maintainability)](https://codeclimate.com/github/iwatkot/py3xui/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/c03ca2bca0191cb4a2ae/test_coverage)](https://codeclimate.com/github/iwatkot/py3xui/test_coverage)

</div>

## Overview
This SDK is designed to interact with the [3x-ui](https://github.com/MHSanaei/3x-ui) app in a more object-oriented way. It provides both synchronous and asynchronous methods to interact with the app. The SDK is designed to be as simple as possible to use, while still providing a lot of flexibility and uses `Pydantic` models to validate the data.<br>
Used dependencies:
- `requests` for synchronous API
- `httpx` for asynchronous API
- `pydantic` for models

Supported Python versions:
- 3.11
- 3.12

## Compatibility Table
Since the 3x-ui app is under development, the SDK may not be compatible with all versions of the app. The table below shows the compatibility between the SDK and the 3x-ui app. Since the developer of SDK is not related to the 3x-ui app, the latest versions of the software are not guaranteed to be compatible with the SDK. It's recommended to use the specified versions of the software to avoid any issues.

| py3xui Version | 3x-ui Version |
|-------------|---------------|
| 0.2.2       | >=2.3.9, <=2.3.11         |
| 0.2.1       | >=2.3.7         |

The SDK does not support older versions of the 3x-ui app.

## Quick Start
You can use both synchronous and asynchronous methods to interact with the 3x-ui app. Both APIs have the same methods and return the same data, so it's up to you to choose which one to use.<br>
After installing the SDK, you can create a new instance of the API. When creating a new instance, you can either use environment variables or pass the credentials directly. It's strongly recommended to use environment variables to store the API credentials.<br>
On creation, the Api won't connect to the 3x-ui app, so you can spawn new instances without spending resources. But after creating an instance, you'll need to call the `login` method to authenticate the user and save the cookie for future requests.

### Installation
```bash
pip install py3xui
```

### Create a new instance of the SDK
It's recommended to use an environment variable to store the API credentials:
```python
import os

os.environ["XUI_HOST"] = "http://your-3x-ui-host.com:2053"
os.environ["XUI_USERNAME"] = "your-username"
os.environ["XUI_PASSWORD"] = "your-password"
```

To work synchronously:
```python
from py3xui import Api

# Using environment variables:
api = Api.from_env()

# Or using the credentials directly:
api = Api("http://your-3x-ui-host.com:2053", "your-username", "your-password")
```

To work asynchronously:
```python
from py3xui import AsyncApi

# Using environment variables:
api = AsyncApi.from_env()

# Or using the credentials directly:
api = AsyncApi("http://your-3x-ui-host.com:2053", "your-username", "your-password")
```

*️⃣ If you're using a custom URI Path, ensure that you've added it to the host, for example:<br>
If your host is `http://your-3x-ui-host.com:2053` and the URI Path is `/test/`, then the host should be `http://your-3x-ui-host.com:2053/test/`.<br>
Otherwise, all API requests will fail with a `404` error.

*️⃣ If you're using a secret token, which is set in in the 3x-ui panel, you'll also add it, otherwise all API request will fail.<br>
Same as for other credentials, you can use an environment variable to store the token:
```python
...
os.environ["XUI_TOKEN"] = "your-token"

api = Api.from_env()
```

Or pass it directly, when creating an instance:
```python
api = Api("http://your-3x-ui-host.com:2053", "your-username", "your-password", "your-token")
```

### Using TLS and custom certificates
To be filled by @snoups.<br>

#### Case 1: Disabling TLS verification
...

### Case 2: Using custom certificates
...


### Login
No matter which API you're using or if was it created using environment variables or credentials, you'll need to call the `login` method to authenticate the user and save the cookie for future requests.
```python
from py3xui import Api, AsyncApi

api = Api.from_env()
api.login()

async_api = AsyncApi.from_env()
await async_api.login()
```

## Examples
You'll find detailed docs with usage examples for both APIs and for used models in the corresponding package directories:
- [Synchronous API](py3xui/api/README.md)
- [Asynchronous API](py3xui/async_api/README.md)
- [Client](py3xui/client/README.md)
- [Inbound](py3xui/inbound/README.md)

In this section, you'll find some examples of how to use the SDK. In the examples, we'll use the synchronous API, but you can use the asynchronous API in the same way, just remember to use `await` before calling the methods.<br>

### Get inbounds list
```python
from py3xui import Api, Inbound

api = Api.from_env()
api.login()
inbounds: List[Inbound] = api.inbound.get_list()
```

### Add a new inbound
```python
from py3xui import Api
from py3xui.inbound import Inbound, Settings, Sniffing, StreamSettings

api = Api.from_env()
api.login()

settings = Settings()
sniffing = Sniffing(enabled=True)

tcp_settings = {
    "acceptProxyProtocol": False,
    "header": {"type": "none"},
}
stream_settings = StreamSettings(security="reality", network="tcp", tcp_settings=tcp_settings)

inbound = Inbound(
    enable=True,
    port=443,
    protocol="vless",
    settings=settings,
    stream_settings=stream_settings,
    sniffing=sniffing,
    remark="test3",
)

api.inbound.add(inbound)
```

### Get a client by email
```python
from py3xui import Api, Client

api = Api.from_env()
api.login()

client: Client = api.client.get_by_email("some-email")
```

### Add a new client
```python
from py3xui import Api, Client

api = Api.from_env()
api.login()

new_client = Client(id=str(uuid.uuid4()), email="test", enable=True)
inbound_id = 1

api.client.add(inbound_id, [new_client])
```

## Bugs and Feature Requests
If you find a bug or have a feature request, please open an issue on the GitHub repository.<br>
You're also welcome to contribute to the project by opening a pull request.
