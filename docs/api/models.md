# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ServerStatus`
- `ServerConfig`

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.

## Inbounds API (3x-ui v3.11.0)

- `InboundOption`: lightweight inbound projection returned by `get_options()`.
- `InboundFallback`: fallback rule of a master inbound, used by `get_fallbacks()` and `set_fallbacks()`.
- `AmneziaWGReadiness`, `AmneziaWGBlocker`: host readiness for kernel-mode AmneziaWG.
- `InboundBulkDeleteResult`, `InboundBulkDeleteReport`: result of `bulk_delete()`.
- `InboundClientsDeleteResult`, `InboundClientsDeleteReport`: result of `delete_all_clients()`.
