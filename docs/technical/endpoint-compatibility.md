# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Sub Balancers API (3x-ui v3.11.0)

- `GET panel/api/sub-balancers`
- `POST panel/api/sub-balancers`
- `POST panel/api/sub-balancers/{id}`
- `POST panel/api/sub-balancers/{id}/del`

Create and update read form fields only: `inboundIds` as repeated keys and `memberWeights` as one JSON object. JSON bodies lose `inboundIds` and are rejected. `DELETE panel/api/sub-balancers/{id}` has the same handler as the POST alias, and py3xui uses the alias.
