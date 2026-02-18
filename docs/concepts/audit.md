# Audit

Each tool call emits structured audit events:
- denied
- pending_approval
- approved / denied_by_human
- executed / error

## Storage
- SQLite table: `audit_logs`
- Export endpoint: `GET /v1/audit/export` (JSONL)
- UI includes status/repo/action filters and per-event detail expansion for fast triage
- Optional external sink adapters:
  - `AUDIT_SINK=syslog`
  - `AUDIT_SINK=s3` (requires `boto3`)
  - `AUDIT_SINK=blob` (requires `azure-storage-blob`)

Audit rows include:
- timestamp
- agent_id
- tool/action/repo
- request and response payload
- status and optional approval reference
- `schema_version` for forward-compatible parsing (current: `1`)

## Schema Versioning
- All new audit records include `schema_version=1`.
- API surfaces this field in:
  - `GET /v1/audit`
  - `GET /v1/audit/export` JSONL lines
- Startup migration adds missing `schema_version` column for existing SQLite databases.
