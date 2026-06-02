# Testing and Quality

## Local Checks

```bash
pytest
mypy py3xui
pylint py3xui
```

## Strategy

- Unit tests cover sync and async API behavior.
- Type checks prevent shape and contract regressions.
- Linting enforces style and consistency.
- Live panel validation is used before compatibility releases.
