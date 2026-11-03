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
- `GET panel/api/server/getPanelUpdateInfo`
- `GET panel/api/server/getUpdateStatus`
- `POST panel/api/server/updatePanel`
- `POST panel/api/server/setUpdateChannel`
- `POST panel/api/server/stopXrayService`
- `POST panel/api/server/restartXrayService`
- `POST panel/api/server/updateGeofile/{fileName}`
- `GET panel/api/server/getNewUUID`
- `GET panel/api/server/getNewmldsa65`
- `GET panel/api/server/getNewmlkem768`
- `GET panel/api/server/getNewVlessEnc`
- `GET panel/api/server/getWebCertFiles`
- `POST panel/api/server/getNewEchCert`
- `POST panel/api/server/getCertHash`
- `POST panel/api/server/getRemoteCertHash`
- `POST panel/api/server/scanRealityTarget`
- `POST panel/api/server/scanRealityTargets`
- `POST panel/api/server/logs/{count}`
- `POST panel/api/server/xraylogs/{count}`
- `POST panel/api/server/amneziawglogs/{count}`
- `GET panel/api/server/getMigration`
- `POST panel/api/server/importDB`
- `GET panel/api/server/descendants`
- `GET panel/api/server/clientIps`
- `POST panel/api/server/clientIps`
