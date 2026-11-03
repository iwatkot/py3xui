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
- `POST panel/api/clients/{email}/attach`: `attach`
- `POST panel/api/clients/{email}/detach`: `detach`
- `POST panel/api/clients/{email}/externalLinks`: `set_external_links`
- `POST panel/api/clients/delOrphans`: `delete_orphans`
- `GET panel/api/clients/export`: `export_clients`
- `POST panel/api/clients/import`: `import_clients`
- `POST panel/api/clients/bulkAdjust`: `bulk_adjust`
- `POST panel/api/clients/bulkEnable`: `bulk_enable`
- `POST panel/api/clients/bulkDisable`: `bulk_disable`
- `POST panel/api/clients/bulkDel`: `bulk_delete`
- `POST panel/api/clients/bulkCreate`: `bulk_add`
- `POST panel/api/clients/bulkAttach`: `bulk_attach`
- `POST panel/api/clients/bulkDetach`: `bulk_detach`
- `POST panel/api/clients/bulkResetTraffic`: `bulk_reset_stats`
- `GET panel/api/clients/groups`: `get_groups`
- `GET panel/api/clients/groups/{name}/emails`: `get_group_emails`
- `POST panel/api/clients/groups/create`: `add_group`
- `POST panel/api/clients/groups/rename`: `rename_group`
- `POST panel/api/clients/groups/delete`: `delete_group`
- `POST panel/api/clients/groups/resetTraffic`: `reset_group_stats`
- `POST panel/api/clients/groups/bulkAdd`: `bulk_add_to_group`
- `POST panel/api/clients/groups/bulkRemove`: `bulk_remove_from_group`
- `POST panel/api/clients/updateTraffic/{email}`: `update_traffic`
- `POST panel/api/clients/hwids/{email}`: `get_hwids`
- `DELETE panel/api/clients/hwids/{email}`: `delete_hwids`
- `DELETE panel/api/clients/hwids/{email}/{id}`: `delete_hwid`
- `POST panel/api/clients/onlinesByGuid`: `online_by_guid`
- `POST panel/api/clients/clientIpsByGuid`: `get_ips_by_guid`
- `POST panel/api/clients/activeInbounds`: `get_active_inbounds`
- `POST panel/api/clients/lastOnline`: `get_last_online`
