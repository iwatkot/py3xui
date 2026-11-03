# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ClientDetails`
- `ServerStatus`
- `ServerConfig`

`Client` keeps fields it does not declare (`extra="allow"`) and returns them from `model_dump()`.
The panel replaces a client on `clients/update/{email}`, so dropping unknown fields on read would
erase them on the next update. `Client` also accepts the client record shape returned by
`clients/get/{email}`: `allowedIPs` as a comma-separated string, `createdAt` / `updatedAt`, and the
UUID in `uuid` while `id` holds the record ID.

`ClientDetails` is the full `clients/get/{email}` payload: `client`, `inbound_ids`,
`external_links`, `used_traffic` and `tunnel_allowed_ips`.

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.
