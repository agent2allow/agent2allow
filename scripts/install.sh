#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: install.sh [--with-demo]

Run Agent2Allow bootstrap directly from a local checkout or by cloning
agent2allow for first-time setup.

Options:
  --with-demo   run the demo after services are ready
  --help        show this message

Environment overrides:
  AGENT2ALLOW_REPO_URL     repository to clone from
  AGENT2ALLOW_INSTALL_DIR  fixed checkout directory for one-time installs
USAGE
}

if [[ "${1-}" == "--help" || "${1-}" == "-h" ]]; then
  usage
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BOOTSTRAP_SCRIPT="$LOCAL_REPO_ROOT/scripts/bootstrap.sh"

if [[ -f "$BOOTSTRAP_SCRIPT" ]]; then
  echo "[install] detected local Agent2Allow checkout"
  exec bash "$BOOTSTRAP_SCRIPT" "$@"
fi

if ! command -v git >/dev/null 2>&1; then
  echo "git is required for remote one-shot install."
  exit 1
fi

REPO_URL="${AGENT2ALLOW_REPO_URL:-https://github.com/agent2allow/agent2allow.git}"
TARGET_DIR="${AGENT2ALLOW_INSTALL_DIR:-}"

if [[ -n "$TARGET_DIR" ]]; then
  if [[ ! -d "$TARGET_DIR" ]]; then
    echo "[install] cloning Agent2Allow into ${TARGET_DIR}"
    git clone --depth 1 "$REPO_URL" "$TARGET_DIR"
  fi
  if [[ ! -f "$TARGET_DIR/scripts/bootstrap.sh" ]]; then
    echo "No Agent2Allow checkout found in ${TARGET_DIR}"
    exit 1
  fi
  exec bash "$TARGET_DIR/scripts/bootstrap.sh" "$@"
fi

WORK_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

PROJECT_DIR="$WORK_DIR/agent2allow"
echo "[install] cloning Agent2Allow into temporary workspace"
git clone --depth 1 "$REPO_URL" "$PROJECT_DIR"
bash "$PROJECT_DIR/scripts/bootstrap.sh" "$@"
