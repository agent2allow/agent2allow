# Contributing

## Setup
1. Start services: `docker compose up --build -d`
2. Run gateway tests: `cd gateway && pip install -r requirements-dev.txt && pytest`
3. Run UI tests: `cd ui && npm install && npm test`

## Development Guidelines
- Keep deny-by-default behavior intact.
- Add tests for policy or approval flow changes.
- Do not commit credentials or tokens.

## Pull Requests
- Describe behavior change and security impact.
- Include test evidence.
- Update docs when API or policy schema changes.
