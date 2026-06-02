# Architecture

## Layers

1. Base transport layer
- Sync: `requests`
- Async: `httpx`

2. Domain API groups
- inbound, client, server, database

3. Models
- Pydantic model validation and normalization

## Design Priorities

- Keep sync and async APIs consistent.
- Hide endpoint churn behind stable Python methods.
- Fail fast on invalid API responses.
