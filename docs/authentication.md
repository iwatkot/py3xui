# Authentication

py3xui supports two auth modes.

## Username and Password

Use `login()` after creating the API instance.

```python
from py3xui import Api

api = Api("http://your-host:2053", "username", "password")
api.login()
```

## Token Authentication

If your panel exposes token auth, pass `token` and skip `login()`.

```python
from py3xui import Api

api = Api("http://your-host:2053", token="your-token")
```

## TLS Notes

- Keep `use_tls_verify=True` in production.
- Use `custom_certificate_path` for self-signed or private CA certificates.
