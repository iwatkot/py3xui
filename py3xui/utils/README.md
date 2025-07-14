<a id="utils.env"></a>

# utils.env

This module contains utility functions for parsing environment variables.

<a id="utils.env.parse_env"></a>

#### parse\_env

```python
def parse_env(keys: list[str],
              postprocess_fn: Callable[[str], Any],
              raise_if_not_found: bool = True) -> Any
```

Parse the environment for the first key that is found and return the value after
postprocessing it.

**Arguments**:

- `keys` _list[str]_ - The keys to search for in the environment.
- `postprocess_fn` _Callable[[str], Any]_ - The postprocessing function to apply to the value.
- `raise_if_not_found` _bool_ - Whether to raise an error if the environment
  variable is not found. Defaults to True.
  

**Raises**:

- `ValueError` - If none of the keys are found in the environment and raise_if_not_found is True.
  

**Returns**:

  Any | None: The postprocessed value or None.

<a id="utils.env.xui_host"></a>

#### xui\_host

```python
def xui_host() -> str
```

Get the XUI host from the environment using the following keys:
- XUI_HOST

**Raises**:

- `ValueError` - If none of the keys are found in the environment
  

**Returns**:

  str | None: The XUI host or None

<a id="utils.env.xui_username"></a>

#### xui\_username

```python
def xui_username() -> str
```

Get the XUI username from the environment using the following keys:
- XUI_USERNAME

**Raises**:

- `ValueError` - If none of the keys are found in the environment
  

**Returns**:

  str | None: The XUI username or None

<a id="utils.env.xui_password"></a>

#### xui\_password

```python
def xui_password() -> str
```

Get the XUI password from the environment using the following keys:
- XUI_PASSWORD

**Raises**:

- `ValueError` - If none of the keys are found in the environment
  

**Returns**:

  str | None: The XUI password or None

<a id="utils.env.tls_verify"></a>

#### tls\_verify

```python
def tls_verify() -> bool | None
```

Get the TLS verification setting from the environment using the following keys:
- TLS_VERIFY

**Returns**:

  bool | None: True if verification is required, False otherwise, or None if not set.

<a id="utils.env.tls_cert_path"></a>

#### tls\_cert\_path

```python
def tls_cert_path() -> str | None
```

Get the path to the TLS certificate from the environment using the following keys:
- TLS_CERT_PATH

**Returns**:

  str | None: The path to the TLS certificate file, or None if not set.

<a id="utils.logger"></a>

# utils.logger

This module contains dummy logging class if the logger was not set in API.

