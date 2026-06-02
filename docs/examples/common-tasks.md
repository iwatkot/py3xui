# Common Tasks

## List Inbounds

```python
from py3xui import Api

api = Api.from_env()
api.login()

for inbound in api.inbound.get_list():
    print(inbound.id, inbound.remark, inbound.protocol)
```

## Create and Update a Client

```python
from uuid import uuid4
from py3xui import Api, Client

api = Api.from_env()
api.login()

inbound_id = 1
email = "client@example.com"

api.client.add(inbound_id, [Client(id=str(uuid4()), email=email, enable=True)])
client = api.client.get_by_email(email)

if client:
    client.total_gb = 5 * 1024 * 1024 * 1024
    api.client.update(str(client.id), client)
```

## Reset and Delete Client

```python
api.client.reset_ips(email)
api.client.reset_stats(inbound_id, email)

client = api.client.get_by_email(email)
api.client.delete(inbound_id, str(client.id) if client else email)
```

## Export Database Backup

```python
api.database.export()
```

## Check Server Status and Config

```python
status = api.server.get_status()
config = api.server.get_server_config()

print(status.cpu)
print(len(config.inbounds))
```
