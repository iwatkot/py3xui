# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.
