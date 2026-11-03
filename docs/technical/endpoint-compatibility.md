# Endpoint Compatibility

3x-ui endpoint naming changed in modern v3 builds, especially for client operations.

The 0.7.0 line aligns client routes to `panel/api/clients/*` and keeps compatibility wrappers in Python method signatures where feasible.

Examples:
- Add client: `panel/api/clients/add`
- Update client: `panel/api/clients/update/{email}`
- Online clients: `panel/api/clients/onlines`

Compatibility behavior is implemented in both sync and async clients.

## Hosts API (3x-ui v3.11.0)

| Endpoint | Method |
|---|---|
| `GET panel/api/hosts/list` | `api.host.get_list()` |
| `GET panel/api/hosts/raw` | `api.host.get_raw_list()` |
| `GET panel/api/hosts/get/{groupId}` | `api.host.get_by_id(group_id)` |
| `GET panel/api/hosts/byInbound/{inboundId}` | `api.host.get_by_inbound(inbound_id)` |
| `GET panel/api/hosts/tags` | `api.host.get_tags()` |
| `POST panel/api/hosts/add` | `api.host.add(host)` |
| `POST panel/api/hosts/update/{groupId}` | `api.host.update(group_id, host)` |
| `POST panel/api/hosts/del/{groupId}` | `api.host.delete(group_id)` |
| `POST panel/api/hosts/setEnable/{groupId}` | `api.host.set_enable(group_id, enable)` |
| `POST panel/api/hosts/reorder` | `api.host.reorder(group_ids)` |
| `POST panel/api/hosts/bulk/add` | `api.host.bulk_add(host)` |
| `POST panel/api/hosts/bulk/setEnable` | `api.host.bulk_set_enable(group_ids, enable)` |
| `POST panel/api/hosts/bulk/del` | `api.host.bulk_delete(group_ids)` |
