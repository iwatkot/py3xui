# Models

py3xui uses Pydantic models for API payload validation and parsing.

Core models include:
- `Inbound`
- `Client`
- `ServerStatus`
- `ServerConfig`

When the upstream panel response shape changes, py3xui adapts parsing logic while preserving stable public methods where possible.

## Sub Balancers API (3x-ui v3.11.0)

`SubBalancer` is a client-side balancer of the JSON subscription. Fields: `id`, `remark`, `strategy`, `inbound_ids`, `member_weights`, `sort_order`, `enabled`, `created_at`, `updated_at`. `remark` and `inbound_ids` are required. Unknown fields returned by the panel are kept on the model.

`SubBalancer.to_form()` returns the form fields sent to the panel.
