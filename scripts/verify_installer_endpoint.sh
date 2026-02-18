#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(mktemp -d)"
SERVER_PID=""

cleanup() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT

log() {
  echo "[verify-installer] $*"
}

fail() {
  echo "[verify-installer] ERROR: $*" >&2
  exit 1
}

mkdir -p "$WORK_DIR/installer-site"
cp "$SCRIPT_DIR/install.sh" "$WORK_DIR/installer-site/install.sh"
cp "$SCRIPT_DIR/installer-page.html" "$WORK_DIR/installer-site/index.html"
echo "get.agent2allow.com" > "$WORK_DIR/installer-site/CNAME"

cat > "$WORK_DIR/serve.py" <<'PY'
import http.server
import socketserver
import sys


directory = sys.argv[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)


with socketserver.TCPServer(("127.0.0.1", 0), Handler) as httpd:
    print(httpd.server_address[1], flush=True)
    httpd.serve_forever()
PY

python3 "$WORK_DIR/serve.py" "$WORK_DIR/installer-site" \
  > "$WORK_DIR/server-port.log" 2>/dev/null &
SERVER_PID=$!

for attempt in $(seq 1 80); do
  if [ -s "$WORK_DIR/server-port.log" ]; then
    break
  fi
  sleep 0.05
done

if [ ! -s "$WORK_DIR/server-port.log" ]; then
  fail "Installer server did not start."
fi

PORT="$(head -n 1 "$WORK_DIR/server-port.log" | tr -d '\r')"
if [ -z "$PORT" ]; then
  fail "Could not read installer server port."
fi

if ! command -v curl >/dev/null 2>&1; then
  fail "curl is required for verification."
fi

curl -fsSL "http://127.0.0.1:${PORT}/" -o "$WORK_DIR/index.html"
curl -fsSL "http://127.0.0.1:${PORT}/install.sh" -o "$WORK_DIR/install.sh"

if ! grep -q "<title>Agent2Allow Installer</title>" "$WORK_DIR/index.html"; then
  fail "Installer landing page title is missing."
fi

if grep -q "^#\\!" "$WORK_DIR/index.html"; then
  fail "Landing page should be HTML, not a shell script."
fi

if ! head -n 1 "$WORK_DIR/install.sh" | grep -q "^#!/usr/bin/env bash$"; then
  fail "install.sh is not executable shell script content."
fi

if ! grep -q "Usage: install.sh" "$WORK_DIR/install.sh"; then
  fail "install.sh usage helper is missing."
fi

bash -n "$WORK_DIR/install.sh" || fail "install.sh syntax check failed."

log "Local endpoint smoke checks passed."
log "Landing page:  http://127.0.0.1:${PORT}/"
log "Script path:   http://127.0.0.1:${PORT}/install.sh"
log "Verifier finished."
