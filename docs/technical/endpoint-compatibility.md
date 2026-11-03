# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Server API (3x-ui v3.11.0)

Endpoints used by `api.server`:

- `GET panel/api/server/fail2banStatus`
- `GET panel/api/server/cpuHistory/{bucket}`
- `GET panel/api/server/history/{metric}/{bucket}`
- `GET panel/api/server/xrayMetricsState`
- `GET panel/api/server/xrayMetricsHistory/{metric}/{bucket}`
- `GET panel/api/server/xrayObservatory`
- `GET panel/api/server/xrayObservatoryHistory/{tag}/{bucket}`
