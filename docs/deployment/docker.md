# Docker Deployment

## Local Stack
```bash
docker compose up --build -d
```
Services:
- `gateway` on :8000
- `ui` on :5173
- `mock-github` on :8081

## Policy and Data
- Policy file mounted in image: `gateway/config/default-policy.yml`
- SQLite file in container: `/app/gateway/data/agent2allow.db`
