# Repo Map

## Entry Points
- Gateway API: `gateway/src/main.py`
- Mock connector API: `connectors/github/mock_server.py`
- UI app: `ui/src/main.jsx`
- Demo script: `examples/github-triage-agent/triage.py`

## Core Modules
- Policy: `gateway/src/policy.py`
- Tool execution + approvals + audit: `gateway/src/service.py`
- DB models: `gateway/src/models.py`
- GitHub connector client: `gateway/src/connectors/github_client.py`

## Build/Test Surface
- Gateway tests: `cd gateway && pytest -q`
- UI tests: `cd ui && npm test --silent`
- UI lint: `cd ui && npm run lint`
- Gateway lint: `cd gateway && ruff check src tests`

## Demo Flow
1. Start gateway + mock github.
2. Run `npm run demo`.
3. Verify deny-by-default, pending approvals, execution after approval, audit entries.
