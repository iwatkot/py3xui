# py3xui 0.7.0 Migration Guide

This release updates the SDK to match the 3x-ui v3 client API namespace changes.

## Summary

3x-ui moved client operations from `panel/api/inbounds/*` to `panel/api/clients/*`.

py3xui 0.7.0 updates both sync and async client APIs accordingly.

## Affected SDK Components

- `py3xui/api/api_client.py`
- `py3xui/async_api/async_api_client.py`
- `tests/test_api.py`
- `tests/test_async_api.py`

## Endpoint Migration Map

- `GET panel/api/inbounds/getClientTraffics/{email}` -> `GET panel/api/clients/get/{email}`
- `POST panel/api/inbounds/clientIps/{email}` -> `POST panel/api/clients/ips/{email}`
- `POST panel/api/inbounds/addClient` -> `POST panel/api/clients/add`
- `POST panel/api/inbounds/updateClient/{client_uuid}` -> `POST panel/api/clients/update/{email}`
- `POST panel/api/inbounds/clearClientIps/{email}` -> `POST panel/api/clients/clearIps/{email}`
- `POST panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}` -> `POST panel/api/clients/resetTraffic/{email}`
- `POST panel/api/inbounds/{inbound_id}/delClient/{client_uuid}` -> `POST panel/api/clients/del/{email}`
- `POST panel/api/inbounds/delDepletedClients/{inbound_id}` -> `POST panel/api/clients/delDepleted`
- `POST panel/api/inbounds/onlines` -> `POST panel/api/clients/onlines`
- `GET panel/api/inbounds/getClientTrafficsById/{client_uuid}` -> implemented via `GET panel/api/clients/list` and local filtering by `id`/`uuid`

## API Behavior Changes

### `client.add(inbound_id, clients)`

- Previous: one request with legacy inbound payload.
- New: one request per client to `panel/api/clients/add` with payload:

```json
{
  "client": { "...": "client fields" },
  "inboundIds": [123]
}
```

### `client.update(client_uuid, client)`

- Route now uses email as identifier: `panel/api/clients/update/{email}`.
- SDK keeps the old method signature.
- The `client_uuid` argument is now fallback-only; `client.email` is preferred.

### `client.delete(inbound_id, client_uuid)`

- Route now requires email.
- SDK keeps the old method signature.
- If `client_uuid` is not an email, SDK resolves it by querying `panel/api/clients/list` and matching against `id`/`uuid`.

### `client.reset_stats(inbound_id, email)` and `client.delete_depleted(inbound_id)`

- 3x-ui client routes are now global for these operations.
- SDK keeps `inbound_id` in signatures for backward compatibility, but the server call no longer uses it.

## Compatibility Notes

- Public method names remain unchanged in sync and async APIs.
- Some arguments are now compatibility placeholders because 3x-ui no longer scopes those routes by inbound.
- If your integration depends on strict per-inbound deletion/reset behavior, review workflows against latest 3x-ui semantics.

## Upgrade Checklist

1. Upgrade `py3xui` to 0.7.0.
2. Ensure your panel is a modern 3x-ui v3 build with `/panel/api/clients/*` endpoints.
3. Re-test client create/update/delete flows.
4. If you pass UUID/id to `delete`, verify the target client appears in `clients/list`.
5. Re-run your CI checks.

## Validation Performed

- `pytest`: 75 passed
- `mypy py3xui`: success
- `pylint py3xui`: 10.00/10

## Known Limitation

`get_traffic_by_id` is now implemented by filtering `clients/list` because the old dedicated route is no longer available in latest 3x-ui API docs.
