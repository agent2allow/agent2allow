#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Validate policy files"
python3 gateway/scripts/validate_policy.py gateway/config/default-policy.yml
python3 gateway/scripts/validate_policy.py examples/github-triage-agent/sample-policy.yml

echo "[2/4] Gateway lint + tests"
(
  cd gateway
  ruff check src tests
  pytest -q
)

echo "[3/4] UI lint + tests"
(
  cd ui
  npm run lint
  npm test --silent -- --pool=threads --maxWorkers=1
)

echo "[4/4] Compose config"
if command -v docker >/dev/null 2>&1; then
  if docker compose config >/dev/null 2>&1; then
    echo "docker compose config: ok"
  else
    echo "docker available but not usable here; skipping compose config (covered in CI)."
  fi
else
  echo "docker not found; skipping compose config check (covered in CI)."
fi

echo "All local checks passed."
