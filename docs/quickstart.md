# 10-Minute Quickstart

## Prerequisites
- Docker + Docker Compose
- Node.js 20+ (for `npm run demo`)
- Python 3.11+ (for demo script)

## 1. Start Agent2Allow
```bash
docker compose up --build -d
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

## Optional Real GitHub Mode
```bash
export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPO=owner/repo
export GITHUB_BASE_URL=https://api.github.com
npm run demo
```
