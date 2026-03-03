#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODE="${1:-log}"

cat <<MSG
Real OpenClaw command shape for this demo:

openclaw agent \
  --local \
  --agent static-check-fixer \
  --message "Read agent/STATIC_CHECK_AGENT.md, analyze workspace/static-signals/current-findings.json against workspace/project, and run mode=$MODE" \
  --thinking medium

This machine does not currently have a runnable openclaw binary installed, so use:
  ./scripts/mock_openclaw_agent.py --mode $MODE
MSG
