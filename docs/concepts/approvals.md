# Approvals

## Flow
1. Agent requests a tool call.
2. Policy marks action as approval-required.
3. Gateway creates pending approval in SQLite.
4. Human approves or denies in API/UI.
5. Gateway logs every state transition in audit log.

## Endpoints
- `GET /v1/approvals/pending`
- `POST /v1/approvals/{id}/approve`
- `POST /v1/approvals/{id}/deny`
