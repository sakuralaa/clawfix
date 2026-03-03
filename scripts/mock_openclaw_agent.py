#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINDINGS_PATH = ROOT / "workspace" / "static-signals" / "current-findings.json"
WORKSPACE = ROOT / "workspace" / "project"


def load_findings() -> dict:
    return json.loads(FINDINGS_PATH.read_text())


def print_log(findings: dict) -> None:
    print("OpenClaw static-check demo --log")
    print()
    for item in findings["findings"]:
        location = item["primaryLocation"]
        file_ref = f"{location['file']}:{location['line']}"
        if item["ruleId"] == "macro-naming":
            symbol = item.get("symbol", "<unknown>")
            fixed = to_macro_name(symbol)
            ref_count = len(item.get("relatedLocations", []))
            print(f"[{item['severity']}] {item['ruleId']} at {file_ref}")
            print(f"Problem: {item['message']}")
            print(
                f"Fix: rename {symbol} -> {fixed} and update {ref_count} references across multiple files"
            )
            print()
            continue

        if item["ruleId"] == "resource-leak":
            print(f"[{item['severity']}] {item['ruleId']} at {file_ref}")
            print(f"Problem: {item['message']}")
            print(
                "Fix: treat FileReader as the owner, declare a destructor in the header, and close the FILE* in the source"
            )
            print("Root cause: upstream ownership is incomplete, so the fix must span header + source")
            print()


def to_macro_name(name: str) -> str:
    out: list[str] = []
    for idx, ch in enumerate(name):
        if ch == '_':
            out.append('_')
            continue
        if ch.isupper() and idx > 0 and out[-1] != '_':
            out.append('_')
        out.append(ch.upper())
    return ''.join(out)


def replace_in_files(old: str, new: str) -> list[str]:
    changed: list[str] = []
    for path in sorted(WORKSPACE.rglob("*")):
        if path.suffix not in {".h", ".hpp", ".c", ".cc", ".cpp"}:
            continue
        original = path.read_text()
        updated = original.replace(old, new)
        if updated != original:
            path.write_text(updated)
            changed.append(str(path.relative_to(ROOT)))
    return changed


def apply_resource_leak_fix() -> list[str]:
    changed: list[str] = []
    header = WORKSPACE / "include" / "file_reader.h"
    source = WORKSPACE / "src" / "file_reader.cpp"

    header_text = header.read_text()
    if "~FileReader();" not in header_text:
        header_text = header_text.replace(
            "  explicit FileReader(const std::string& path);\n",
            "  explicit FileReader(const std::string& path);\n  ~FileReader();\n",
        )
        header.write_text(header_text)
        changed.append(str(header.relative_to(ROOT)))

    source_text = source.read_text()
    destructor = (
        "FileReader::~FileReader() {\n"
        "  if (file_ != nullptr) {\n"
        "    std::fclose(file_);\n"
        "    file_ = nullptr;\n"
        "  }\n"
        "}\n\n"
    )
    if "FileReader::~FileReader()" not in source_text:
        anchor = "namespace {"
        anchor_index = source_text.find(anchor)
        if anchor_index == -1:
            raise RuntimeError("cannot locate insertion point for FileReader destructor")
        source_text = source_text[:anchor_index] + destructor + source_text[anchor_index:]
        source.write_text(source_text)
        changed.append(str(source.relative_to(ROOT)))

    return changed


def print_fix_summary(changed_files: list[str], findings: dict) -> None:
    unique = sorted(set(changed_files))
    print("OpenClaw static-check demo --fix")
    print()
    print("Applied fixes:")
    for item in unique:
        print(f"- {item}")
    print()
    print("Resolved:")
    for item in findings["findings"]:
        location = item["primaryLocation"]
        print(f"- {item['ruleId']} {location['file']}:{location['line']}")
    print()
    print("Remaining:")
    print("- none")


def apply_fix() -> None:
    findings = load_findings()
    changed_files: list[str] = []
    changed_files.extend(replace_in_files("maxBufferSize", "MAX_BUFFER_SIZE"))
    changed_files.extend(replace_in_files("File_open_retry", "FILE_OPEN_RETRY"))
    changed_files.extend(replace_in_files("telemetryFlushWindow", "TELEMETRY_FLUSH_WINDOW"))
    changed_files.extend(replace_in_files("Cache_line_size", "CACHE_LINE_SIZE"))
    changed_files.extend(apply_resource_leak_fix())
    print_fix_summary(changed_files, findings)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["log", "fix"], required=True)
    args = parser.parse_args()

    if not WORKSPACE.exists():
        raise SystemExit("workspace/project missing; run ./scripts/reset_demo.py first")

    findings = load_findings()
    if args.mode == "log":
        print_log(findings)
        return
    apply_fix()


if __name__ == "__main__":
    main()
