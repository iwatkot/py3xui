<a id="inbound.bases"></a>

# inbound.bases

This module contains the base classes for the inbound models.

<a id="inbound.bases.JsonStringModel"></a>

## JsonStringModel Objects

```python
class JsonStringModel(BaseModel)
```

Base class for models that have a JSON string as a field.

<a id="inbound.bases.JsonStringModel.model_validate"></a>

#### model\_validate

```python
@model_validator(mode="before")
def model_validate(cls, values)
```

Converts the JSON string to a dictionary if it is a string.

**Arguments**:

- `values` _Any_ - The values to validate.
  

**Returns**:

- `Any` - The validated values.

<a id="inbound.inbound"></a>

# inbound.inbound

This module contains the Inbound class, which represents an inbound connection in the XUI API.

<a id="inbound.inbound.InboundFields"></a>

## InboundFields Objects

```python
class InboundFields()
```

Stores the fields returned by the XUI API for parsing.

<a id="inbound.inbound.Inbound"></a>

## Inbound Objects

```python
class Inbound(BaseModel)
```

Represents an inbound connection in the XUI API.

**Attributes**:

- `enable` _bool_ - Whether the inbound connection is enabled. Required.
- `port` _int_ - The port number for the inbound connection. Required.
- `protocol` _str_ - The protocol for the inbound connection. Required.
- `settings` _Settings_ - The settings for the inbound connection. Required.
- `stream_settings` _StreamSettings_ - The stream settings for the inbound connection. Required.
- `sniffing` _Sniffing_ - The sniffing settings for the inbound connection. Required.
- `listen` _str_ - The listen address for the inbound connection. Optional.
- `remark` _str_ - The remark for the inbound connection. Optional.
- `id` _int_ - The ID of the inbound connection. Optional.
- `up` _int_ - The up value for the inbound connection. Optional.
- `down` _int_ - The down value for the inbound connection. Optional.
- `total` _int_ - The total value for the inbound connection. Optional.
- `expiry_time` _int_ - The expiry time for the inbound connection. Optional.
- `client_stats` _list[Client]_ - The client stats for the inbound connection. Optional.
- `tag` _str_ - The tag for the inbound connection. Optional.

<a id="inbound.inbound.Inbound.stream_settings"></a>

#### stream\_settings

type: ignore

<a id="inbound.inbound.Inbound.expiry_time"></a>

#### expiry\_time

type: ignore

<a id="inbound.inbound.Inbound.to_json"></a>

#### to\_json

```python
def to_json() -> dict[str, Any]
```

Converts the Inbound instance to a JSON-compatible dictionary for the XUI API.

**Returns**:

  dict[str, Any]: The JSON-compatible dictionary.

<a id="inbound.settings"></a>

# inbound.settings

This module contains the Settings class, which is used to parse the JSON response
from the XUI API.

<a id="inbound.settings.SettingsFields"></a>

## SettingsFields Objects

```python
class SettingsFields()
```

Stores the fields returned by the XUI API for parsing.

<a id="inbound.settings.Settings"></a>

## Settings Objects

```python
class Settings(JsonStringModel)
```

Represents the settings for an inbound connection.

**Attributes**:

- `clients` _list[Client]_ - The clients for the inbound connection. Optional.
- `decryption` _str_ - The decryption method for the inbound connection. Optional.
- `fallbacks` _list_ - The fallbacks for the inbound connection. Optional.

<a id="inbound.sniffing"></a>

# inbound.sniffing

This module contains the Sniffing class for parsing the XUI API response.

<a id="inbound.sniffing.SniffingFields"></a>

## SniffingFields Objects

```python
class SniffingFields()
```

Stores the fields returned by the XUI API for parsing.

<a id="inbound.sniffing.Sniffing"></a>

## Sniffing Objects

```python
class Sniffing(JsonStringModel)
```

Represents the sniffing settings for an inbound.

**Attributes**:

- `enabled` _bool_ - Whether sniffing is enabled. Required.
- `dest_override` _list[str]_ - The destination override. Optional.
- `metadata_only` _bool_ - Whether to only sniff metadata. Optional.
- `route_only` _bool_ - Whether to only sniff routes. Optional.

<a id="inbound.sniffing.Sniffing.dest_override"></a>

#### dest\_override

type: ignore

<a id="inbound.sniffing.Sniffing.metadata_only"></a>

#### metadata\_only

type: ignore

<a id="inbound.sniffing.Sniffing.route_only"></a>

#### route\_only

type: ignore

<a id="inbound.stream_settings"></a>

# inbound.stream\_settings

This module contains the StreamSettings class for parsing the XUI API response.

<a id="inbound.stream_settings.StreamSettingsFields"></a>

## StreamSettingsFields Objects

```python
class StreamSettingsFields()
```

Stores the fields returned by the XUI API for parsing.

<a id="inbound.stream_settings.StreamSettings"></a>

## StreamSettings Objects

```python
class StreamSettings(JsonStringModel)
```

Represents the stream settings for an inbound.

**Attributes**:

- `security` _str_ - The security for the inbound connection. Required.
- `network` _str_ - The network for the inbound connection. Required.
- `tcp_settings` _dict_ - The TCP settings for the inbound connection. Required.
- `external_proxy` _list_ - The external proxy for the inbound connection. Optional.
- `reality_settings` _dict_ - The reality settings for the inbound connection. Optional.
- `xtls_settings` _dict_ - The xTLS settings for the inbound connection. Optional.
- `tls_settings` _dict_ - The TLS settings for the inbound connection. Optional.

<a id="inbound.stream_settings.StreamSettings.tls_settings"></a>

#### tls\_settings

type: ignore

