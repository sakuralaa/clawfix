#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "static-signals"
SIGNAL_DST = ROOT / "workspace" / "static-signals" / "current-findings.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["small", "large"], required=True)
    args = parser.parse_args()

    src = FIXTURE_DIR / f"{args.scenario}-findings.json"
    if not src.exists():
        raise SystemExit(f"missing signal fixture: {src}")

    SIGNAL_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, SIGNAL_DST)
    print(f"copied static signals: {src} -> {SIGNAL_DST}")


if __name__ == "__main__":
    main()
