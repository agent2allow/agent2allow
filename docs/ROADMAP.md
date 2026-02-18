# Roadmap

## Completed
1. Idempotency keys for `/v1/tool-calls` to prevent duplicate writes.
2. Retry/backoff behavior in GitHub connector with explicit tests.
3. Policy schema validation CLI.
4. SDK quickstart snippets with approval examples (JS + Python).
5. Denied-call troubleshooting guide with concrete checks.
6. Bulk approval UI and bulk approval API endpoint.
7. Audit event `schema_version` with SQLite-safe startup migration.
8. Connector authoring template and runtime contract checks.

## Next
1. Approval reason presets in UI.
2. Policy wizard CLI scaffold for common templates.
3. Expand integration tests for real-mode safety checks.
4. Add container health checks and startup readiness probes.
5. Optional typed OpenAPI client generation for SDKs.
