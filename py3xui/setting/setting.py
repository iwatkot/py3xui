"""This module contains the models of the panel settings in the XUI API."""

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class AllSettingFields:
    """Stores the fields returned by the XUI API for parsing."""

    WEB_LISTEN = "webListen"
    WEB_DOMAIN = "webDomain"
    WEB_PORT = "webPort"
    WEB_CERT_FILE = "webCertFile"
    WEB_KEY_FILE = "webKeyFile"
    WEB_BASE_PATH = "webBasePath"
    SESSION_MAX_AGE = "sessionMaxAge"
    TRUSTED_PROXY_CIDRS = "trustedProxyCIDRs"
    REALITY_SCAN_CANDIDATES = "realityScanCandidates"
    IP_LIMIT_ALLOWLIST = "ipLimitAllowlist"
    PANEL_OUTBOUND = "panelOutbound"

    PAGE_SIZE = "pageSize"
    EXPIRE_DIFF = "expireDiff"
    TRAFFIC_DIFF = "trafficDiff"
    REMARK_TEMPLATE = "remarkTemplate"
    SUB_SHOW_IDENTITY_ON_ALL_LINKS = "subShowIdentityOnAllLinks"
    SUB_INFO_NODE_ENABLE = "subInfoNodeEnable"
    SUB_HOST_SORT_MODE = "subHostSortMode"
    SUB_CALENDAR_EXPIRE_INCLUSIVE = "subCalendarExpireInclusive"
    SUB_EXPIRED_TEMPLATE = "subExpiredTemplate"
    SUB_TRAFFIC_DEPLETED_TEMPLATE = "subTrafficDepletedTemplate"
    DATEPICKER = "datepicker"

    TG_BOT_ENABLE = "tgBotEnable"
    TG_BOT_TOKEN = "tgBotToken"
    TG_BOT_PROXY = "tgBotProxy"
    TG_BOT_API_SERVER = "tgBotAPIServer"
    TG_BOT_CHAT_ID = "tgBotChatId"
    TG_RUN_TIME = "tgRunTime"
    TG_BOT_BACKUP = "tgBotBackup"
    TG_CPU = "tgCpu"
    TG_MEMORY = "tgMemory"
    TG_LANG = "tgLang"
    TG_ENABLED_EVENTS = "tgEnabledEvents"

    SMTP_ENABLE = "smtpEnable"
    SMTP_HOST = "smtpHost"
    SMTP_PORT = "smtpPort"
    SMTP_USERNAME = "smtpUsername"
    SMTP_PASSWORD = "smtpPassword"
    SMTP_FROM = "smtpFrom"
    SMTP_FROM_NAME = "smtpFromName"
    SMTP_TO = "smtpTo"
    SMTP_ENCRYPTION_TYPE = "smtpEncryptionType"
    SMTP_ENABLED_EVENTS = "smtpEnabledEvents"
    SMTP_CPU = "smtpCpu"
    SMTP_MEMORY = "smtpMemory"

    DISCORD_BOT_ENABLE = "discordBotEnable"
    DISCORD_BOT_TOKEN = "discordBotToken"
    DISCORD_CHANNEL_ID = "discordChannelId"
    DISCORD_ADMIN_IDS = "discordAdminIds"
    DISCORD_RUN_TIME = "discordRunTime"
    DISCORD_BOT_BACKUP = "discordBotBackup"
    DISCORD_CPU = "discordCpu"
    DISCORD_MEMORY = "discordMemory"
    DISCORD_LANG = "discordLang"
    DISCORD_ENABLED_EVENTS = "discordEnabledEvents"

    OUTBOUND_DOWN_THRESHOLD = "outboundDownThreshold"
    NODE_DOWN_THRESHOLD = "nodeDownThreshold"

    TIME_LOCATION = "timeLocation"
    TWO_FACTOR_ENABLE = "twoFactorEnable"
    TWO_FACTOR_TOKEN = "twoFactorToken"

    HAPP_LINK_ENABLE = "happLinkEnable"
    SUB_ENABLE = "subEnable"
    SUB_JSON_ENABLE = "subJsonEnable"
    SUB_JSON_AUTO_DETECT = "subJsonAutoDetect"
    SUB_JSON_ALWAYS_ARRAY = "subJsonAlwaysArray"
    SUB_JSON_USER_AGENT_REGEX = "subJsonUserAgentRegex"
    SUB_CLASH_AUTO_DETECT = "subClashAutoDetect"
    SUB_CLASH_USER_AGENT_REGEX = "subClashUserAgentRegex"
    SUB_TITLE = "subTitle"
    SUB_SUPPORT_URL = "subSupportUrl"
    SUB_PROFILE_MODE = "subProfileMode"
    SUB_PROFILE_URL = "subProfileUrl"
    SUB_ANNOUNCE = "subAnnounce"
    SUB_ENABLE_ROUTING = "subEnableRouting"
    SUB_ROUTING_RULES = "subRoutingRules"
    SUB_INCY_ENABLE_ROUTING = "subIncyEnableRouting"
    SUB_INCY_ROUTING_RULES = "subIncyRoutingRules"
    SUB_LISTEN = "subListen"
    SUB_PORT = "subPort"
    SUB_PATH = "subPath"
    SUB_DOMAIN = "subDomain"
    SUB_CERT_FILE = "subCertFile"
    SUB_KEY_FILE = "subKeyFile"
    EXTERNAL_SUB_USER_AGENT = "externalSubUserAgent"
    SUB_UPDATES = "subUpdates"
    EXTERNAL_TRAFFIC_INFORM_ENABLE = "externalTrafficInformEnable"
    EXTERNAL_TRAFFIC_INFORM_URI = "externalTrafficInformURI"
    RESTART_XRAY_ON_CLIENT_DISABLE = "restartXrayOnClientDisable"
    SUB_ENCRYPT = "subEncrypt"
    SUB_URI = "subURI"
    SUB_JSON_PATH = "subJsonPath"
    SUB_JSON_URI = "subJsonURI"
    SUB_CLASH_ENABLE = "subClashEnable"
    SUB_CLASH_PATH = "subClashPath"
    SUB_CLASH_URI = "subClashURI"
    SUB_CLASH_ENABLE_ROUTING = "subClashEnableRouting"
    SUB_CLASH_RULES = "subClashRules"
    SUB_CLASH_REMOTE_DNS = "subClashRemoteDNS"
    SUB_JSON_MUX = "subJsonMux"
    SUB_JSON_RULES = "subJsonRules"
    SUB_JSON_ROUTING_RULES = "subJsonRoutingRules"
    SUB_JSON_DNS = "subJsonDns"
    SUB_JSON_FINAL_MASK = "subJsonFinalMask"
    SUB_JSON_OBSERVATORY = "subJsonObservatory"
    SUB_THEME_DIR = "subThemeDir"
    SUB_HIDE_SETTINGS = "subHideSettings"

    SUB_HAPP_AUTO_DETECT = "subHappAutoDetect"
    SUB_HAPP_PROVIDER_ID = "subHappProviderId"
    SUB_HAPP_NEW_URL = "subHappNewUrl"
    SUB_HAPP_FALLBACK_URL = "subHappFallbackUrl"
    SUB_HAPP_SUB_INFO_COLOR = "subHappSubInfoColor"
    SUB_HAPP_SUB_INFO_TEXT = "subHappSubInfoText"
    SUB_HAPP_SUB_INFO_BUTTON_TEXT = "subHappSubInfoButtonText"
    SUB_HAPP_SUB_INFO_BUTTON_LINK = "subHappSubInfoButtonLink"
    SUB_HAPP_SUB_EXPIRE = "subHappSubExpire"
    SUB_HAPP_SUB_EXPIRE_BUTTON_LINK = "subHappSubExpireButtonLink"
    SUB_HAPP_NOTIFICATION_EXPIRE = "subHappNotificationExpire"
    SUB_HAPP_NO_LIMIT = "subHappNoLimit"
    SUB_HAPP_ALWAYS_HWID = "subHappAlwaysHwid"
    SUB_HAPP_TUN_MODE = "subHappTunMode"
    SUB_HAPP_TUN_TYPE = "subHappTunType"
    SUB_HAPP_EXCLUDE_ROUTES = "subHappExcludeRoutes"
    SUB_HAPP_EXCLUDE_APNS = "subHappExcludeApns"
    SUB_HAPP_COLOR_PROFILE = "subHappColorProfile"
    SUB_HAPP_PING_TYPE = "subHappPingType"
    SUB_HAPP_AUTO_CONNECT = "subHappAutoConnect"
    SUB_HAPP_AUTO_CONNECT_TYPE = "subHappAutoConnectType"
    SUB_HAPP_PER_APP_MODE = "subHappPerAppMode"
    SUB_HAPP_PER_APP_LIST = "subHappPerAppList"
    SUB_HAPP_LOCAL_PROXY_AUTH = "subHappLocalProxyAuth"

    SUB_INCY_APP_AUTO_DETECT = "subIncyAppAutoDetect"
    SUB_INCY_PROFILE_DESCRIPTION = "subIncyProfileDescription"
    SUB_INCY_SORT_ORDER = "subIncySortOrder"
    SUB_INCY_SUPPORT_EMAIL = "subIncySupportEmail"
    SUB_INCY_ANNOUNCE_URL = "subIncyAnnounceUrl"
    SUB_INCY_PREMIUM_URL = "subIncyPremiumUrl"
    SUB_INCY_BANNER_TEXT = "subIncyBannerText"
    SUB_INCY_BANNER_BUTTON_TEXT = "subIncyBannerButtonText"
    SUB_INCY_BANNER_BUTTON_URL = "subIncyBannerButtonUrl"
    SUB_INCY_BANNER_BG_COLOR = "subIncyBannerBgColor"
    SUB_INCY_BANNER_BUTTON_COLOR = "subIncyBannerButtonColor"
    SUB_INCY_HIDE_URL = "subIncyHideUrl"
    SUB_INCY_HIDE_CHECK = "subIncyHideCheck"
    SUB_INCY_NO_LIMIT_ENABLED = "subIncyNoLimitEnabled"
    SUB_INCY_PER_APP_ENABLE = "subIncyPerAppEnable"
    SUB_INCY_PER_APP_MODE = "subIncyPerAppMode"
    SUB_INCY_PER_APP_LIST = "subIncyPerAppList"
    SUB_INCY_FRAGMENTATION_ENABLE = "subIncyFragmentationEnable"
    SUB_INCY_FRAGMENT_LENGTH = "subIncyFragmentLength"
    SUB_INCY_FRAGMENT_INTERVAL = "subIncyFragmentInterval"
    SUB_INCY_FRAGMENT_PACKETS = "subIncyFragmentPackets"
    SUB_INCY_NOISES_ENABLE = "subIncyNoisesEnable"
    SUB_INCY_NOISES_TYPE = "subIncyNoisesType"
    SUB_INCY_NOISES_PACKET = "subIncyNoisesPacket"
    SUB_INCY_NOISES_DELAY = "subIncyNoisesDelay"
    SUB_INCY_RESOLVE_ENABLE = "subIncyResolveEnable"
    SUB_INCY_RESOLVE_DNS_DOMAIN = "subIncyResolveDnsDomain"
    SUB_INCY_RESOLVE_DNS_IP = "subIncyResolveDnsIp"

    LDAP_ENABLE = "ldapEnable"
    LDAP_HOST = "ldapHost"
    LDAP_PORT = "ldapPort"
    LDAP_USE_TLS = "ldapUseTLS"
    LDAP_INSECURE_SKIP_VERIFY = "ldapInsecureSkipVerify"
    LDAP_BIND_DN = "ldapBindDN"
    LDAP_PASSWORD = "ldapPassword"
    LDAP_BASE_DN = "ldapBaseDN"
    LDAP_USER_FILTER = "ldapUserFilter"
    LDAP_USER_ATTR = "ldapUserAttr"
    LDAP_VLESS_FIELD = "ldapVlessField"
    LDAP_SYNC_CRON = "ldapSyncCron"
    LDAP_FLAG_FIELD = "ldapFlagField"
    LDAP_TRUTHY_VALUES = "ldapTruthyValues"
    LDAP_INVERT_FLAG = "ldapInvertFlag"
    LDAP_INBOUND_TAGS = "ldapInboundTags"
    LDAP_AUTO_CREATE = "ldapAutoCreate"
    LDAP_AUTO_DELETE = "ldapAutoDelete"
    LDAP_DEFAULT_TOTAL_GB = "ldapDefaultTotalGB"
    LDAP_DEFAULT_EXPIRY_DAYS = "ldapDefaultExpiryDays"
    LDAP_DEFAULT_LIMIT_IP = "ldapDefaultLimitIP"

    WARP_UPDATE_INTERVAL = "warpUpdateInterval"

    HAS_TG_BOT_TOKEN = "hasTgBotToken"
    HAS_TWO_FACTOR_TOKEN = "hasTwoFactorToken"
    HAS_LDAP_PASSWORD = "hasLdapPassword"
    HAS_API_TOKEN = "hasApiToken"
    HAS_WARP_SECRET = "hasWarpSecret"
    HAS_NORD_SECRET = "hasNordSecret"
    HAS_SMTP_PASSWORD = "hasSmtpPassword"
    HAS_DISCORD_BOT_TOKEN = "hasDiscordBotToken"


