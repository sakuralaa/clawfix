#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="$ROOT/workspace/project"
OUT="$WORKSPACE/demo_app"

if [[ ! -d "$WORKSPACE" ]]; then
  echo "workspace missing: $WORKSPACE"
  echo "run ./scripts/reset_demo.py first"
  exit 1
fi

cd "$WORKSPACE"
g++ -std=c++17 -Wall -Wextra -Iinclude src/*.cpp -o "$OUT"
./demo_app
