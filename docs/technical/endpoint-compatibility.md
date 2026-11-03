# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Settings API (3x-ui v3.11.0)

Sync and async `api.setting` use JSON bodies on these routes:

- `POST panel/api/setting/all`, `defaultSettings`, `factoryDefaults`, `update`, `validateRegex`, `updateUser`, `restartPanel`
- `POST panel/api/setting/testSmtp`, `testTgBot`, `tgBotCapabilities`, `testDiscord`
- `GET panel/api/setting/getDefaultJsonConfig`, `apiTokens`
- `POST panel/api/setting/apiTokens/create`, `apiTokens/delete/{id}`, `apiTokens/setEnabled/{id}`

`testSmtp` adds a `stage` field to the response, so `test_smtp()` returns it instead of raising on failure.
