<div align="center" markdown>
<img src="https://github.com/iwatkot/py3xui/assets/118521851/42c5d579-6202-4a9e-88f3-2d844fdd95b6">

Sync and Async Object-oriented Python SDK for the 3x-ui API.

<p align="center">
    <a href="#Overview">Overview</a> •
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
No matter which API you're using or if was it created using environment variables or credentials, you'll need to call the `login` method to authenticate the user and save the cookie for future requests.
```python
from py3xui import Api, AsyncApi

api = Api.from_env()
api.login()

async_api = AsyncApi.from_env()
await async_api.login()
```

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
You'll find detailed docs with usage examples for both APIs and for used models in the corresponding package directories:
- [Synchronous API](py3xui/api/README.md)
- [Asynchronous API](py3xui/async_api/README.md)
- [Client](py3xui/client/README.md)
- [Inbound](py3xui/inbound/README.md)

In this section, you'll find some examples of how to use the SDK. In the examples, we'll use the synchronous API, but you can use the asynchronous API in the same way, just remember to use `await` before calling the methods.<br>

### Set the traffic limit for the client
ℹ️ You'll also find this example in the [demo.py](demo.py) file.

```python
from py3xui import Api

# 1️⃣ Create an instance of the API class.
host = "**************************"
username = "**********"
password = "**********"
api = Api(host, username, password)

# 2️⃣ Login to the API.
api.login()

user_email = "iwatkot"  # ⬅️ Your user email here.
inbound_id = 4  # ⬅️ Your inbound ID here.

# 3️⃣ Get the inbound.
inbound = api.inbound.get_by_id(inbound_id)
print(f"Inbound has {len(inbound.settings.clients)} clients")

# 4️⃣ Find the needed client in the inbound.
client = None
for c in inbound.settings.clients:
    if c.email == user_email:
        client = c
        break

if client:
    print(f"Found client with ID: {client.id}")  # ⬅️ The actual Client UUID.
else:
    raise ValueError(f"Client with email {user_email} not found")

cliend_uuid = client.id

# 5️⃣ Get the client by email.
client_by_email = api.client.get_by_email(user_email)
print(f"Client by email has ID: {client_by_email.id}")  # ⬅️ The numeric ID here.

# 6️⃣ Update the client with needed parameters.
client_by_email.total_gb = 1000 * 1024 * 1024  # ⬅️ Your value here.

# 7️⃣ Update the client ID so it will be UUID, not numeric.
client_by_email.id = cliend_uuid

# 8️⃣ Update the client.
api.client.update(client_by_email.id, client_by_email)
```

### Create a connection string and QR code
When you need to provide the user with a connection string that can be used in a software to create a new connection profile and/or a QR code, you can use the following example.

```python
from py3xui import Inbound

XUI_EXTERNAL_IP = "**********"  # ⬅️ Your external IP here or domain name.
MAIN_REMARK = "gmfvbot"  # ⬅️ It can be any string.
SERVER_PORT = 443  # ⬅️ Your server port here.


def get_connection_string(inbound: Inbound, user_uuid: str, user_email: int) -> str:
    """Prepare a connection string for the given inbound, user UUID and telegram ID.

    Arguments:
        inbound (Inbound): The inbound object.
        user_uuid (str): The UUID of the user.
        user_email (int): The email of the user.

    Returns:
        str: The connection string.
    """
    public_key = inbound.stream_settings.reality_settings.get("settings").get("publicKey")
    website_name = inbound.stream_settings.reality_settings.get("serverNames")[0]
    short_id = inbound.stream_settings.reality_settings.get("shortIds")[0]

    connection_string = (
        f"vless://{user_uuid}@{XUI_EXTERNAL_IP}:{SERVER_PORT}"
        f"?type=tcp&security=reality&pbk={public_key}&fp=firefox&sni={website_name}"
        f"&sid={short_id}&spx=%2F#{MAIN_REMARK}-{user_email}"
    )

    return connection_string
```

And how, when you have the connection string, you can use the `qrcode` library to generate a QR code:

```bash
pip install qrcode
```

```python
import os

import qrcode

# 1️⃣ Obtain the connection string.
user_email = "iwatkot"  # ⬅️ Your user email here.
connection_string = get_connection_string(inbound, "**********", user_email)

# 2️⃣ Create the QR code.
img = qrcode.make(connection_string)

# 3️⃣ Save the QR code to the file.
qrcode_path = os.path.join("qrcodes", f"{user_email}.png")
img.save(qrcode_path)

# Now you can use the `qrcode_path` to send the QR code to the user.
```


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
