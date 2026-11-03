# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Client details: `panel/api/clients/get/{email}` (`get_details`, full payload; `get_by_email` keeps the 0.7.0 shape)
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Clients API (3x-ui v3.11.0)

- `GET panel/api/clients/list/paged`: `get_list_paged`
- `GET panel/api/clients/get/subId/{subId}`: `get_details_by_sub_id`
- `GET panel/api/clients/get/tgId/{tgId}`: `get_details_by_tg_id`
- `POST panel/api/clients/renewalPreview`: `get_renewal_preview`
- `GET panel/api/clients/traffic/{email}`: `get_traffic`
- `GET panel/api/clients/subLinks/{subId}`: `get_sub_links`
- `GET panel/api/clients/links/{email}`: `get_links`
- `POST panel/api/clients/happLink/{id}`: `get_happ_link`
