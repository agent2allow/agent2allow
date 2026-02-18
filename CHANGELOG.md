# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]
### Added
- Optional SDK OpenAPI export/type generation flow:
  - `scripts/export_openapi.py`
  - `sdk/js/scripts/generate_openapi_types.mjs`
  - `sdk/python/scripts/generate_openapi_types.py`
- Lightweight approval RBAC guards on approve/deny/bulk approval endpoints.
- External audit sink adapter framework (`none`, `syslog`, `s3`, `blob`).
- Policy diff/check CLI: `gateway/scripts/policy_diff.py` and `./agent2allow policy-diff`.
- Optional API key auth for approval mutation endpoints (`X-Approval-Api-Key`).

## [0.1.0] - 2026-02-18
### Added
- Deny-by-default policy enforcement with approval workflow and audit logging.
- Mock-first GitHub triage demo with deterministic smoke test.
- Retry/backoff and idempotency support for tool calls.
- Approval UI with bulk actions and reason presets.
- Audit schema versioning and JSONL export support.
- Policy validation and policy wizard scaffolds.
- Connector contract checks and connector authoring template.
- Local diagnostics command: `./agent2allow doctor`.

### Security
- Secret pattern scanning in CI.
- Responsible disclosure policy and threat model docs.
- Optional real-mode safety tests for GitHub read-only checks.
