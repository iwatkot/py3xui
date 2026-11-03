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

## Clients API models (3x-ui v3.11.0)

- `ClientPage`: result of `get_list_paged`: `items` (`ClientSlim`), `total`, `filtered`, `page`, `page_size`, `summary` (`ClientsSummary`), `groups`.
- `ClientSlim`: compact row without credentials, it can not be passed to `update`.
- `ClientsSummary`: client counters over the whole panel; the email lists stop at 200 entries.
- `ClientTraffic`: traffic counters of a client.
- `ClientRenewalPreview`: result of `get_renewal_preview`.
- `ClientExternalLink`: external link or subscription, argument of `set_external_links`. `ClientDetails.external_links` items can be loaded with `ClientExternalLink.model_validate`.
- `ClientEntry`: `client`, `inbound_ids` and `traffic` (`ClientEntryTraffic`). Returned by `export_clients`, accepted by `import_clients`.
- `BulkResult`: `count` (created, adjusted, deleted or changed clients) and `skipped` (`BulkSkip` with `email` and `reason`).
