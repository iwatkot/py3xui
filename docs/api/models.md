# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ServerStatus`
- `ServerConfig`

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.

## Xray API (3x-ui v3.11.0)

Models of `api.xray`, exported from `py3xui`:

- `XraySettings`, `GeodataSource`, `OutboundTraffic`
- `PiaAccount`, `PiaCountry`, `PiaRegion`, `PiaServer`, `PiaServers`, `PiaKey`
- `OutboundTestResult`, `OutboundTestEndpoint`, `OutboundTestEgress`, `BalancerStatus`, `RouteTestResult`
- `GeoFile`, `GeoCategory`, `GeoCategoryPage`, `GeoEntry`, `GeoEntryPage`, `GeodataTokenIssue`