class AllSetting(BaseModel):
    """Represents every panel setting in the XUI API.

    Field names are the snake_case form of the panel keys kept in `AllSettingFields`. All
    of them are optional when parsing. Keys unknown to this model are kept and sent back.

    The panel redacts secrets in `get_all()`: `tg_bot_token`, `two_factor_token`,
    `ldap_password`, `smtp_password` and `discord_bot_token` come back blank and the
    `has_*` flags tell whether they are configured. A blank secret sent to `update()`
    keeps the stored value. The `has_*` flags are read-only and left out of `model_dump()`.

    Attributes:
        Web server:
            web_listen (str), web_domain (str), web_port (int), web_cert_file (str),
            web_key_file (str), web_base_path (str), session_max_age (int),
            trusted_proxy_cidrs (str), reality_scan_candidates (str), ip_limit_allowlist (str),
            panel_outbound (str)
        Display and subscription templates:
            page_size (int), expire_diff (int), traffic_diff (int), remark_template (str),
            sub_show_identity_on_all_links (bool), sub_info_node_enable (bool),
            sub_host_sort_mode (str), sub_calendar_expire_inclusive (bool),
            sub_expired_template (str), sub_traffic_depleted_template (str), datepicker (str)
        Telegram bot:
            tg_bot_enable (bool), tg_bot_token (str), tg_bot_proxy (str), tg_bot_api_server (str),
            tg_bot_chat_id (str), tg_run_time (str), tg_bot_backup (bool), tg_cpu (int),
            tg_memory (int), tg_lang (str), tg_enabled_events (str)
        SMTP notifications:
            smtp_enable (bool), smtp_host (str), smtp_port (int), smtp_username (str),
            smtp_password (str), smtp_from (str), smtp_from_name (str), smtp_to (str),
            smtp_encryption_type (str), smtp_enabled_events (str), smtp_cpu (int), smtp_memory (int)
        Discord bot:
            discord_bot_enable (bool), discord_bot_token (str), discord_channel_id (str),
            discord_admin_ids (str), discord_run_time (str), discord_bot_backup (bool),
            discord_cpu (int), discord_memory (int), discord_lang (str),
            discord_enabled_events (str)
        Alert thresholds:
            outbound_down_threshold (int), node_down_threshold (int)
        Time zone and two-factor authentication:
            time_location (str), two_factor_enable (bool), two_factor_token (str)
        Subscription service:
            happ_link_enable (bool), sub_enable (bool), sub_json_enable (bool),
            sub_json_auto_detect (bool), sub_json_always_array (bool),
            sub_json_user_agent_regex (str), sub_clash_auto_detect (bool),
            sub_clash_user_agent_regex (str), sub_title (str), sub_support_url (str),
            sub_profile_mode (str), sub_profile_url (str), sub_announce (str),
            sub_enable_routing (bool), sub_routing_rules (str), sub_incy_enable_routing (bool),
            sub_incy_routing_rules (str), sub_listen (str), sub_port (int), sub_path (str),
            sub_domain (str), sub_cert_file (str), sub_key_file (str),
            external_sub_user_agent (str), sub_updates (int), external_traffic_inform_enable (bool),
            external_traffic_inform_uri (str), restart_xray_on_client_disable (bool),
            sub_encrypt (bool), sub_uri (str), sub_json_path (str), sub_json_uri (str),
            sub_clash_enable (bool), sub_clash_path (str), sub_clash_uri (str),
            sub_clash_enable_routing (bool), sub_clash_rules (str), sub_clash_remote_dns (bool),
            sub_json_mux (str), sub_json_rules (str), sub_json_routing_rules (str),
            sub_json_dns (str), sub_json_final_mask (str), sub_json_observatory (str),
            sub_theme_dir (str), sub_hide_settings (bool)
        Happ client customization:
            sub_happ_auto_detect (bool), sub_happ_provider_id (str), sub_happ_new_url (str),
            sub_happ_fallback_url (str), sub_happ_sub_info_color (str),
            sub_happ_sub_info_text (str), sub_happ_sub_info_button_text (str),
            sub_happ_sub_info_button_link (str), sub_happ_sub_expire (bool),
            sub_happ_sub_expire_button_link (str), sub_happ_notification_expire (bool),
            sub_happ_no_limit (bool), sub_happ_always_hwid (bool), sub_happ_tun_mode (str),
            sub_happ_tun_type (str), sub_happ_exclude_routes (str), sub_happ_exclude_apns (bool),
            sub_happ_color_profile (str), sub_happ_ping_type (str), sub_happ_auto_connect (bool),
            sub_happ_auto_connect_type (str), sub_happ_per_app_mode (str),
            sub_happ_per_app_list (str), sub_happ_local_proxy_auth (str)
        Incy client customization:
            sub_incy_app_auto_detect (bool), sub_incy_profile_description (str),
            sub_incy_sort_order (str), sub_incy_support_email (str), sub_incy_announce_url (str),
            sub_incy_premium_url (str), sub_incy_banner_text (str),
            sub_incy_banner_button_text (str), sub_incy_banner_button_url (str),
            sub_incy_banner_bg_color (str), sub_incy_banner_button_color (str),
            sub_incy_hide_url (str), sub_incy_hide_check (str), sub_incy_no_limit_enabled (str),
            sub_incy_per_app_enable (str), sub_incy_per_app_mode (str), sub_incy_per_app_list (str),
            sub_incy_fragmentation_enable (str), sub_incy_fragment_length (str),
            sub_incy_fragment_interval (str), sub_incy_fragment_packets (str),
            sub_incy_noises_enable (str), sub_incy_noises_type (str), sub_incy_noises_packet (str),
            sub_incy_noises_delay (str), sub_incy_resolve_enable (str),
            sub_incy_resolve_dns_domain (str), sub_incy_resolve_dns_ip (str)
        LDAP:
            ldap_enable (bool), ldap_host (str), ldap_port (int), ldap_use_tls (bool),
            ldap_insecure_skip_verify (bool), ldap_bind_dn (str), ldap_password (str),
            ldap_base_dn (str), ldap_user_filter (str), ldap_user_attr (str),
            ldap_vless_field (str), ldap_sync_cron (str), ldap_flag_field (str),
            ldap_truthy_values (str), ldap_invert_flag (bool), ldap_inbound_tags (str),
            ldap_auto_create (bool), ldap_auto_delete (bool), ldap_default_total_gb (int),
            ldap_default_expiry_days (int), ldap_default_limit_ip (int)
        WARP:
            warp_update_interval (int)
        Read-only flags (never sent back):
            has_tg_bot_token (bool), has_two_factor_token (bool), has_ldap_password (bool),
            has_api_token (bool), has_warp_secret (bool), has_nord_secret (bool),
            has_smtp_password (bool), has_discord_bot_token (bool)

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()
        api.login()

        settings: py3xui.AllSetting = api.setting.get_all()
        settings.sub_title = "My subscription"
        api.setting.update(settings)
        ```
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    web_listen: str = Field(default="", alias=AllSettingFields.WEB_LISTEN)  # type: ignore
    web_domain: str = Field(default="", alias=AllSettingFields.WEB_DOMAIN)  # type: ignore
    web_port: int = Field(default=0, alias=AllSettingFields.WEB_PORT)  # type: ignore
    web_cert_file: str = Field(default="", alias=AllSettingFields.WEB_CERT_FILE)  # type: ignore
    web_key_file: str = Field(default="", alias=AllSettingFields.WEB_KEY_FILE)  # type: ignore
    web_base_path: str = Field(default="", alias=AllSettingFields.WEB_BASE_PATH)  # type: ignore
    session_max_age: int = Field(default=0, alias=AllSettingFields.SESSION_MAX_AGE)  # type: ignore
    trusted_proxy_cidrs: str = Field(  # type: ignore
        default="", alias=AllSettingFields.TRUSTED_PROXY_CIDRS
    )
    reality_scan_candidates: str = Field(  # type: ignore
        default="", alias=AllSettingFields.REALITY_SCAN_CANDIDATES
    )
    ip_limit_allowlist: str = Field(  # type: ignore
        default="", alias=AllSettingFields.IP_LIMIT_ALLOWLIST
    )
    panel_outbound: str = Field(default="", alias=AllSettingFields.PANEL_OUTBOUND)  # type: ignore

    page_size: int = Field(default=0, alias=AllSettingFields.PAGE_SIZE)  # type: ignore
    expire_diff: int = Field(default=0, alias=AllSettingFields.EXPIRE_DIFF)  # type: ignore
    traffic_diff: int = Field(default=0, alias=AllSettingFields.TRAFFIC_DIFF)  # type: ignore
    remark_template: str = Field(default="", alias=AllSettingFields.REMARK_TEMPLATE)  # type: ignore
    sub_show_identity_on_all_links: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_SHOW_IDENTITY_ON_ALL_LINKS
    )
    sub_info_node_enable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_INFO_NODE_ENABLE
    )
    sub_host_sort_mode: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HOST_SORT_MODE
    )
    sub_calendar_expire_inclusive: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_CALENDAR_EXPIRE_INCLUSIVE
    )
    sub_expired_template: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_EXPIRED_TEMPLATE
    )
    sub_traffic_depleted_template: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_TRAFFIC_DEPLETED_TEMPLATE
    )
    datepicker: str = Field(default="", alias=AllSettingFields.DATEPICKER)  # type: ignore

    tg_bot_enable: bool = Field(default=False, alias=AllSettingFields.TG_BOT_ENABLE)  # type: ignore
    tg_bot_token: str = Field(default="", alias=AllSettingFields.TG_BOT_TOKEN)  # type: ignore
    tg_bot_proxy: str = Field(default="", alias=AllSettingFields.TG_BOT_PROXY)  # type: ignore
    tg_bot_api_server: str = Field(  # type: ignore
        default="", alias=AllSettingFields.TG_BOT_API_SERVER
    )
    tg_bot_chat_id: str = Field(default="", alias=AllSettingFields.TG_BOT_CHAT_ID)  # type: ignore
    tg_run_time: str = Field(default="", alias=AllSettingFields.TG_RUN_TIME)  # type: ignore
    tg_bot_backup: bool = Field(default=False, alias=AllSettingFields.TG_BOT_BACKUP)  # type: ignore
    tg_cpu: int = Field(default=0, alias=AllSettingFields.TG_CPU)  # type: ignore
    tg_memory: int = Field(default=0, alias=AllSettingFields.TG_MEMORY)  # type: ignore
    tg_lang: str = Field(default="", alias=AllSettingFields.TG_LANG)  # type: ignore
    tg_enabled_events: str = Field(  # type: ignore
        default="", alias=AllSettingFields.TG_ENABLED_EVENTS
    )

    smtp_enable: bool = Field(default=False, alias=AllSettingFields.SMTP_ENABLE)  # type: ignore
    smtp_host: str = Field(default="", alias=AllSettingFields.SMTP_HOST)  # type: ignore
    smtp_port: int = Field(default=0, alias=AllSettingFields.SMTP_PORT)  # type: ignore
    smtp_username: str = Field(default="", alias=AllSettingFields.SMTP_USERNAME)  # type: ignore
    smtp_password: str = Field(default="", alias=AllSettingFields.SMTP_PASSWORD)  # type: ignore
    smtp_from: str = Field(default="", alias=AllSettingFields.SMTP_FROM)  # type: ignore
    smtp_from_name: str = Field(default="", alias=AllSettingFields.SMTP_FROM_NAME)  # type: ignore
    smtp_to: str = Field(default="", alias=AllSettingFields.SMTP_TO)  # type: ignore
    smtp_encryption_type: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SMTP_ENCRYPTION_TYPE
    )
    smtp_enabled_events: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SMTP_ENABLED_EVENTS
    )
    smtp_cpu: int = Field(default=0, alias=AllSettingFields.SMTP_CPU)  # type: ignore
    smtp_memory: int = Field(default=0, alias=AllSettingFields.SMTP_MEMORY)  # type: ignore

    discord_bot_enable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.DISCORD_BOT_ENABLE
    )
    discord_bot_token: str = Field(  # type: ignore
        default="", alias=AllSettingFields.DISCORD_BOT_TOKEN
    )
    discord_channel_id: str = Field(  # type: ignore
        default="", alias=AllSettingFields.DISCORD_CHANNEL_ID
    )
    discord_admin_ids: str = Field(  # type: ignore
        default="", alias=AllSettingFields.DISCORD_ADMIN_IDS
    )
    discord_run_time: str = Field(  # type: ignore
        default="", alias=AllSettingFields.DISCORD_RUN_TIME
    )
    discord_bot_backup: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.DISCORD_BOT_BACKUP
    )
    discord_cpu: int = Field(default=0, alias=AllSettingFields.DISCORD_CPU)  # type: ignore
    discord_memory: int = Field(default=0, alias=AllSettingFields.DISCORD_MEMORY)  # type: ignore
    discord_lang: str = Field(default="", alias=AllSettingFields.DISCORD_LANG)  # type: ignore
    discord_enabled_events: str = Field(  # type: ignore
        default="", alias=AllSettingFields.DISCORD_ENABLED_EVENTS
    )

    outbound_down_threshold: int = Field(  # type: ignore
        default=0, alias=AllSettingFields.OUTBOUND_DOWN_THRESHOLD
    )
    node_down_threshold: int = Field(  # type: ignore
        default=0, alias=AllSettingFields.NODE_DOWN_THRESHOLD
    )

    time_location: str = Field(default="", alias=AllSettingFields.TIME_LOCATION)  # type: ignore
    two_factor_enable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.TWO_FACTOR_ENABLE
    )
    two_factor_token: str = Field(  # type: ignore
        default="", alias=AllSettingFields.TWO_FACTOR_TOKEN
    )

    happ_link_enable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAPP_LINK_ENABLE
    )
    sub_enable: bool = Field(default=False, alias=AllSettingFields.SUB_ENABLE)  # type: ignore
    sub_json_enable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_JSON_ENABLE
    )
    sub_json_auto_detect: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_JSON_AUTO_DETECT
    )
    sub_json_always_array: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_JSON_ALWAYS_ARRAY
    )
    sub_json_user_agent_regex: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_JSON_USER_AGENT_REGEX
    )
    sub_clash_auto_detect: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_CLASH_AUTO_DETECT
    )
    sub_clash_user_agent_regex: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_CLASH_USER_AGENT_REGEX
    )
    sub_title: str = Field(default="", alias=AllSettingFields.SUB_TITLE)  # type: ignore
    sub_support_url: str = Field(default="", alias=AllSettingFields.SUB_SUPPORT_URL)  # type: ignore
    sub_profile_mode: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_PROFILE_MODE
    )
    sub_profile_url: str = Field(default="", alias=AllSettingFields.SUB_PROFILE_URL)  # type: ignore
    sub_announce: str = Field(default="", alias=AllSettingFields.SUB_ANNOUNCE)  # type: ignore
    sub_enable_routing: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_ENABLE_ROUTING
    )
    sub_routing_rules: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_ROUTING_RULES
    )
    sub_incy_enable_routing: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_INCY_ENABLE_ROUTING
    )
    sub_incy_routing_rules: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_ROUTING_RULES
    )
    sub_listen: str = Field(default="", alias=AllSettingFields.SUB_LISTEN)  # type: ignore
    sub_port: int = Field(default=0, alias=AllSettingFields.SUB_PORT)  # type: ignore
    sub_path: str = Field(default="", alias=AllSettingFields.SUB_PATH)  # type: ignore
    sub_domain: str = Field(default="", alias=AllSettingFields.SUB_DOMAIN)  # type: ignore
    sub_cert_file: str = Field(default="", alias=AllSettingFields.SUB_CERT_FILE)  # type: ignore
    sub_key_file: str = Field(default="", alias=AllSettingFields.SUB_KEY_FILE)  # type: ignore
    external_sub_user_agent: str = Field(  # type: ignore
        default="", alias=AllSettingFields.EXTERNAL_SUB_USER_AGENT
    )
    sub_updates: int = Field(default=0, alias=AllSettingFields.SUB_UPDATES)  # type: ignore
    external_traffic_inform_enable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.EXTERNAL_TRAFFIC_INFORM_ENABLE
    )
    external_traffic_inform_uri: str = Field(  # type: ignore
        default="", alias=AllSettingFields.EXTERNAL_TRAFFIC_INFORM_URI
    )
    restart_xray_on_client_disable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.RESTART_XRAY_ON_CLIENT_DISABLE
    )
    sub_encrypt: bool = Field(default=False, alias=AllSettingFields.SUB_ENCRYPT)  # type: ignore
    sub_uri: str = Field(default="", alias=AllSettingFields.SUB_URI)  # type: ignore
    sub_json_path: str = Field(default="", alias=AllSettingFields.SUB_JSON_PATH)  # type: ignore
    sub_json_uri: str = Field(default="", alias=AllSettingFields.SUB_JSON_URI)  # type: ignore
    sub_clash_enable: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_CLASH_ENABLE
    )
    sub_clash_path: str = Field(default="", alias=AllSettingFields.SUB_CLASH_PATH)  # type: ignore
    sub_clash_uri: str = Field(default="", alias=AllSettingFields.SUB_CLASH_URI)  # type: ignore
    sub_clash_enable_routing: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_CLASH_ENABLE_ROUTING
    )
    sub_clash_rules: str = Field(default="", alias=AllSettingFields.SUB_CLASH_RULES)  # type: ignore
    sub_clash_remote_dns: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_CLASH_REMOTE_DNS
    )
    sub_json_mux: str = Field(default="", alias=AllSettingFields.SUB_JSON_MUX)  # type: ignore
    sub_json_rules: str = Field(default="", alias=AllSettingFields.SUB_JSON_RULES)  # type: ignore
    sub_json_routing_rules: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_JSON_ROUTING_RULES
    )
    sub_json_dns: str = Field(default="", alias=AllSettingFields.SUB_JSON_DNS)  # type: ignore
    sub_json_final_mask: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_JSON_FINAL_MASK
    )
    sub_json_observatory: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_JSON_OBSERVATORY
    )
    sub_theme_dir: str = Field(default="", alias=AllSettingFields.SUB_THEME_DIR)  # type: ignore
    sub_hide_settings: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HIDE_SETTINGS
    )

    sub_happ_auto_detect: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HAPP_AUTO_DETECT
    )
    sub_happ_provider_id: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_PROVIDER_ID
    )
    sub_happ_new_url: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_NEW_URL
    )
    sub_happ_fallback_url: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_FALLBACK_URL
    )
    sub_happ_sub_info_color: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_SUB_INFO_COLOR
    )
    sub_happ_sub_info_text: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_SUB_INFO_TEXT
    )
    sub_happ_sub_info_button_text: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_SUB_INFO_BUTTON_TEXT
    )
    sub_happ_sub_info_button_link: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_SUB_INFO_BUTTON_LINK
    )
    sub_happ_sub_expire: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HAPP_SUB_EXPIRE
    )
    sub_happ_sub_expire_button_link: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_SUB_EXPIRE_BUTTON_LINK
    )
    sub_happ_notification_expire: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HAPP_NOTIFICATION_EXPIRE
    )
    sub_happ_no_limit: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HAPP_NO_LIMIT
    )
    sub_happ_always_hwid: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HAPP_ALWAYS_HWID
    )
    sub_happ_tun_mode: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_TUN_MODE
    )
    sub_happ_tun_type: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_TUN_TYPE
    )
    sub_happ_exclude_routes: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_EXCLUDE_ROUTES
    )
    sub_happ_exclude_apns: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HAPP_EXCLUDE_APNS
    )
    sub_happ_color_profile: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_COLOR_PROFILE
    )
    sub_happ_ping_type: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_PING_TYPE
    )
    sub_happ_auto_connect: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_HAPP_AUTO_CONNECT
    )
    sub_happ_auto_connect_type: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_AUTO_CONNECT_TYPE
    )
    sub_happ_per_app_mode: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_PER_APP_MODE
    )
    sub_happ_per_app_list: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_PER_APP_LIST
    )
    sub_happ_local_proxy_auth: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_HAPP_LOCAL_PROXY_AUTH
    )

    sub_incy_app_auto_detect: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.SUB_INCY_APP_AUTO_DETECT
    )
    sub_incy_profile_description: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_PROFILE_DESCRIPTION
    )
    sub_incy_sort_order: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_SORT_ORDER
    )
    sub_incy_support_email: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_SUPPORT_EMAIL
    )
    sub_incy_announce_url: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_ANNOUNCE_URL
    )
    sub_incy_premium_url: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_PREMIUM_URL
    )
    sub_incy_banner_text: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_BANNER_TEXT
    )
    sub_incy_banner_button_text: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_BANNER_BUTTON_TEXT
    )
    sub_incy_banner_button_url: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_BANNER_BUTTON_URL
    )
    sub_incy_banner_bg_color: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_BANNER_BG_COLOR
    )
    sub_incy_banner_button_color: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_BANNER_BUTTON_COLOR
    )
    sub_incy_hide_url: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_HIDE_URL
    )
    sub_incy_hide_check: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_HIDE_CHECK
    )
    sub_incy_no_limit_enabled: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_NO_LIMIT_ENABLED
    )
    sub_incy_per_app_enable: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_PER_APP_ENABLE
    )
    sub_incy_per_app_mode: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_PER_APP_MODE
    )
    sub_incy_per_app_list: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_PER_APP_LIST
    )
    sub_incy_fragmentation_enable: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_FRAGMENTATION_ENABLE
    )
    sub_incy_fragment_length: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_FRAGMENT_LENGTH
    )
    sub_incy_fragment_interval: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_FRAGMENT_INTERVAL
    )
    sub_incy_fragment_packets: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_FRAGMENT_PACKETS
    )
    sub_incy_noises_enable: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_NOISES_ENABLE
    )
    sub_incy_noises_type: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_NOISES_TYPE
    )
    sub_incy_noises_packet: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_NOISES_PACKET
    )
    sub_incy_noises_delay: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_NOISES_DELAY
    )
    sub_incy_resolve_enable: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_RESOLVE_ENABLE
    )
    sub_incy_resolve_dns_domain: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_RESOLVE_DNS_DOMAIN
    )
    sub_incy_resolve_dns_ip: str = Field(  # type: ignore
        default="", alias=AllSettingFields.SUB_INCY_RESOLVE_DNS_IP
    )

    ldap_enable: bool = Field(default=False, alias=AllSettingFields.LDAP_ENABLE)  # type: ignore
    ldap_host: str = Field(default="", alias=AllSettingFields.LDAP_HOST)  # type: ignore
    ldap_port: int = Field(default=0, alias=AllSettingFields.LDAP_PORT)  # type: ignore
    ldap_use_tls: bool = Field(default=False, alias=AllSettingFields.LDAP_USE_TLS)  # type: ignore
    ldap_insecure_skip_verify: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.LDAP_INSECURE_SKIP_VERIFY
    )
    ldap_bind_dn: str = Field(default="", alias=AllSettingFields.LDAP_BIND_DN)  # type: ignore
    ldap_password: str = Field(default="", alias=AllSettingFields.LDAP_PASSWORD)  # type: ignore
    ldap_base_dn: str = Field(default="", alias=AllSettingFields.LDAP_BASE_DN)  # type: ignore
    ldap_user_filter: str = Field(  # type: ignore
        default="", alias=AllSettingFields.LDAP_USER_FILTER
    )
    ldap_user_attr: str = Field(default="", alias=AllSettingFields.LDAP_USER_ATTR)  # type: ignore
    ldap_vless_field: str = Field(  # type: ignore
        default="", alias=AllSettingFields.LDAP_VLESS_FIELD
    )
    ldap_sync_cron: str = Field(default="", alias=AllSettingFields.LDAP_SYNC_CRON)  # type: ignore
    ldap_flag_field: str = Field(default="", alias=AllSettingFields.LDAP_FLAG_FIELD)  # type: ignore
    ldap_truthy_values: str = Field(  # type: ignore
        default="", alias=AllSettingFields.LDAP_TRUTHY_VALUES
    )
    ldap_invert_flag: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.LDAP_INVERT_FLAG
    )
    ldap_inbound_tags: str = Field(  # type: ignore
        default="", alias=AllSettingFields.LDAP_INBOUND_TAGS
    )
    ldap_auto_create: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.LDAP_AUTO_CREATE
    )
    ldap_auto_delete: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.LDAP_AUTO_DELETE
    )
    ldap_default_total_gb: int = Field(  # type: ignore
        default=0, alias=AllSettingFields.LDAP_DEFAULT_TOTAL_GB
    )
    ldap_default_expiry_days: int = Field(  # type: ignore
        default=0, alias=AllSettingFields.LDAP_DEFAULT_EXPIRY_DAYS
    )
    ldap_default_limit_ip: int = Field(  # type: ignore
        default=0, alias=AllSettingFields.LDAP_DEFAULT_LIMIT_IP
    )

    warp_update_interval: int = Field(  # type: ignore
        default=0, alias=AllSettingFields.WARP_UPDATE_INTERVAL
    )

    has_tg_bot_token: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_TG_BOT_TOKEN, exclude=True
    )
    has_two_factor_token: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_TWO_FACTOR_TOKEN, exclude=True
    )
    has_ldap_password: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_LDAP_PASSWORD, exclude=True
    )
    has_api_token: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_API_TOKEN, exclude=True
    )
    has_warp_secret: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_WARP_SECRET, exclude=True
    )
    has_nord_secret: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_NORD_SECRET, exclude=True
    )
    has_smtp_password: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_SMTP_PASSWORD, exclude=True
    )
    has_discord_bot_token: bool = Field(  # type: ignore
        default=False, alias=AllSettingFields.HAS_DISCORD_BOT_TOKEN, exclude=True
    )


# pylint: disable=too-few-public-methods
class TgBotCapabilitiesFields:
    """Stores the fields returned by the XUI API for parsing."""

    INLINE_ENABLED = "inlineEnabled"
    GROUP_PRIVACY = "groupPrivacy"
    USERNAME = "username"
    RUNNING = "running"


class TgBotCapabilities(BaseModel):
    """Represents what the Telegram bot configured on the panel can do.

    Attributes:
        inline_enabled (bool): Whether inline mode is switched on in BotFather. Required.
        group_privacy (bool): Whether group privacy is on. When it is, the bot does not see
            a bare /start in a group. Required.
        username (str): The username of the bot. Required.
        running (bool): Whether the bot is running. Required.
    """

    model_config = ConfigDict(populate_by_name=True)

    inline_enabled: bool = Field(alias=TgBotCapabilitiesFields.INLINE_ENABLED)  # type: ignore
    group_privacy: bool = Field(alias=TgBotCapabilitiesFields.GROUP_PRIVACY)  # type: ignore
    username: str
    running: bool
