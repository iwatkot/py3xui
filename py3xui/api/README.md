<a id="api.api"></a>

# api.api

This module provides classes to interact with the XUI API.

<a id="api.api.Api"></a>

## Api Objects

```python
class Api()
```

This class provides a high-level interface to interact with the XUI API.
Access to the client, inbound, and database APIs is provided through this class.

**Arguments**:

- `host` _str_ - The XUI host URL.
- `username` _str_ - The XUI username.
- `password` _str_ - The XUI password.
- `logger` _Any | None_ - The logger, if not set, a dummy logger is used.
  
  Attributes and Properties:
- `client` _ClientApi_ - The client API.
- `inbound` _InboundApi_ - The inbound API.
- `database` _DatabaseApi_ - The database API.
- `session` _str_ - The session cookie for the XUI API.
  
  Public Methods:
- `login` - Logs into the XUI API.
- `from_env` - Creates an instance of the API from environment variables.
  

**Examples**:

    ```python
    import py3xui

    # It's recommended to use environment variables for the credentials.
    os.environ["XUI_HOST"] = "https://xui.example.com"
    os.environ["XUI_USERNAME"] = "username"
    os.environ["XUI_PASSWORD"] = "password"

    api = py3xui.Api.from_env()

    # Alternatively, you can provide the credentials directly.
    api = py3xui.Api("https://xui.example.com", "username", "password")

    api.login()

    # Some examples of using the API.
    inbounds: list[py3xui.Inbound] = api.inbound.get_list()
    client: py3xui.Client = api.client.get_by_email("email")
    ```

<a id="api.api.Api.session"></a>

#### session

```python
@property
def session() -> str | None
```

The session cookie for the XUI API.

**Returns**:

- `str` - The session cookie for the XUI API.

<a id="api.api.Api.from_env"></a>

#### from\_env

```python
@classmethod
def from_env(cls, logger: Any | None = None) -> Api
```

Creates an instance of the API from environment variables.
Following environment variables should be set:
- XUI_HOST: The XUI host URL.
- XUI_USERNAME: The XUI username.
- XUI_PASSWORD: The XUI password.

**Arguments**:

- `logger` _Any | None_ - The logger, if not set, a dummy logger is used.
  

**Returns**:

- `Api` - The API instance.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    ```

<a id="api.api.Api.login"></a>

#### login

```python
def login() -> None
```

Logs into the XUI API and sets the session cookie for the client, inbound, and
database APIs.

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    ```

<a id="api.api_base"></a>

# api.api\_base

This module contains the base class for the XUI API.

<a id="api.api_base.ApiFields"></a>

## ApiFields Objects

```python
class ApiFields()
```

Stores the fields returned by the XUI API for parsing.

<a id="api.api_base.BaseApi"></a>

## BaseApi Objects

```python
class BaseApi()
```

Base class for the XUI API. Contains common methods for making requests.

**Arguments**:

- `host` _str_ - The host of the XUI API.
- `username` _str_ - The username for the XUI API.
- `password` _str_ - The password for the XUI API.
- `logger` _Any | None_ - The logger, if not set, a dummy logger is used.
  
  Attributes and Properties:
- `host` _str_ - The host of the XUI API.
- `username` _str_ - The username for the XUI API.
- `password` _str_ - The password for the XUI API.
- `max_retries` _int_ - The maximum number of retries for a request.
- `session` _str_ - The session cookie for the XUI API.
  
  Public Methods:
- `login` - Logs into the XUI API.
  
  Private Methods:
- `_check_response` - Checks the response from the XUI API.
- `_url` - Returns the URL for the XUI API.
- `_request_with_retry` - Makes a request to the XUI API with retries.
- `_post` - Makes a POST request to the XUI API.
- `_get` - Makes a GET request to the XUI API.

<a id="api.api_base.BaseApi.host"></a>

#### host

```python
@property
def host() -> str
```

The host of the XUI API.

**Returns**:

- `str` - The host of the XUI API.

<a id="api.api_base.BaseApi.username"></a>

#### username

```python
@property
def username() -> str
```

The username for the XUI API.

**Returns**:

- `str` - The username for the XUI API.

<a id="api.api_base.BaseApi.password"></a>

#### password

```python
@property
def password() -> str
```

The password for the XUI API.

**Returns**:

- `str` - The password for the XUI API.

