# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ServerStatus`
- `ServerConfig`

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.

## Hosts API (3x-ui v3.11.0)

- `HostGroup`: the settings of a group plus its `inbound_ids` and `hosts`. Used by `add`, `update` and the read methods of `api.host`.
- `Host`: a single stored row (one per address and inbound) with its numeric `id`, `inbound_id` and `address`. Returned by `get_raw_list`, `add`, `update` and `bulk_add`.

Lists that the panel returns as `null` are parsed as empty lists. Both models keep unknown fields, so they survive a fetch and update round trip.
