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

Audit rows include:
- timestamp
- agent_id
- tool/action/repo
- request and response payload
- status and optional approval reference
