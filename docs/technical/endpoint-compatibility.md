# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Inbounds API (3x-ui v3.11.0)

- `GET panel/api/inbounds/list/slim`
- `GET panel/api/inbounds/options`
- `GET panel/api/inbounds/amneziawgKernelReadiness`
- `GET panel/api/inbounds/allLinks`
- `POST panel/api/inbounds/bulkDel`
- `POST panel/api/inbounds/setEnable/{id}`
- `POST panel/api/inbounds/{id}/subSortIndex`
- `POST panel/api/inbounds/{id}/resetTraffic`
- `POST panel/api/inbounds/{id}/delAllClients`
- `POST panel/api/inbounds/import` (form field `data` with the inbound JSON)
- `POST panel/api/inbounds/pushClientTraffics`
- `GET panel/api/inbounds/{id}/fallbacks`
- `POST panel/api/inbounds/{id}/fallbacks`
