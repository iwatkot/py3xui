<div align="center" markdown>
<img src="https://github.com/iwatkot/py3xui/assets/118521851/42c5d579-6202-4a9e-88f3-2d844fdd95b6">

⚠️ The legacy secret token feature was removed in 3x-UI 2.6.0. ⚠️
The project also supports optional bearer token authentication with the `token` constructor argument or `XUI_TOKEN` environment variable for panels that expose token auth.

Sync and Async Object-oriented Python SDK for the 3x-ui API.

<p align="center">
	<a href="#Overview">Overview</a> •
	<a href="#Quick-Start">Quick Start</a> •
	<a href="#Examples">Examples</a> •
	<a href="#Bugs-and-Feature-Requests">Bugs and Feature Requests</a> •
	<a href="https://py3xui.gitbook.io/py3xui-docs">Documentation</a> •
	<a href="https://pypi.org/project/py3xui/">PyPI</a>
</p>

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/iwatkot/py3xui)](https://github.com/iwatkot/py3xui/releases)
[![PyPI - Version](https://img.shields.io/pypi/v/py3xui)](https://pypi.org/project/py3xui/)
[![GitHub issues](https://img.shields.io/github/issues/iwatkot/py3xui)](https://github.com/iwatkot/py3xui/issues)
[![Build Status](https://github.com/iwatkot/py3xui/actions/workflows/checks.yml/badge.svg)](https://github.com/iwatkot/py3xui/actions)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)<br>
[![PyPI - Downloads](https://img.shields.io/pypi/dm/py3xui)](https://pypi.org/project/py3xui/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py3xui)](https://pypi.org/project/py3xui/)
[![codecov](https://codecov.io/github/iwatkot/py3xui/graph/badge.svg?token=M9EYR3D23P)](https://codecov.io/github/iwatkot/py3xui)

_ℹ️ If you need a JavaScript SDK, check out [js3xui](https://github.com/iwatkot/js3xui)._
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

Since the 3x-ui app is under development, the SDK may not be compatible with all versions of the app. The developer of SDK is not related to the 3x-ui app, therefore the latest versions of the software are not guaranteed to be compatible with the SDK. <br>
The SDK does not support versions of the 3x-ui older than `2.3.7`.

## Quick Start
You can use both synchronous and asynchronous methods to interact with the 3x-ui app. Both APIs have the same methods and return the same data, so it's up to you to choose which one to use.<br>
After installing the SDK, you can create a new instance of the API. When creating a new instance, you can either use environment variables or pass the credentials directly. It's strongly recommended to use environment variables to store the API credentials.<br>
On creation, the Api won't connect to the 3x-ui app, so you can spawn new instances without spending resources. But after creating an instance, you'll need to call the `login` method to authenticate the user and save the cookie for future requests.

### Installation
```bash
pip install py3xui
```

### Create a new instance of the API
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

For synchronous token authentication, set `XUI_TOKEN` instead of `XUI_USERNAME` and `XUI_PASSWORD`, or pass `token` directly:
```python
from py3xui import Api

api = Api("http://your-3x-ui-host.com:2053", token="your-api-token")
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

### Using TLS and custom certificates
Interacting with server over HTTPS requires careful management of TLS verification to ensure secure communications. This SDK provides options for setting TLS configurations, which include specifying custom certificates for increased trust or disabling TLS verification when necessary.

#### Case 1: Disabling TLS verification
For development, you can disable TLS verification. This is not recommended for production due to the increased risk of security threats like man-in-the-middle attacks.
```python
api = Api("http://your-3x-ui-host.com:2053", "your-username", "your-password", use_tls_verify=False)
```
❗ Warning: Never disable TLS verification in production.

#### Case 2: Using сustom сertificates
If you are interacting with a server that uses a self-signed certificate or one not recognized by the standard CA bundle, you can specify a custom certificate path:
```python
api = Api(
	"http://your-3x-ui-host.com:2053",
	"your-username",
	"your-password",
	custom_certificate_path="/path/to/your/certificate.pem",
)
```
This allows you to maintain TLS verification by providing a trusted certificate explicitly.

### Login
When using username/password authentication, call the `login` method to authenticate the user and save the cookie for future requests. The API first fetches the CSRF token from the `csrf-token` endpoint and sends it with the login request.
```python
from py3xui import Api, AsyncApi

api = Api.from_env()
api.login()

async_api = AsyncApi.from_env()
await async_api.login()
```

When the synchronous `Api` is created with `token` or `XUI_TOKEN`, do not call `login`; requests are authenticated with the `Authorization: Bearer ...` header.

#### Using two-factor authentication
If you enabled two-factor authentication in the 3x-ui app, you'll need to pass the two-factor code to the `login` method. The code can be either a string or an integer.
```python
from py3xui import Api, AsyncApi

api = Api.from_env()
api.login("123456")  # Replace with your actual two-factor code.

async_api = AsyncApi.from_env()
await async_api.login("123456")  # Replace with your actual two-factor code.
```

Note, that the two-factor code is being changed every 30 seconds, so you need to ensure that you pass the correct code when calling the `login` method. If you don't pass the code, the login will fail.  
Keep in mind, that the session cookie has it's own expiration time, so you may need to call the `login` method again after some time while providing the new two-factor code. So, it's recommended to have some sort of automation to retrieve the valid two-factor code from time to time.  

ℹ️ As an example of solution to automate the two-factor code retrieval, you can use the [`pyotp`](https://github.com/pyauth/pyotp) library to generate the code based on your secret key.

## Examples

Large examples were moved to GitBook docs to keep README focused while preserving all advanced usage.

- Advanced snippets: https://py3xui.gitbook.io/py3xui-docs/examples/advanced-snippets
- Common tasks: https://py3xui.gitbook.io/py3xui-docs/examples/common-tasks
- Sync recipes: https://py3xui.gitbook.io/py3xui-docs/examples/sync-recipes
- Async recipes: https://py3xui.gitbook.io/py3xui-docs/examples/async-recipes

### Get inbounds list
```python
from typing import List
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
import uuid
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