<a id="api.api_base.BaseApi.max_retries"></a>

#### max\_retries

```python
@property
def max_retries() -> int
```

The maximum number of retries for a request.

**Returns**:

- `int` - The maximum number of retries for a request.

<a id="api.api_base.BaseApi.max_retries"></a>

#### max\_retries

```python
@max_retries.setter
def max_retries(value: int) -> None
```

Sets the maximum number of retries for a request.

**Arguments**:

- `value` _int_ - The maximum number of retries for a request.

<a id="api.api_base.BaseApi.session"></a>

#### session

```python
@property
def session() -> str | None
```

The session cookie for the XUI API.

**Returns**:

  str | None: The session cookie for the XUI API.

<a id="api.api_base.BaseApi.session"></a>

#### session

```python
@session.setter
def session(value: str | None) -> None
```

Sets the session cookie for the XUI API.

**Arguments**:

- `value` _str | None_ - The session cookie for the XUI API.

<a id="api.api_base.BaseApi.login"></a>

#### login

```python
def login() -> None
```

Logs into the XUI API and sets the session cookie if successful.

**Raises**:

- `ValueError` - If the login is unsuccessful.

<a id="api.api_client"></a>

# api.api\_client

This module contains the ClientApi class which provides methods to interact with the
clients in the XUI API.

<a id="api.api_client.ClientApi"></a>

## ClientApi Objects

```python
class ClientApi(BaseApi)
```

This class provides methods to interact with the clients in the XUI API.

Attributes and Properties:
host (str): The XUI host URL.
username (str): The XUI username.
password (str): The XUI password.
session (requests.Session): The session object for the API.
max_retries (int): The maximum number of retries for the API requests.

Public Methods:
get_by_email: Retrieves a client by email.
get_ips: Retrieves the IPs associated with a client.
add: Adds clients to an inbound.
update: Updates a client.
reset_ips: Resets the IPs associated with a client.
reset_stats: Resets the statistics of a client.
delete: Deletes a client.
delete_depleted: Deletes depleted clients.
online: Retrieves online clients.

**Examples**:

    ```python
    import uuid
    import py3xui

    api = py3xui.Api.from_env()
    api.login()

    client: py3xui.Client = api.client.get_by_email("email")

    new_client = py3xui.Client(id=new_uuid, email="test", enable=True)
    inbound_id = 1
    api.client.add(inbound_id, [new_client])
    ```

<a id="api.api_client.ClientApi.get_by_email"></a>

#### get\_by\_email

```python
def get_by_email(email: str) -> Client | None
```

This route is used to retrieve information about a specific client based on their email.
This endpoint provides details such as traffic statistics and other relevant information
related to the client.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9d0e5cd5-e6ac-4d72-abca-76cf75af5f00)

**Arguments**:

- `email` _str_ - The email of the client to retrieve.
  

**Returns**:

  Client | None: The client object if found, otherwise None.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    client: py3xui.Client = api.client.get_by_email("email")
    ```

<a id="api.api_client.ClientApi.get_ips"></a>

#### get\_ips

```python
def get_ips(email: str) -> list[str]
```

This route is used to retrieve the IP records associated with a specific client
identified by their email.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#06f1214c-dbb0-49f2-81b5-8e924abd19a9)

**Arguments**:

- `email` _str_ - The email of the client to retrieve.
  

**Returns**:

- `list[str]` - The list of IP records associated with the client.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    ips = api.client.get_ips("email")
    ```

<a id="api.api_client.ClientApi.add"></a>

#### add

```python
def add(inbound_id: int, clients: list[Client])
```

This route is used to add a new clients to a specific inbound identified by its ID.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#c4d325ae-fbb4-44e9-bd2e-29eebb7fbc52)

**Arguments**:

- `inbound_id` _int_ - The ID of the inbound to add the clients to.
- `clients` _list[Client]_ - The list of clients to add.
  

**Examples**:

    ```python
    import uuid
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    new_client = py3xui.Client(id=str(uuid.uuid4()), email="test", enable=True)
    inbound_id = 1

    api.client.add(inbound_id, [new_client])

<a id="api.api_client.ClientApi.update"></a>

#### update

```python
def update(client_uuid: str, client: Client) -> None
```

This route is used to update an existing client identified by its UUID within a specific
inbound.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#af1bee51-199c-4176-b3ab-d325ba2fae19)

**Arguments**:

- `client_uuid` _str_ - The UUID of the client to update.
- `client` _Client_ - The client object with updated information.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    client = api.client.get_by_email("email")
    client.email = "newemail"
    api.client.update(client.id, client)
    ```

