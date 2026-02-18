#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/bootstrap.sh [--with-demo]

Install/run the development stack for Agent2Allow.

Options:
  --with-demo   run the demo script after services are ready.
  --help        show this message.
USAGE
}

WITH_DEMO=0
for arg in "$@"; do
  case "$arg" in
    --with-demo)
      WITH_DEMO=1
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      usage
      exit 1
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required. Install Docker first."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose is required. Install a modern Docker Compose plugin."
  exit 1
fi

echo "[bootstrap] starting gateway + mock services"
docker compose up --build -d
echo "[bootstrap] waiting for gateway readiness"
for _ in {1..45}; do
  if curl -fsS http://localhost:8000/ready >/dev/null; then
    break
  fi
  sleep 1
done
curl -fsS http://localhost:8000/ready >/dev/null

echo "[bootstrap] services are ready"
echo "[bootstrap] UI: http://localhost:5173"
echo "[bootstrap] API: http://localhost:8000"

if [[ "$WITH_DEMO" == "1" ]]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required for demo; install Node.js and retry with --with-demo."
    exit 1
  fi
  echo "[bootstrap] running demo"
npm run -s demo
fi
