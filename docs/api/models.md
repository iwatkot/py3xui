# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ServerStatus`
- `ServerConfig`

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.

## Settings API (3x-ui v3.11.0)

- `AllSetting`: every panel setting, returned by `api.setting.get_all()` and accepted by `api.setting.update()`. Unknown keys are kept and sent back. The `has_*` flags are read-only and left out of `model_dump()`.
- `TgBotCapabilities`: what the Telegram bot can do, returned by `api.setting.get_tg_bot_capabilities()`.
- `ApiToken`: an API token, returned by `api.setting.get_api_tokens()` and `api.setting.add_api_token()`. `token` is filled only by `add_api_token()`. `created_at` is in Unix seconds and `expires_at` in Unix milliseconds.
