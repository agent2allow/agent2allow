# Docker Deployment

## Local Stack
```bash
docker compose up --build -d
```
Services:
- `gateway` on :8000
- `ui` on :5173
- `mock-github` on :8081
- Healthchecks:
  - gateway: `GET /ready`
  - mock-github: `GET /health`
  - ui: HTTP fetch to `/`

## Policy and Data
- Policy file mounted in image: `gateway/config/default-policy.yml`
- SQLite file in container: `/app/gateway/data/agent2allow.db`

## Probe Endpoints
- Liveness: `GET /health` (gateway)
- Readiness: `GET /ready` (gateway, verifies service init + DB + policy file)
