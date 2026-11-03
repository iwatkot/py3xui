# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Nodes API (3x-ui v3.11.0)

All 16 `panel/api/nodes/*` routes are covered by `api.node` in both clients. All bodies are JSON.

- `update` sends the whole node, because the panel replaces it. An omitted `apiToken` keeps the stored token.
- `add`, `update`, `test`, `certFingerprint` and `inbounds` share one request contract: `name`, `address` and `port` are required by the panel on all of them.
- `get_history` accepts the metrics `cpu`, `mem`, `netUp`, `netDown` and the buckets 2, 30, 60, 180, 360, 720, 1440, 2880, 10080, as validated by the panel. The OpenAPI description of this route lists fewer metrics and different buckets.
