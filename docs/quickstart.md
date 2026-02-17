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

## Optional Real GitHub Mode
```bash
export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPO=owner/repo
export GITHUB_BASE_URL=https://api.github.com
npm run demo
```
