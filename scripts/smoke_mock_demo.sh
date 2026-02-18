#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

cleanup() {
  docker compose down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "[smoke] starting gateway + mock-github"
docker compose up -d --build gateway mock-github

echo "[smoke] waiting for gateway readiness"
for _ in {1..45}; do
  if curl -fsS http://localhost:8000/ready >/dev/null; then
    break
  fi
  sleep 1
done
curl -fsS http://localhost:8000/ready >/dev/null

echo "[smoke] running demo"
DEMO_OUTPUT="$(npm run -s demo)"
echo "$DEMO_OUTPUT"

for expected in \
  "Deny-by-default check: denied" \
  "Read call: executed" \
  "Pending approvals:" \
  "Approved" \
  "Audit events total:"; do
  if ! grep -q "$expected" <<<"$DEMO_OUTPUT"; then
    echo "[smoke] missing expected demo output: $expected"
    exit 1
  fi
done

echo "[smoke] success"
