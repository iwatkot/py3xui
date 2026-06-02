# Synchronous Recipes

## Minimal Script

```python
from py3xui import Api

api = Api.from_env()
api.login()
print(api.server.get_status())
```

## Token-Based Auth Script

```python
from py3xui import Api

api = Api("http://your-host:2053", token="your-token")
print(api.client.online())
```

## TLS with Custom Certificate

```python
from py3xui import Api

api = Api(
    "https://your-host:2053",
    "username",
    "password",
    custom_certificate_path="/path/to/ca.pem",
)
api.login()
print(api.server.get_status())
```

## Safe Client Lookup

```python
email = "user@example.com"
client = api.client.get_by_email(email)

if client is None:
    print("Client not found")
else:
    print("Found:", client.email)
```
