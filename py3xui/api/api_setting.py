"""This module contains the SettingApi class for handling panel settings in the XUI API."""

# pylint: disable=R0801

from typing import Any

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.setting import AllSetting, TgBotCapabilities


class SettingApi(BaseApi):
    """This class provides methods to interact with the panel settings in the XUI API.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_all: Retrieves all panel settings.
        get_default_settings: Retrieves the effective default settings for the request host.
        get_factory_defaults: Retrieves the shipped default value of each setting.
        update: Saves all panel settings.
        validate_regex: Validates a regular expression with the panel's RE2 compiler.
        update_user: Changes the panel admin username and password.
        restart_panel: Restarts the panel.
        test_smtp: Sends a test email and reports the stage it reached.
        test_tg_bot: Sends a test message through the Telegram bot.
        get_tg_bot_capabilities: Retrieves what the Telegram bot can do.
        test_discord: Sends a test notification through the Discord bot.
        get_default_xray_config: Retrieves the default Xray config template.

    Examples:
        ```python
        import py3xui

        api = py3xui.Api.from_env()
        api.login()

        settings: py3xui.AllSetting = api.setting.get_all()
        ```
    """

    def get_all(self) -> AllSetting:
        """This route is used to retrieve all panel settings.

        Secrets come back blank, the `has_*` flags of the model tell whether they are set.

        Returns:
            AllSetting: The panel settings.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            settings: py3xui.AllSetting = api.setting.get_all()
            print(settings.web_port)
            ```
        """
        endpoint = "panel/api/setting/all"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting all panel settings...")

        response = self._post(url, headers, {})
        return AllSetting.model_validate(response.json().get(ApiFields.OBJ))

    def get_default_settings(self) -> dict[str, Any]:
        """This route is used to retrieve the effective default settings for the request host.

        The values are the ones currently in effect, so they depend on the stored settings.

        Returns:
            dict[str, Any]: The settings by panel key (e.g. `pageSize`, `subURI`).

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            defaults = api.setting.get_default_settings()
            print(defaults["subURI"])
            ```
        """
        endpoint = "panel/api/setting/defaultSettings"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting default settings...")

        response = self._post(url, headers, {})
        return response.json().get(ApiFields.OBJ)

    def get_factory_defaults(self) -> dict[str, str]:
        """This route is used to retrieve the shipped default value of each setting.

        Credentials and per-install values are never included.

        Returns:
            dict[str, str]: The default values by panel key, all of them as strings.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            factory_defaults = api.setting.get_factory_defaults()
            print(factory_defaults["webPort"])
            ```
        """
        endpoint = "panel/api/setting/factoryDefaults"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting factory defaults...")

        response = self._post(url, headers, {})
        return response.json().get(ApiFields.OBJ)

    def update(  # pylint: disable=R0913
        self,
        settings: AllSetting,
        *,
        two_factor_code: str | int | None = None,
        clear_tg_bot_token: bool = False,
        clear_ldap_password: bool = False,
        clear_smtp_password: bool = False,
        clear_discord_bot_token: bool = False,
    ) -> None:
        """This route is used to save all panel settings.

        The panel replaces every setting: absent fields become zero values, so always start
        from the result of `get_all()`. A blank secret keeps the stored value, use the
        `clear_*` arguments to remove it. Some changes only apply after `restart_panel()`.

        Arguments:
            settings (AllSetting): The panel settings.
            two_factor_code (str | int | None): The current two-factor code, required when
                two-factor authentication is on and this call disables or rebinds it.
            clear_tg_bot_token (bool): Whether to remove the stored Telegram bot token.
            clear_ldap_password (bool): Whether to remove the stored LDAP password.
            clear_smtp_password (bool): Whether to remove the stored SMTP password.
            clear_discord_bot_token (bool): Whether to remove the stored Discord bot token.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            settings = api.setting.get_all()
            settings.sub_title = "My subscription"
            api.setting.update(settings)
            ```
        """
        endpoint = "panel/api/setting/update"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = settings.model_dump(by_alias=True, exclude_defaults=True)
        if two_factor_code is not None:
            data["twoFactorCode"] = str(two_factor_code)
        clears = {
            "clearTgBotToken": clear_tg_bot_token,
            "clearLdapPassword": clear_ldap_password,
            "clearSmtpPassword": clear_smtp_password,
            "clearDiscordBotToken": clear_discord_bot_token,
        }
        data.update({key: True for key, clear in clears.items() if clear})
        self.logger.info("Updating panel settings...")

        self._post(url, headers, data)
        self.logger.info("Panel settings updated successfully.")

    def validate_regex(self, pattern: str) -> None:
        """This route is used to validate a regular expression with the panel's RE2 compiler.

        Nothing is saved. An invalid pattern raises ValueError with the compiler message.

        Arguments:
            pattern (str): The regular expression to validate.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.setting.validate_regex("(?m)^general-purpose$")
            ```
        """
        endpoint = "panel/api/setting/validateRegex"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {"regex": pattern}
        self.logger.info("Validating regular expression...")

        self._post(url, headers, data)

    def update_user(  # pylint: disable=R0913, R0917
        self,
        old_username: str,
        old_password: str,
        new_username: str,
        new_password: str,
        two_factor_code: str | int | None = None,
    ) -> None:
        """This route is used to change the panel admin username and password.

        Arguments:
            old_username (str): The current username.
            old_password (str): The current password.
            new_username (str): The new username. Must not be empty.
            new_password (str): The new password. Must not be empty.
            two_factor_code (str | int | None): The current two-factor code, required when
                two-factor authentication is on.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.setting.update_user("admin", "admin", "newadmin", "newpass")
            ```
        """
        endpoint = "panel/api/setting/updateUser"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        data = {
            "oldUsername": old_username,
            "oldPassword": old_password,
            "newUsername": new_username,
            "newPassword": new_password,
        }
        if two_factor_code is not None:
            data["twoFactorCode"] = str(two_factor_code)
        self.logger.info("Updating panel user...")

        self._post(url, headers, data)
        self.logger.info("Panel user updated successfully.")

    def restart_panel(self) -> None:
        """This route is used to restart the panel.

        The panel restarts after a 3 second delay, so requests fail until it is back.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.setting.restart_panel()
            ```
        """
        endpoint = "panel/api/setting/restartPanel"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Restarting the panel...")

        self._post(url, headers, {})

    def test_smtp(self) -> dict[str, Any]:
        """This route is used to send a test email and report the stage it reached.

        Unlike other methods, this one does not raise on a failed test: the result carries
        `success`, the `stage` it reached (`connect`, `auth`, `send`) and the message in `msg`.
        When the email service is unavailable the panel sends no `stage`.

        Returns:
            dict[str, Any]: The test result.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            result = api.setting.test_smtp()
            if not result["success"]:
                print(result.get("stage"), result["msg"])
            ```
        """
        endpoint = "panel/api/setting/testSmtp"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Testing SMTP...")

        response = self._post(url, headers, {}, skip_check=True)
        return response.json()

    def test_tg_bot(self) -> None:
        """This route is used to send a test message through the Telegram bot.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.setting.test_tg_bot()
            ```
        """
        endpoint = "panel/api/setting/testTgBot"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Testing the Telegram bot...")

        self._post(url, headers, {})

    def get_tg_bot_capabilities(self) -> TgBotCapabilities:
        """This route is used to retrieve what the Telegram bot can do.

        The panel responds with an error when the bot is disabled or not running.

        Returns:
            TgBotCapabilities: The bot capabilities.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            capabilities = api.setting.get_tg_bot_capabilities()
            print(capabilities.inline_enabled)
            ```
        """
        endpoint = "panel/api/setting/tgBotCapabilities"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting Telegram bot capabilities...")

        response = self._post(url, headers, {})
        return TgBotCapabilities.model_validate(response.json().get(ApiFields.OBJ))

    def test_discord(self) -> None:
        """This route is used to send a test notification through the Discord bot.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            api.setting.test_discord()
            ```
        """
        endpoint = "panel/api/setting/testDiscord"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Testing the Discord bot...")

        self._post(url, headers, {})

    def get_default_xray_config(self) -> dict[str, Any]:
        """This route is used to retrieve the default Xray config template of the panel.

        Returns:
            dict[str, Any]: The default Xray config.

        Examples:
            ```python
            import py3xui

            api = py3xui.Api.from_env()
            api.login()

            config = api.setting.get_default_xray_config()
            print(config["outbounds"])
            ```
        """
        endpoint = "panel/api/setting/getDefaultJsonConfig"
        headers = {"Accept": "application/json"}
        url = self._url(endpoint)
        self.logger.info("Getting default Xray config...")

        response = self._get(url, headers)
        return response.json().get(ApiFields.OBJ)
