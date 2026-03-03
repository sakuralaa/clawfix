#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

OPENCLAW_REPO_PATH="${OPENCLAW_REPO_PATH:-../openclaw}"

if [ ! -d "$OPENCLAW_REPO_PATH" ]; then
  echo "OPENCLAW_REPO_PATH does not exist: $OPENCLAW_REPO_PATH" >&2
  echo "Set OPENCLAW_REPO_PATH in .env to a local OpenClaw checkout." >&2
  exit 1
fi

if [ ! -f "$OPENCLAW_REPO_PATH/Dockerfile" ]; then
  echo "OPENCLAW_REPO_PATH is missing a Dockerfile: $OPENCLAW_REPO_PATH" >&2
  exit 1
fi

docker compose up -d --build openclaw-gateway

READY_PORT="${OPENCLAW_GATEWAY_PORT:-18799}"
READY_HOST="127.0.0.1"
READY_TIMEOUT_SECONDS="${OPENCLAW_STARTUP_TIMEOUT_SECONDS:-30}"

python3 - <<PY
import socket
import sys
import time

host = "${READY_HOST}"
port = int("${READY_PORT}")
deadline = time.time() + int("${READY_TIMEOUT_SECONDS}")

while time.time() < deadline:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    try:
        sock.connect((host, port))
    except OSError:
        time.sleep(1.0)
    else:
        sock.close()
        print(f"OpenClaw gateway is ready on {host}:{port}")
        sys.exit(0)
    finally:
        try:
            sock.close()
        except OSError:
            pass

print(f"Timed out waiting for OpenClaw gateway on {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
