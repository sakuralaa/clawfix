#!/usr/bin/env sh
set -eu

STATE_DIR="/home/node/.openclaw"
AGENT_DIR="$STATE_DIR/agents/main/agent"
GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18799}"
HOST_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18799}"

mkdir -p "$STATE_DIR" "$AGENT_DIR" "/demo/workspace/project"

cat > "$STATE_DIR/openclaw.json" <<EOF
{
  "agents": {
    "defaults": {
      "workspace": "/demo/workspace/project",
      "sandbox": {
        "mode": "off"
      },
      "model": {
        "primary": "${OPENCLAW_PRIMARY_MODEL:-google/gemini-2.5-flash}"
      }
    }
  },
  "auth": {
    "profiles": {
      "google:default": {
        "provider": "google",
        "mode": "api_key"
      }
    },
    "order": {
      "google": ["google:default"]
    }
  },
  "gateway": {
    "bind": "lan",
    "port": ${GATEWAY_PORT},
    "auth": {
      "mode": "token",
      "token": "${OPENCLAW_GATEWAY_TOKEN}"
    },
    "controlUi": {
      "allowedOrigins": [
        "http://127.0.0.1:${HOST_GATEWAY_PORT}",
        "http://localhost:${HOST_GATEWAY_PORT}"
      ]
    },
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    }
  },
  "tools": {
    "profile": "coding",
    "fs": {
      "workspaceOnly": true
    }
  }
}
EOF

if [ -n "${GEMINI_API_KEY:-}" ]; then
  cat > "$AGENT_DIR/auth-profiles.json" <<EOF
{
  "version": 1,
  "profiles": {
    "google:default": {
      "type": "api_key",
      "provider": "google",
      "key": "${GEMINI_API_KEY}"
    }
  },
  "order": {
    "google": ["google:default"]
  }
}
EOF
fi

chown -R node:node "$STATE_DIR"

export OPENCLAW_CONFIG_PATH="$STATE_DIR/openclaw.json"
exec su node -s /bin/sh -c "export OPENCLAW_CONFIG_PATH=/home/node/.openclaw/openclaw.json && openclaw gateway run --allow-unconfigured --bind lan --port ${GATEWAY_PORT}"
