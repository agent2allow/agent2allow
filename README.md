Agent2Allow — Ship AI agents safely to production in 10 minutes — with deny-by-default permissions, human approvals, and auditable tool calls.

# Agent2Allow

Agent2Allow is an open-core tool gateway for AI agents.
It enforces policy, routes risky actions through approvals, and records auditable tool calls.

## Quickstart (placeholder)
```bash
docker compose up --build -d
npm run demo
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

## Development
```bash
cd gateway && pytest
cd ui && npm test
```
