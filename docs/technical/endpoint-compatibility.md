# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Xray API (3x-ui v3.11.0)

- `POST xray/` returns its payload as a JSON string in `obj`; `get_settings()` parses it into `XraySettings`.
- `xray/update` replaces the outbound test URL on every call: when `outboundTestUrl` is absent the panel resets it to the default one.
- `update()` and the outbound test methods take the Xray JSON as a string, exactly as the form fields expect it.
