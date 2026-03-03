#!/usr/bin/env sh
set -eu

STATE_DIR="/home/node/.openclaw"
AGENT_DIR="$STATE_DIR/agents/main/agent"

mkdir -p "$STATE_DIR" "$AGENT_DIR" "/demo/workspace/project"

cat > "$STATE_DIR/openclaw.json" <<EOF
{
  "agents": {
    "defaults": {
      "workspace": "/demo/workspace/project",
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
    "controlUi": {
      "allowedOrigins": [
        "http://127.0.0.1:${OPENCLAW_GATEWAY_PORT:-18799}",
        "http://localhost:${OPENCLAW_GATEWAY_PORT:-18799}"
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

exec su node -s /bin/sh -c 'cd /app && node dist/index.js gateway --allow-unconfigured --bind lan --port 18789'
