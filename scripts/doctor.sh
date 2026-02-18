#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

JSON_MODE=false
STRICT_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      JSON_MODE=true
      shift
      ;;
    --strict)
      STRICT_MODE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./agent2allow doctor [--json] [--strict]"
      exit 1
      ;;
  esac
done

errors=0
warnings=0
report_file="$(mktemp)"
trap 'rm -f "$report_file"' EXIT

record() {
  local level="$1"
  local message="$2"
  printf '%s\t%s\n' "$level" "$message" >> "$report_file"
}

ok() {
  echo "[ok] $1"
  record "ok" "$1"
}

warn() {
  echo "[warn] $1"
  warnings=$((warnings + 1))
  record "warn" "$1"
}

err() {
  echo "[error] $1"
  errors=$((errors + 1))
  record "error" "$1"
}

echo "Agent2Allow Doctor"
echo "Workspace: $ROOT_DIR"

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "docker daemon reachable"
    if docker compose config >/dev/null 2>&1; then
      ok "docker compose config valid"
    else
      warn "docker compose config failed"
    fi
  else
    warn "docker installed but daemon not reachable (common in WSL without integration)"
  fi
else
  warn "docker not found"
fi

if python3 gateway/scripts/validate_policy.py gateway/config/default-policy.yml >/dev/null 2>&1; then
  ok "default policy template valid"
else
  err "default policy template invalid"
fi

if python3 gateway/scripts/validate_policy.py examples/github-triage-agent/sample-policy.yml >/dev/null 2>&1; then
  ok "sample policy template valid"
else
  err "sample policy template invalid"
fi

if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
  ok "gateway /health reachable"
else
  warn "gateway /health not reachable"
fi

if curl -fsS http://localhost:8000/ready >/dev/null 2>&1; then
  ok "gateway /ready reachable"
else
  warn "gateway /ready not reachable"
fi

if curl -fsS http://localhost:8081/health >/dev/null 2>&1; then
  ok "mock-github /health reachable"
else
  warn "mock-github /health not reachable"
fi

if curl -fsS http://localhost:5173 >/dev/null 2>&1; then
  ok "ui reachable"
else
  warn "ui not reachable"
fi

echo "Summary: errors=$errors warnings=$warnings strict=$STRICT_MODE"

if [[ "$JSON_MODE" == "true" ]]; then
  REPORT_FILE="$report_file" ERRORS="$errors" WARNINGS="$warnings" STRICT_MODE="$STRICT_MODE" python3 - <<'PY'
import json
import os
from pathlib import Path

entries = []
for line in Path(os.environ["REPORT_FILE"]).read_text(encoding="utf-8").splitlines():
    level, message = line.split("\t", 1)
    entries.append({"level": level, "message": message})

payload = {
    "summary": {
        "errors": int(os.environ["ERRORS"]),
        "warnings": int(os.environ["WARNINGS"]),
        "strict": os.environ["STRICT_MODE"].lower() == "true",
    },
    "checks": entries,
}
print(json.dumps(payload, indent=2))
PY
fi

if [[ "$errors" -gt 0 ]]; then
  exit 1
fi
if [[ "$STRICT_MODE" == "true" && "$warnings" -gt 0 ]]; then
  exit 2
fi
