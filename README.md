# py3xui

Python SDK for 3x-ui with synchronous and asynchronous clients.

## Documentation

Project documentation is now maintained in GitBook-ready format under the `docs/` directory.

- Start here: `docs/README.md`
- Table of contents: `docs/SUMMARY.md`
- 0.7.0 release notes: `docs/release-notes/0.7.0.md`

## Install

```bash
pip install py3xui
```

## Quick Example

```python
from py3xui import Api

api = Api("http://your-3x-ui-host:2053", "username", "password")
api.login()
status = api.server.get_status()
print(status)
```

## Development Checks

```bash
pytest
mypy py3xui
pylint py3xui
```
