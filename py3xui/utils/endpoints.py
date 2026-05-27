from enum import Enum


class Endpoints(str, Enum):
    """Stores the endpoints for the XUI API."""

    LOGIN = "login"
    CSRF_TOKEN = "csrf-token"

    # Inbounds
    INBOUND_LIST = "panel/api/inbounds/list"
    INBOUND_GET = "panel/api/inbounds/get/{inbound_id}"
    INBOUND_ADD = "panel/api/inbounds/add"
    INBOUND_DELETE = "panel/api/inbounds/del/{inbound_id}"
    INBOUND_UPDATE = "panel/api/inbounds/update/{inbound_id}"
    INBOUND_RESET_ALL_TRAFFICS = "panel/api/inbounds/resetAllTraffics"
    INBOUND_RESET_CLIENT_TRAFFIC = "panel/api/inbounds/resetAllClientTraffics/{inbound_id}"

    # Clients
    CLIENT_GET_BY_EMAIL = "panel/api/inbounds/getClientTraffics/{email}"
    CLIENT_GET_IPS = "panel/api/inbounds/clientIps/{email}"
    CLIENT_ADD = "panel/api/inbounds/addClient"
    CLIENT_UPDATE = "panel/api/inbounds/updateClient/{client_uuid}"
    CLIENT_CLEAR_IPS = "panel/api/inbounds/clearClientIps/{email}"
    CLIENT_RESET_TRAFFIC = "panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}"
    CLIENT_DELETE = "panel/api/inbounds/{inbound_id}/delClient/{client_uuid}"
    CLIENT_DELETE_DEPLETED = "panel/api/inbounds/delDepletedClients/{inbound_id}"
    CLIENT_ONLINE = "panel/api/inbounds/onlines"
    CLIENT_GET_TRAFFIC_BY_ID = "panel/api/inbounds/getClientTrafficsById/{client_uuid}"

    # Server
    SERVER_GET_DB = "panel/api/server/getDb"
    SERVER_STATUS = "panel/api/server/status"
    SERVER_GET_NEW_X25519_CERT = "panel/api/server/getNewX25519Cert"
    SERVER_INSTALL_XRAY = "panel/api/server/installXray/{version}"
    SERVER_UPDATE_GEOFILE = "panel/api/server/updateGeofile"
    SERVER_GET_XRAY_VERSION = "panel/api/server/getXrayVersion"
    SERVER_GET_CONFIG_JSON = "panel/api/server/getConfigJson"

    # Database
    DATABASE_CREATE_BACKUP = "panel/api/inbounds/createbackup"
