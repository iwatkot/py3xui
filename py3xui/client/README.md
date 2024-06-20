<a id="client.client"></a>

# client.client

This module contains the Client class which represents a client in the XUI API.

<a id="client.client.ClientFields"></a>

## ClientFields Objects

```python
class ClientFields()
```

Stores the fields returned by the XUI API for parsing.

<a id="client.client.Client"></a>

## Client Objects

```python
class Client(BaseModel)
```

Represents a client in the XUI API.

**Attributes**:

- `email` _str_ - The email of the client. Required.
- `enable` _bool_ - Whether the client is enabled. Required.
- `id` _int | str_ - The ID of the client. Required.
- `inbound_id` _int | None_ - The ID of the inbound connection. Optional.
- `up` _int_ - The upload speed of the client. Optional.
- `down` _int_ - The download speed of the client. Optional.
- `expiry_time` _int_ - The expiry time of the client. Optional.
- `total` _int_ - The total amount of data transferred by the client. Optional.
- `reset` _int_ - The time at which the client's data was last reset. Optional.
- `flow` _str_ - The flow of the client. Optional.
- `limit_ip` _int_ - The limit of IPs for the client. Optional.
- `sub_id` _str_ - The sub ID of the client. Optional.
- `tg_id` _str_ - The Telegram ID of the client. Optional.
- `total_gb` _int_ - The total amount of data transferred by the client in GB. Optional.

<a id="client.client.Client.inbound_id"></a>

#### inbound\_id

type: ignore

<a id="client.client.Client.expiry_time"></a>

#### expiry\_time

type: ignore

<a id="client.client.Client.limit_ip"></a>

#### limit\_ip

type: ignore

<a id="client.client.Client.sub_id"></a>

#### sub\_id

type: ignore

<a id="client.client.Client.tg_id"></a>

#### tg\_id

type: ignore

<a id="client.client.Client.total_gb"></a>

#### total\_gb

type: ignore

