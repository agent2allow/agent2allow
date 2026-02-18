# Threat Model (MVP)

## Assets
- Tool-call authorization decisions.
- Approval decisions and reasons.
- Audit logs and exported JSONL.
- GitHub access token (when real mode is enabled).

## Trust Boundaries
- Agent/client -> Gateway API.
- Gateway -> GitHub API (mock or real).
- Operator UI -> Gateway approval/audit endpoints.
- CI pipeline -> repository source and secrets.

## Primary Threats
1. Unauthorized write actions.
- Mitigation: deny-by-default policy + medium/high risk approval gating.

2. Secret leakage (tokens/keys in repo or logs).
- Mitigation: CI secret scan, CONTRIBUTING guidance, no token persistence in repo.

3. Audit tampering or missing event context.
- Mitigation: structured audit rows, schema version field, JSONL export for external retention.

4. Replay/duplicate write side effects.
- Mitigation: idempotency key handling with request hash binding.

5. Misconfigured policy scopes.
- Mitigation: policy validator, quickstart troubleshooting, policy wizard templates.

## Residual Risks
- Single-node SQLite is not immutable/audit-proof storage.
- Operator account hardening and RBAC are out-of-scope for current MVP.
