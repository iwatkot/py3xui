# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ServerStatus`
- `ServerConfig`

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.

## Server API (3x-ui v3.11.0)

Models in `py3xui.server`:

- `Fail2banStatus`, `HistoryPoint`, `CpuHistoryPoint`, `XrayMetricsState`, `ObservatorySnapshot`
- `PanelUpdateInfo`, `PanelUpdateStatus`