<a id="api.api_client.ClientApi.reset_ips"></a>

#### reset\_ips

```python
def reset_ips(email: str) -> None
```

This route is used to reset or clear the IP records associated with a specific client
identified by their email address.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#7af93bc4-693a-4fa4-8560-0642783af6f3)

**Arguments**:

- `email` _str_ - The email of the client to reset the IPs for.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    api.client.reset_ips("email")
    ```

<a id="api.api_client.ClientApi.reset_stats"></a>

#### reset\_stats

```python
def reset_stats(inbound_id: int, email: str) -> None
```

This route is used to reset the traffic statistics for a specific client identified by
their email address  within a particular inbound identified by its ID.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#52081826-8e06-4dc1-9bad-8a95f1cd8a96)

**Arguments**:

- `inbound_id` _int_ - The ID of the inbound to reset the client stats.
- `email` _str_ - The email of the client to reset the stats for.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    inbound_id = 1

    api.client.reset_stats(inbound_id, "test")
    ```

<a id="api.api_client.ClientApi.delete"></a>

#### delete

```python
def delete(inbound_id: int, client_uuid: str) -> None
```

This route is used to delete a client identified by its UUID within a specific inbound
identified by its ID.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#97aa9d0e-9cc3-46db-a364-c2fda39586bd)

**Arguments**:

- `inbound_id` _int_ - The ID of the inbound to delete the client from.
- `client_uuid` _str_ - The UUID of the client to delete.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    client = api.client.get_by_email("email")
    inbound_id = 1

    api.client.delete(inbound_id, client.id)
    ```

<a id="api.api_client.ClientApi.delete_depleted"></a>

#### delete\_depleted

```python
def delete_depleted(inbound_id: int) -> None
```

This route is used to delete all depleted clients associated with a specific inbound
identified by its ID.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#8f4975c9-1051-43cb-afa7-c42ca2542c6b)

**Arguments**:

- `inbound_id` _int_ - The ID of the inbound to delete the depleted clients from.
  

**Examples**:

  
    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    inbounds: list[py3xui.Inbound] = api.inbound.get_list()

    for inbound in inbounds:
        api.client.delete_depleted(inbound.id)
    ```

<a id="api.api_client.ClientApi.online"></a>

#### online

```python
def online() -> list[str]
```

Returns a list of email addresses of online clients.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9cac8101-017e-4415-94e2-d30f4dcf49de)

**Returns**:

- `list[str]` - The list of email addresses of online clients.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    res = api.client.online()
    print(res)
    ```

<a id="api.api_client.ClientApi.get_traffic_by_id"></a>

#### get\_traffic\_by\_id

```python
def get_traffic_by_id(client_uuid: int) -> list[Client]
```

This route is used to retrieve information about a specific client based on their UUID.

NOTE: At the moment of writing this, the API documentation does not exist for this route.

**Arguments**:

- `client_uuid` _int_ - The UUID of the client to retrieve.
  

**Returns**:

- `list[Client]` - The list of clients.
  

**Examples**:

  
    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()

    clients = api.client.get_traffic_by_id("239708ef-487e-4945-829d-ad79a0ce067e")
    print(clients)
    ```

<a id="api.api_database"></a>

# api.api\_database

This module contains the DatabaseApi class, which is responsible handling database operations
in the XUI API.

<a id="api.api_database.DatabaseApi"></a>

## DatabaseApi Objects

```python
class DatabaseApi(BaseApi)
```

This class provides methods to interact with the database in the XUI API.

Attributes and Properties:
host (str): The XUI host URL.
username (str): The XUI username.
password (str): The XUI password.
session (requests.Session): The session object for the API.
max_retries (int): The maximum number of retries for the API requests.

Public Methods:
export: Exports the database.

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    api.database.export()
    ```

<a id="api.api_database.DatabaseApi.export"></a>

#### export

```python
def export() -> None
```

This endpoint triggers the creation of a system backup and initiates the delivery of
the backup file to designated administrators via a configured Telegram bot. The server
verifies the Telegram bot's activation status within the system settings and checks for
the presence of admin IDs specified in the settings before sending the backup.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#5368cbc0-7c84-4b8c-aa54-d9fffb24d1f2)

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    api.database.export()
    ```

