Agent2Allow — Ship AI agents safely to production in 10 minutes — with deny-by-default permissions, human approvals, and auditable tool calls.

# Agent2Allow

Agent2Allow is an open-core tool gateway for AI agents.
It enforces policy, routes risky actions through approvals, and records auditable tool calls.

## 10-Minute Quickstart
```bash
docker compose up --build -d
npm run demo
```

Expected demo flow:
- deny-by-default blocks an unscoped repo call
- issue listing executes immediately
- write actions become pending approvals
- approvals execute queued actions
- audit log records all transitions

Smoke test script:
```bash
./scripts/smoke_mock_demo.sh
```

Policy change review helper:
```bash
./agent2allow policy-diff old-policy.yml new-policy.yml --strict
```

## Architecture Overview
- `gateway/`: policy enforcement, approval workflow, audit logging
- `ui/`: minimal operator UI for pending approvals and audit events
- `connectors/`: tool backends (GitHub mock in this repo)
- `sdk/`: thin JS/Python clients
- `examples/`: runnable integration examples

## Project Docs
- `docs/quickstart.md`
- `docs/concepts/policies.md`
- `docs/concepts/approvals.md`
- `docs/concepts/audit.md`
- `docs/deployment/docker.md`
- `docs/security/threat-model.md`
- `docs/security/incident-response.md`
- `docs/releasing.md`
- `CHANGELOG.md`

## Development
```bash
cd gateway && ruff check src tests
cd gateway && pytest
cd ui && npm run lint
cd ui && npm test
```
