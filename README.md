# AI Static Check Fix Demo

A runnable demo repo for an OpenClaw-based static-check diagnosis and repair workflow.

The repo contains:

- a small scenario
- a large scenario
- simulated static-check findings
- a real OpenClaw runner
- a local mock runner

## Full Start

### 0. Prerequisites

You need these locally:

- Docker
- Docker Compose
- Python 3
- a Gemini API key

### 1. Clone the required OpenClaw repo locally

This demo must run against your OpenClaw version.

Do not use the official OpenClaw repo for this demo.

This repo builds Docker from a local OpenClaw checkout. It does not pull a published OpenClaw image.

```bash
git clone https://github.com/sakuralaa/openclaw.git openclaw
```

If you already have the repo:

```bash
cd openclaw
git pull
```

### 2. Clone this demo repo

```bash
git clone <this-demo-repo-url> ai-static-check-fix-demo
cd ai-static-check-fix-demo
```

### 3. Create local config

```bash
cp .env.example .env
```

Generate a gateway token locally:

```bash
openssl rand -hex 32
```

Edit `.env` and fill your local values:

```env
OPENCLAW_REPO_PATH=../openclaw
OPENCLAW_GATEWAY_PORT=18799
OPENCLAW_BASE_URL=http://127.0.0.1:18799
OPENCLAW_GATEWAY_TOKEN=replace-me
GEMINI_API_KEY=replace-me
OPENCLAW_PRIMARY_MODEL=google/gemini-3-flash-preview
OPENCLAW_AGENT_ID=main
OPENCLAW_MODEL=openclaw
OPENCLAW_TIMEOUT_SECONDS=180
OPENCLAW_STARTUP_TIMEOUT_SECONDS=30
```

Notes:

- do not commit `.env`
- use your own gateway token
- use your own provider key
- if `openclaw` is not a sibling checkout, set `OPENCLAW_REPO_PATH` to an absolute path
- `OPENCLAW_REPO_PATH` must point to `https://github.com/sakuralaa/openclaw.git`

### 4. Prepare the demo workspace

Large scenario:

```bash
python3 ./scripts/reset_demo.py --scenario large
```

Small scenario:

```bash
python3 ./scripts/reset_demo.py --scenario small
```

### 5. Start the dedicated OpenClaw gateway

```bash
./scripts/docker_up.sh
```

What this does:

- loads `.env`
- builds Docker from `OPENCLAW_REPO_PATH`
- mounts this repo at `/demo`
- uses `/demo/workspace/project` as the OpenClaw workspace
- waits for the gateway to accept connections before returning

`OPENCLAW_REPO_PATH` is expected to target your repo:

- `https://github.com/sakuralaa/openclaw.git`

### 6. Open the Web UI

Open:

```text
http://127.0.0.1:18799/#token=<OPENCLAW_GATEWAY_TOKEN>
```

If you changed `OPENCLAW_GATEWAY_PORT`, replace `18799`.

The `#token=...` fragment is required for the dashboard.

### 7. If the browser asks for pairing

List pending device requests:

```bash
docker exec -it ai-static-check-fix-demo-openclaw \
  sh -lc 'cd /app && OPENCLAW_GATEWAY_PORT=18789 node dist/index.js devices list'
```

Approve a request:

```bash
docker exec -it ai-static-check-fix-demo-openclaw \
  sh -lc 'cd /app && OPENCLAW_GATEWAY_PORT=18789 node dist/index.js devices approve <requestId>'
```

Then refresh the browser.

Why `18789` here:

- host port is `18799` by default
- container-internal gateway port is `18789`

### 8. Run the agent

Log mode:

```bash
./scripts/openclaw_demo_agent.py --mode log
```

Fix mode:

```bash
./scripts/openclaw_demo_agent.py --mode fix
```

The runner appends session information to:

- `logs/openclaw-runs/openclaw-demo.log`

### 9. Stop the gateway

```bash
./scripts/docker_down.sh
```

## What This Demo Exercises

The demo intentionally includes these static-check issue types:

- macro naming violations
- a cross-file resource leak in `FileReader`

The point is to show:

- the agent reads static-check findings from JSON
- the agent reads source files on demand from the mounted workspace
- the agent can explain root cause across files
- the agent can modify files in `--fix` mode

## Runtime Files

Static signals:

- `fixtures/static-signals/small-findings.json`
- `fixtures/static-signals/large-findings.json`
- `workspace/static-signals/current-findings.json`

Workspace:

- `workspace/project/`

Agent definition:

- `agent/STATIC_CHECK_AGENT.md`

Runners:

- `scripts/openclaw_demo_agent.py`
- `scripts/mock_openclaw_agent.py`

Helper commands:

- `scripts/reset_demo.py`
- `scripts/use_signal_fixture.py`
- `scripts/build_demo.sh`
- `scripts/docker_up.sh`
- `scripts/docker_down.sh`

## Scenario Commands

Small log:

```bash
python3 ./scripts/reset_demo.py --scenario small
./scripts/openclaw_demo_agent.py --mode log
```

Small fix:

```bash
python3 ./scripts/reset_demo.py --scenario small
./scripts/openclaw_demo_agent.py --mode fix
```

Large log:

```bash
python3 ./scripts/reset_demo.py --scenario large
./scripts/openclaw_demo_agent.py --mode log
```

Large fix:

```bash
python3 ./scripts/reset_demo.py --scenario large
./scripts/openclaw_demo_agent.py --mode fix
```

If you only want to switch the active findings file without resetting the workspace:

```bash
python3 ./scripts/use_signal_fixture.py --scenario small
python3 ./scripts/use_signal_fixture.py --scenario large
```

## Mock Mode

If you want a deterministic local run without real OpenClaw:

```bash
python3 ./scripts/reset_demo.py --scenario small
./scripts/mock_openclaw_agent.py --mode log
./scripts/mock_openclaw_agent.py --mode fix
```

## Upload Notes

Before pushing this repo:

- keep `.env` local only
- keep provider keys local only
- keep gateway tokens local only
- review `logs/openclaw-runs/openclaw-demo.log` before pushing, or leave it untracked
- make sure `OPENCLAW_REPO_PATH` is documented in `.env.example`, not committed in `.env`

## Token And Pairing Summary

Gateway token:

- required by `scripts/openclaw_demo_agent.py`
- required by the Web UI
- stored only in your local `.env`
- can be generated with `openssl rand -hex 32`

Pairing:

- the dedicated gateway may require browser/device pairing
- if so, use `devices list` and `devices approve` inside the container
- approval is separate from the shared gateway token

## Required OpenClaw Repo

Users of this demo should use:

- `https://github.com/sakuralaa/openclaw.git`

They should not use the official OpenClaw repository for this demo.
