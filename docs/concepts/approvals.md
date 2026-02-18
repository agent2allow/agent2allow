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
- `POST /v1/approvals/bulk`

## Optional RBAC
Approval RBAC can be enabled with environment settings:
- `APPROVAL_RBAC_ENABLED=true`
- `APPROVAL_ROLE_BINDINGS` as JSON user->role map (example: `{"alice":"reviewer","bob":"admin"}`)
- `APPROVAL_ROLES_FOR_APPROVE`, `APPROVAL_ROLES_FOR_DENY`
- `APPROVAL_ROLES_FOR_HIGH_RISK_APPROVE` (default: `admin`)

When enabled:
- approvers without a mapped role receive `403`
- high-risk approvals can be restricted to admin-only roles
