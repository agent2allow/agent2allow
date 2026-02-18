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
9. Approval reason presets in UI.
10. Policy wizard CLI scaffold for common templates.
11. Real-mode safety integration tests (optional, env-gated).
12. Container health checks and startup readiness probes.
13. UI system status banner and local doctor diagnostics command.
14. Release hygiene docs (`CHANGELOG.md`, release guide).
15. Security operations docs (threat model + incident response).
16. Manual real-mode safety GitHub workflow.

## Next
1. Optional typed OpenAPI client generation for SDKs.
2. Add lightweight RBAC for approval actions.
3. Add persistent external audit sink (S3/Blob/syslog) adapter.
4. Add policy diff/check command for change reviews.
