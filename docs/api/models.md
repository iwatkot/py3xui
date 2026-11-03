# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ServerStatus`
- `ServerConfig`

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.

## Nodes API (3x-ui v3.11.0)

- `Node`: a remote panel, used for reads and writes. Unknown fields are kept and sent back on update. `api_token` is write-only: `None` keeps the stored token, `clear_api_token=True` removes it. A `null` `inboundTags` from the panel is parsed as an empty list.
- `NodeProbeResult`: result of `test()` and `probe()`. An unreachable node has the `offline` status and the reason in `error`, it does not raise.
- `NodeUpdateResult`: per-node result of `update_panel()`.
- `NodeRemoteInbound`: an inbound returned by `get_remote_inbounds()`.
- `NodeWebCertFiles`: result of `get_web_cert_files()`.
- `NodeHistoryPoint`: a point of `get_history()`.
