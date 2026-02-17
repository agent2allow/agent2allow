Ship AI agents safely to production in 10 minutes — with deny-by-default permissions, human approvals, and auditable tool calls.

# Agent2Allow

Agent2Allow is an OSS-first open-core tool firewall/gateway for AI agents.
It sits between an agent and external tools (GitHub in MVP), enforces policy, requests approvals for risky actions, and writes a complete audit trail.

## 10-Minute Quickstart
```bash
docker compose up --build -d
npm run demo
```

Then open:
- Gateway API: `http://localhost:8000`
- UI: `http://localhost:5173`

## Demo Outcome (`npm run demo`)
- Denied call without matching policy scope.
- Read-only issue listing executes directly.
- Write actions become pending approvals.
- After approval, labels/comments execute.
- Audit log records the entire chain.

## Why It Is Safe By Default
- `deny-by-default`: no rule match means blocked.
- allowlist by `tool + action + repo` scope.
- risk-aware gating: `medium/high` requires approval.
- centralized execution path writes audit events for every decision.

## How to Add a Connector
See `docs/concepts/connectors.md`.

## Repository Layout
- `gateway/` FastAPI gateway, policy engine, approvals, audit, tests
- `ui/` minimal React UI for pending approvals and audit log
- `connectors/github/` mock GitHub API for local demo
- `sdk/js/` and `sdk/python/` thin clients
- `examples/github-triage-agent/` end-to-end triage script and policy sample
- `docs/` concepts, quickstart, deployment, plan

## Phase Checklist
- [x] DISCUSS/EXPLORE
- [x] PLAN
- [x] EXECUTE

## Roadmap
### MVP (dieses Repo)
- Deny-by-default Policy-Enforcer (YAML DSL)
- Human Approval Flow (pending, approve, deny)
- Audit Log in SQLite + JSONL Export
- GitHub Connector (issues list, labels, comments)
- Minimal UI (Approvals + Audit)
- Node + Python SDK Clients
- Mock-first 10-minute demo
- CI: gateway tests + UI tests + compose validation

### Später (Open Core Expansion)
- SSO/RBAC und Multi-Tenant
- OPA/Rego policy backend
- Signierte/tamper-evident Audit Chains
- Weitere Connectoren (Jira, Slack, DB, ERP)
- Queue/Worker für asynchrone long-running Actions

## Useful Commands
- `cd gateway && pytest`
- `cd ui && npm test`
- `npm run demo`
