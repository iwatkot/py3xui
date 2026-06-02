# Advanced Snippets

These are the larger, end-to-end snippets moved from the repository README.

## Set Traffic Limit for a Client

```python
from py3xui import Api

# 1️⃣ Create an instance of the API class.
host = "**************************"
username = "**********"
password = "**********"
api = Api(host, username, password)

# 2️⃣ Login to the API.
api.login()

user_email = "iwatkot"  # Your user email.
inbound_id = 4  # Your inbound ID.

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
    print(f"Found client with ID: {client.id}")  # The actual Client UUID.
else:
    raise ValueError(f"Client with email {user_email} not found")

client_uuid = client.id

# 5️⃣ Get the client by email.
client_by_email = api.client.get_by_email(user_email)
print(f"Client by email has ID: {client_by_email.id}")  # The numeric ID.

# 6️⃣ Update the client with needed parameters.
client_by_email.total_gb = 1000 * 1024 * 1024

# 7️⃣ Update the client ID so it will be UUID, not numeric.
client_by_email.id = client_uuid

# 8️⃣ Update the client.
api.client.update(client_by_email.id, client_by_email)
```

## Generate Reality Keys

```python
from py3xui import Api

api = Api("https://your-host", "username", "password", use_tls_verify=False)
api.login()

keys = api.server.generate_reality_keys()
print("Public key:", keys.public_key)
print("Private key:", keys.private_key)
```

## Create Connection String and QR Code

```python
from py3xui import Inbound

XUI_EXTERNAL_IP = "**********"  # External IP or domain.
MAIN_REMARK = "gmfvbot"
SERVER_PORT = 443


def get_connection_string(inbound: Inbound, user_uuid: str, user_email: int) -> str:
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

Install QR dependency:

```bash
pip install qrcode
```

Generate and save QR:

```python
import os
import qrcode

user_email = "iwatkot"
connection_string = get_connection_string(inbound, "**********", user_email)

img = qrcode.make(connection_string)
qrcode_path = os.path.join("qrcodes", f"{user_email}.png")
img.save(qrcode_path)
```
