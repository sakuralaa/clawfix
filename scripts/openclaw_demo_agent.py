#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any
from urllib import parse
from urllib import error, request
from uuid import uuid4
import socket

from mock_openclaw_agent import apply_fix


ROOT = Path(__file__).resolve().parent.parent
AGENT_PATH = ROOT / "agent" / "STATIC_CHECK_AGENT.md"
FINDINGS_PATH = ROOT / "workspace" / "static-signals" / "current-findings.json"
WORKSPACE = ROOT / "workspace" / "project"
LOG_DIR = ROOT / "logs" / "openclaw-runs"
LOG_PATH = LOG_DIR / "openclaw-demo.log"


class OpenClawCallError(RuntimeError):
    pass


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[key] = value


def _require_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or not value.strip():
        raise SystemExit(f"{name} is required")
    return value.strip()


def _extract_web_search_queries(delta: dict[str, Any]) -> list[str]:
    queries: list[str] = []
    tool_calls = delta.get("tool_calls")
    if not isinstance(tool_calls, list):
        return queries
    for tool_call in tool_calls:
        if not isinstance(tool_call, dict):
            continue
        function = tool_call.get("function")
        if not isinstance(function, dict):
            continue
        name = function.get("name")
        if not isinstance(name, str) or "web_search" not in name:
            continue
        arguments = function.get("arguments")
        if isinstance(arguments, str) and arguments.strip():
            try:
                parsed = json.loads(arguments)
            except json.JSONDecodeError:
                queries.append(arguments.strip())
                continue
            if isinstance(parsed, dict):
                query = parsed.get("query")
                if isinstance(query, str) and query.strip():
                    queries.append(query.strip())
                    continue
            queries.append(arguments.strip())
    return queries


def _workspace_file_list() -> list[str]:
    files: list[str] = []
    for path in sorted(WORKSPACE.rglob("*")):
        if path.suffix not in {".h", ".hpp", ".c", ".cc", ".cpp"}:
            continue
        files.append(str(path.relative_to(WORKSPACE)))
    return files


