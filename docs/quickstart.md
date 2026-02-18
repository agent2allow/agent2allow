# 10-Minute Quickstart

## Prerequisites
- Docker + Docker Compose
- Node.js 20+ (for `npm run demo`)
- Python 3.11+ (for demo script)

## 1. Start Agent2Allow
```bash
docker compose up --build -d
```
Readiness check:
```bash
curl -fsS http://localhost:8000/ready
```

## 2. Run Demo Triage (Mock Mode)
```bash
npm run demo
```

Expected behavior:
- denied call for non-allowed repo
- read issue list allowed
- write actions become pending approvals
- approvals are executed
- audit records visible

## 3. Open UI
- http://localhost:5173
- Use bulk approval actions from "Pending Approvals":
  - select one or more items
  - `Approve selected` or `Deny selected`

## 4. Run deterministic smoke check
```bash
./scripts/smoke_mock_demo.sh
```

## 5. SDK copy-paste examples
- JavaScript: `sdk/js/README.md`
- Python: `sdk/python/README.md`
- For retriable agent loops, send `X-Idempotency-Key` per tool call.
- If the same key is replayed with the same payload, response includes `idempotent_replay=true`.

## 6. Run all local checks in one command
```bash
./scripts/dev_check.sh
```

Run local diagnostics:
```bash
./agent2allow doctor
```
Machine-readable diagnostics:
```bash
./agent2allow doctor --json
```
Strict mode (fail on warnings too):
```bash
./agent2allow doctor --strict
```

## 7. Add a connector
- Start with `connectors/template/README.md`.
- Follow `docs/concepts/connectors.md` for contract and test requirements.

## 8. Generate a policy template
```bash
python3 gateway/scripts/policy_wizard.py \
  --template triage-standard \
  --repo acme/roadrunner \
  --out ./tmp/policy.yml
```

## 9. Diff policy changes before rollout
```bash
./agent2allow policy-diff gateway/config/default-policy.yml ./tmp/policy.yml --strict
```

## 10. Generate SDK OpenAPI types (optional)
```bash
python3 scripts/export_openapi.py
cd sdk/js && npm run openapi:types
python3 sdk/python/scripts/generate_openapi_types.py
```

## Troubleshooting
- If demo says `Gateway not reachable`, confirm `http://localhost:8000/health`.
- If ports are busy, stop old containers: `docker compose down`.
- If Node deps mismatch, run `cd ui && npm ci`.

### Denied tool call (`decision=deny`)
1. Confirm the tool call payload (`tool`, `action`, `resource.repo`) matches your policy rule.
2. Verify policy loaded in gateway:
   - run `docker compose logs gateway | rg -n "policy|deny|allow|approval"`
3. Check rule scope:
   - `tool` must be `github`
   - `actions` must include exact action name (`issues.list`, `issues.set_labels`, `issues.create_comment`)
   - `repo` must match `owner/name` (glob patterns allowed where configured)
4. If action risk is `medium` or `high`, expect `pending_approval` instead of immediate execution.
5. Open UI (`http://localhost:5173`) and approve/deny from Pending Approvals.
6. Validate final state in audit log UI or export JSONL and inspect `decision` and `error` fields.
7. For parser compatibility, rely on audit `schema_version` (currently `1`) in API and export payloads.
8. For high-volume triage, use bulk approvals (`POST /v1/approvals/bulk`) from UI or API client.

## Optional Real GitHub Mode
```bash
export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPO=owner/repo
export GITHUB_BASE_URL=https://api.github.com
npm run demo
```

Optional real-mode safety tests (non-destructive, skipped by default):
```bash
export REAL_GITHUB_ENABLE_TESTS=true
export REAL_GITHUB_REPO=owner/repo
cd gateway && pytest -q tests/test_real_mode_safety.py
```
Optional auth for higher rate limits:
```bash
export REAL_GITHUB_TOKEN=ghp_xxx
```

## Optional Approval RBAC
Enable lightweight role checks for approval decisions:

```bash
export APPROVAL_RBAC_ENABLED=true
export APPROVAL_ROLE_BINDINGS='{"alice":"reviewer","bob":"admin"}'
export APPROVAL_ROLES_FOR_APPROVE=reviewer,admin
export APPROVAL_ROLES_FOR_HIGH_RISK_APPROVE=admin
```

## Optional Approval API Key Auth
Require API key auth on approval mutation endpoints:
```bash
export APPROVAL_API_KEY_ENABLED=true
export APPROVAL_API_KEYS='{"k-ops":"ops-reviewer"}'
```

Send header:
```bash
curl -X POST http://localhost:8000/v1/approvals/1/approve \
  -H "Content-Type: application/json" \
  -H "X-Approval-Api-Key: k-ops" \
  -d '{"approver":"ignored-when-api-key-enabled","reason":"safe change"}'
```

## Optional External Audit Sink
Forward every audit event to an external sink:

```bash
# syslog
export AUDIT_SINK=syslog
export AUDIT_SINK_SYSLOG_HOST=localhost
export AUDIT_SINK_SYSLOG_PORT=514
export AUDIT_SINK_SYSLOG_FACILITY=user
```

For cloud sinks set `AUDIT_SINK=s3` or `AUDIT_SINK=blob` and provide the matching bucket/container env vars.

Manual GitHub workflow alternative:
- Configure repo secret `REAL_GITHUB_TOKEN`.
- Run workflow `Real-Mode Safety` and provide `github_repo` input.
