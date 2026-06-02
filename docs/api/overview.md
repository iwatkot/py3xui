# API Overview

Both clients expose the same high-level surface:

- `inbound` operations
- `client` operations
- `server` operations
- `database` operations

Choose one style:
- `Api` for blocking/synchronous flows
- `AsyncApi` for async event-loop based flows

The SDK keeps compatibility-focused method signatures even when upstream endpoint semantics evolve.