def _build_user_prompt(mode: str) -> str:
    findings = json.loads(FINDINGS_PATH.read_text())
    payload = {
        "mode": mode,
        "task": (
            "Analyze the simulated static-check findings against the workspace. "
            "Use OpenClaw filesystem tools to inspect files under workspaceRoot on demand. "
            "Identify root cause, especially whether the issue is upstream, and explain the cross-file fix. "
            "Coverage is mandatory: do not omit any affected file or known reference, and do not leave any finding partially analyzed. "
            "In fix mode, edit the workspace files directly and return what you actually changed."
        ),
        "findings": findings["findings"],
        "workspaceRoot": "/demo/workspace/project",
        "workspaceFilesHint": _workspace_file_list(),
    }
    if mode == "log":
        payload["responseContract"] = {
            "style": "json",
            "requirements": [
                "Return a top-level object",
                "Include findings as an array",
                "Each finding must include id, location, rootCause, filesToChange, fixSummary",
                "Each finding must include inspectedLocations as an array of file/line pairs with a short reason",
                "Include a top-level reasoningSummary string",
                "Inspect the primary location and every provided relatedLocation before finalizing the answer",
                "If a trace is provided, inspect the trace locations needed to confirm the upstream root cause",
                "For naming findings, filesToChange must include the definition file and every workspace file that references the symbol",
                "If you discover additional affected references beyond relatedLocations, include them in filesToChange and inspectedLocations",
                "Do not omit a known affected file from filesToChange",
                "fixSummary must describe the required fix only, not optional hardening advice",
                "Do not include markdown fences",
            ],
        }
    else:
        payload["responseContract"] = {
            "style": "json",
            "requirements": [
                "Return a top-level object",
                "Apply the fixes directly to files under workspaceRoot using filesystem edit tools",
                "Do not return only a proposed plan",
                "Include summary",
                "Include appliedEdits as an array",
                "Each appliedEdits item must have file, change, and status",
                "Include inspectedLocations as an array of file/line pairs with a short reason",
                "Include reasoningSummary as a concise explanation, not hidden chain-of-thought",
                "Inspect the primary location and every provided relatedLocation before finalizing the plan",
                "If a trace is provided, inspect the trace locations needed to confirm the upstream root cause",
                "The applied fixes must cover every affected file you confirmed from the workspace",
                "Do not leave a known finding partially fixed",
                "After editing, re-read the changed regions and include a validationSummary",
                "If any finding could not be fixed, include it under unresolvedFindings with a blocker",
                "Do not include markdown fences",
            ],
        }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _parse_json_text(text: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _write_run_log(
    *,
    mode: str,
    base_url: str,
    agent_id: str,
    model: str,
    session_key: str,
    session_url: str,
    success: bool,
    failure: str | None = None,
) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    path = LOG_PATH
    lines = [
        "-----",
        f"timestamp: {now.isoformat()}",
        f"mode: {mode}",
        f"base_url: {base_url}",
        f"agent_id: {agent_id}",
        f"model: {model}",
        f"api_call_status: {'success' if success else 'failure'}",
        f"session_key: {session_key}",
        f"session_url: {session_url}",
    ]
    if failure:
        lines.append(f"failure: {failure}")
        lines.append("")
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return path


def _build_session_key(agent_id: str) -> str:
    return f"agent:{agent_id}:openai:{uuid4()}"


def _build_session_url(base_url: str, session_key: str) -> str:
    return f"{base_url.rstrip('/')}/chat?session={parse.quote(session_key, safe='')}"


def _print_log_summary(payload: dict[str, Any] | None, fallback_text: str) -> None:
    if not isinstance(payload, dict):
        print(fallback_text)
        return
    findings = payload.get("findings")
    if not isinstance(findings, list) or not findings:
        print(fallback_text)
        return
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        location = finding.get("location")
        location_text = ""
        if isinstance(location, dict):
            file_path = location.get("file")
            line = location.get("line")
            if isinstance(file_path, str) and isinstance(line, int):
                location_text = f"{file_path}:{line}"
        finding_id = finding.get("id")
        header_parts = [part for part in (location_text, finding_id) if isinstance(part, str) and part]
        if header_parts:
            print(" ".join(header_parts))
        root_cause = finding.get("rootCause")
        if isinstance(root_cause, str) and root_cause.strip():
            print(f"Root cause: {root_cause.strip()}")
        files_to_change = finding.get("filesToChange")
        if isinstance(files_to_change, list) and files_to_change:
            files = [item for item in files_to_change if isinstance(item, str) and item.strip()]
            if files:
                print(f"Files to change: {', '.join(files)}")
        inspected = finding.get("inspectedLocations")
        if isinstance(inspected, list) and inspected:
            viewed: list[str] = []
            for item in inspected:
                if not isinstance(item, dict):
                    continue
                file_path = item.get("file")
                line = item.get("line")
                if isinstance(file_path, str) and isinstance(line, int):
                    viewed.append(f"{file_path}:{line}")
            if viewed:
                print(f"Inspected: {', '.join(viewed)}")
        fix_summary = finding.get("fixSummary")
        if isinstance(fix_summary, str) and fix_summary.strip():
            print(f"Fix: {fix_summary.strip()}")
        print()


def _create_request_body(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    stream: bool,
) -> dict[str, Any]:
    return {
        "model": model,
        "temperature": 0,
        "stream": stream,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }


def _request_openclaw(
    *,
    base_url: str,
    token: str,
    agent_id: str,
    session_key: str,
    timeout_seconds: int,
    body: dict[str, Any],
):
    req = request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-openclaw-agent-id": agent_id,
            "x-openclaw-session-key": session_key,
        },
        method="POST",
    )
    try:
        return request.urlopen(req, timeout=timeout_seconds)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        raise OpenClawCallError(f"OpenClaw HTTP {exc.code}: {detail or exc.reason}") from exc
    except error.URLError as exc:
        raise OpenClawCallError(f"Cannot reach OpenClaw at {base_url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise OpenClawCallError(
            f"OpenClaw request timed out after {timeout_seconds}s while connecting to {base_url}"
        ) from exc
    except socket.timeout as exc:
        raise OpenClawCallError(
            f"OpenClaw request timed out after {timeout_seconds}s while connecting to {base_url}"
        ) from exc


