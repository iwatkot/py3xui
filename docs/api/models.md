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