<a id="api.api_inbound"></a>

# api.api\_inbound

This module contains the InboundApi class for handling inbounds in the XUI API.

<a id="api.api_inbound.InboundApi"></a>

## InboundApi Objects

```python
class InboundApi(BaseApi)
```

This class provides methods to interact with the inbounds in the XUI API.

Attributes and Properties:
host (str): The XUI host URL.
username (str): The XUI username.
password (str): The XUI password.
session (requests.Session): The session object for the API.
max_retries (int): The maximum number of retries for the API requests.

Public Methods:
get_list: Retrieves a list of inbounds.
add: Adds a new inbound.
delete: Deletes an inbound.
update: Updates an inbound.
reset_stats: Resets the statistics of all inbounds.
reset_client_stats: Resets the statistics of a specific inbound.

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()

    inbounds: list[py3xui.Inbound] = api.inbound.get_list()
    ```

<a id="api.api_inbound.InboundApi.get_list"></a>

#### get\_list

```python
def get_list() -> list[Inbound]
```

This route is used to retrieve a comprehensive list of all inbounds along with
their associated client options and statistics.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#b7c42b67-4362-44d3-bd61-ba7df0721802)

**Returns**:

- `list[Inbound]` - A list of inbounds.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()

    inbounds: list[py3xui.Inbound] = api.inbound.get_list()
    ```

<a id="api.api_inbound.InboundApi.add"></a>

#### add

```python
def add(inbound: Inbound) -> None
```

This route is used to add a new inbound configuration.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#813ac729-5ba6-4314-bc2a-d0d3acc70388)

**Arguments**:

- `inbound` _Inbound_ - The inbound object to add.
  

**Examples**:

    ```python
    import py3xui
    from py3xui.inbound import Inbound, Settings, Sniffing, StreamSettings

    api = py3xui.Api.from_env()
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

<a id="api.api_inbound.InboundApi.delete"></a>

#### delete

```python
def delete(inbound_id: int) -> None
```

This route is used to delete an inbound identified by its ID.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#a655d0e3-7d8c-4331-9061-422fcb515da9)

**Arguments**:

- `inbound_id` _int_ - The ID of the inbound to delete.
  

**Examples**:

  
    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    inbounds: list[py3xui.Inbound] = api.inbound.get_list()

    for inbound in inbounds:
        api.inbound.delete(inbound.id)
    ```

<a id="api.api_inbound.InboundApi.update"></a>

#### update

```python
def update(inbound_id: int, inbound: Inbound) -> None
```

This route is used to update an existing inbound identified by its ID.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#19249b9f-a940-41e2-8bf4-86ff8dde857e)

**Arguments**:

- `inbound_id` _int_ - The ID of the inbound to update.
- `inbound` _Inbound_ - The inbound object to update.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    inbounds: list[py3xui.Inbound] = api.inbound.get_list()
    inbound = inbounds[0]

    inbound.remark = "updated"

    api.inbound.update(inbound.id, inbound)
    ```

<a id="api.api_inbound.InboundApi.reset_stats"></a>

#### reset\_stats

```python
def reset_stats() -> None
```

This route is used to reset the traffic statistics for all inbounds within the system.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#6749f362-dc81-4769-8f45-37dc9e99f5e9)

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    api.inbound.reset_stats()
    ```

<a id="api.api_inbound.InboundApi.reset_client_stats"></a>

#### reset\_client\_stats

```python
def reset_client_stats(inbound_id: int) -> None
```

This route is used to reset the traffic statistics for all clients associated with a
specific inbound identified by its ID.

[Source documentation](https://documenter.getpostman.com/view/16802678/2s9YkgD5jm#9bd93925-12a0-40d8-a390-d4874dea3683)

**Arguments**:

- `inbound_id` _int_ - The ID of the inbound to reset the client stats.
  

**Examples**:

    ```python
    import py3xui

    api = py3xui.Api.from_env()
    api.login()
    inbounds: list[py3xui.Inbound] = api.inbound.get_list()
    inbound = inbounds[0]

    api.inbound.reset_client_stats(inbound.id)
    ```