def _run_openclaw_prompt_nonstream(
    *,
    base_url: str,
    token: str,
    agent_id: str,
    session_key: str,
    timeout_seconds: int,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    body = _create_request_body(
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        stream=False,
    )
    with _request_openclaw(
        base_url=base_url,
        token=token,
        agent_id=agent_id,
        session_key=session_key,
        timeout_seconds=timeout_seconds,
        body=body,
    ) as response:
        raw = response.read().decode("utf-8", errors="replace").strip()
    payload = json.loads(raw)
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise OpenClawCallError("OpenClaw non-stream response is missing choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise OpenClawCallError("OpenClaw non-stream response is missing message")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise OpenClawCallError("OpenClaw non-stream response did not produce assistant text")
    return content.strip()


def _run_openclaw_prompt_stream(
    *,
    base_url: str,
    token: str,
    agent_id: str,
    session_key: str,
    timeout_seconds: int,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    body = _create_request_body(
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        stream=True,
    )
    text_parts: list[str] = []
    seen_queries: set[str] = set()

    try:
        with _request_openclaw(
            base_url=base_url,
            token=token,
            agent_id=agent_id,
            session_key=session_key,
            timeout_seconds=timeout_seconds,
            body=body,
        ) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = event.get("choices")
                if not isinstance(choices, list):
                    continue
                for choice in choices:
                    if not isinstance(choice, dict):
                        continue
                    delta = choice.get("delta")
                    if not isinstance(delta, dict):
                        continue
                    for query in _extract_web_search_queries(delta):
                        if query not in seen_queries:
                            seen_queries.add(query)
                            print(f"web_search: {query}")
                    content = delta.get("content")
                    if isinstance(content, str) and content:
                        text_parts.append(content)
    except TimeoutError:
        return _run_openclaw_prompt_nonstream(
            base_url=base_url,
            token=token,
            agent_id=agent_id,
            session_key=session_key,
            timeout_seconds=timeout_seconds,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
    except socket.timeout:
        return _run_openclaw_prompt_nonstream(
            base_url=base_url,
            token=token,
            agent_id=agent_id,
            session_key=session_key,
            timeout_seconds=timeout_seconds,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    text = "".join(text_parts).strip()
    if text:
        return text
    return _run_openclaw_prompt_nonstream(
        base_url=base_url,
        token=token,
        agent_id=agent_id,
        session_key=session_key,
        timeout_seconds=timeout_seconds,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


def _call_openclaw(*, mode: str) -> str:
    base_url = _require_env("OPENCLAW_BASE_URL", "http://127.0.0.1:18799").rstrip("/")
    token = _require_env("OPENCLAW_GATEWAY_TOKEN")
    agent_id = _require_env("OPENCLAW_AGENT_ID", "main")
    model = _require_env("OPENCLAW_MODEL", "openclaw")
    timeout_seconds = int(_require_env("OPENCLAW_TIMEOUT_SECONDS", "90"))
    session_key = _build_session_key(agent_id)
    session_url = _build_session_url(base_url, session_key)
    log_path = LOG_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{mode}.log"

    system_prompt = AGENT_PATH.read_text().strip()
    user_prompt = _build_user_prompt(mode)
    try:
        response_text = _run_openclaw_prompt_stream(
            base_url=base_url,
            token=token,
            agent_id=agent_id,
            session_key=session_key,
            timeout_seconds=timeout_seconds,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
    except OpenClawCallError as exc:
        log_path = _write_run_log(
            mode=mode,
            base_url=base_url,
            agent_id=agent_id,
            model=model,
            session_key=session_key,
            session_url=session_url,
            success=False,
            failure=str(exc),
        )
        print(f"session url: {session_url}")
        print(f"log written: {log_path}")
        raise SystemExit(str(exc)) from exc
    response_payload = _parse_json_text(response_text)
    log_path = _write_run_log(
        mode=mode,
        base_url=base_url,
        agent_id=agent_id,
        model=model,
        session_key=session_key,
        session_url=session_url,
        success=True,
    )
    if mode == "log":
        _print_log_summary(response_payload, response_text)
        print(f"session url: {session_url}")
        print(f"log written: {log_path}")
        return ""
    print(f"session url: {session_url}")
    print(f"log written: {log_path}")
    return response_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["log", "fix"], required=True)
    parser.add_argument(
        "--apply-demo-fixes",
        action="store_true",
        help="After a real OpenClaw fix analysis, apply the local deterministic demo fixes.",
    )
    args = parser.parse_args()

    _load_dotenv(ROOT / ".env")

    if not WORKSPACE.exists():
        raise SystemExit("workspace/project missing; run ./scripts/reset_demo.py first")

    text = _call_openclaw(mode=args.mode)
    if text:
        print(text)

    if args.mode == "fix" and args.apply_demo_fixes:
        print()
        print("---- local demo patch apply ----")
        apply_fix()


if __name__ == "__main__":
    main()
