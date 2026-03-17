# AI Static Check Autofix Agent

A runnable demo repo for an OpenClaw-based static-check diagnosis and repair workflow.

License:

- non-commercial use only
- commercial use requires prior written permission

This repo includes:

- simulated static-check findings
- a mutable C++ demo workspace
- a real OpenClaw runner wired through Docker
- a deterministic local mock runner

## What Changed

You do not need to fork OpenClaw for this demo anymore.

This repo pulls the official OpenClaw image defined in `.env` / `.env.example`, writes the runtime config inside the container, and exposes the gateway locally through Docker Compose.

## Prerequisites

- Docker
- Docker Compose v2
- Python 3
- a Gemini API key
- a C++ compiler only if you want to build the demo app locally

Windows note:

- normal Git clone is fine, but shell scripts in this repo should stay LF, not CRLF
- prefer `docker compose ...` directly instead of `./scripts/*.sh`
- run Python scripts with `python .\scripts\...`

## Quick Start

Clone the repo:

```bash
git clone <this-demo-repo-url> ai-static-check-fix-demo
cd ai-static-check-fix-demo
```

Create local config:

```bash
cp .env.example .env
```

Generate a gateway token:

```bash
openssl rand -hex 32
```

Edit `.env` and fill in your local secrets:

```env
OPENCLAW_IMAGE=ghcr.io/openclaw/openclaw:main-slim@sha256:3d8a43e4e96fdfec4d96f774f3029eed821651370a330fce3fe4e27625440b73
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

Bring the gateway up:

```bash
docker compose up -d
```

Notes:

- `.env` stays local and must never be committed
- the default OpenClaw image is already pinned to a digest for reproducibility
- if you change `.env`, restart Docker Compose so the generated OpenClaw config is rebuilt
- `openclaw-cli` is kept as a compose profile-only helper, so normal `docker compose up -d` only starts the gateway

## Dashboard And Pairing

Print the dashboard URL:

```bash
docker compose --profile cli run --rm --no-deps openclaw-cli dashboard --no-open
```

Open that URL in your browser.

If the browser asks you to pair the device, list pending requests:

```bash
docker compose --profile cli run --rm --no-deps openclaw-cli devices list
```

Approve the request:

```bash
docker compose --profile cli run --rm --no-deps openclaw-cli devices approve <requestId>
```

Then refresh the dashboard page.

If the dashboard is not ready yet:

```bash
docker compose ps
docker compose logs --tail=120 openclaw-gateway
```

## Reset The Demo Workspace

The live demo workspace is mutable:

- findings: `workspace/static-signals/current-findings.json`
- source tree: `workspace/project`

Those two need to stay in sync. Before a fresh fix run, reset one of the scenarios:

```bash
python ./scripts/reset_demo.py --scenario small
python ./scripts/reset_demo.py --scenario large
```

If you only swap the findings file but keep a previously fixed workspace, the agent may correctly decide there is nothing left to edit.

## Run The Agent

Diagnosis only:

```bash
python ./scripts/openclaw_demo_agent.py --mode log
```

Apply fixes:

```bash
python ./scripts/openclaw_demo_agent.py --mode fix
```

Fix mode is expected to:

- inspect every file implicated by the findings
- post one short dashboard comment before the first edit
- edit files under `workspace/project`
- re-read changed regions for validation
- post one short dashboard comment summarizing the edits
- finish with a short completion note

If fix mode exits with:

```text
OpenClaw returned from fix mode without modifying workspace/project.
```

then either the workspace was already fixed, or the run stopped at diagnosis without applying edits. Reset the workspace first if you want a clean end-to-end fix run.

Run metadata is appended to:

- `logs/openclaw-runs/openclaw-demo.log`

## Build The Demo App

Compile and run the C++ project under `workspace/project`:

```bash
./scripts/build_demo.sh
```

The build uses:

```bash
g++ -std=c++17 -Wall -Wextra -Iinclude src/*.cpp -o demo_app
```

## Mock Mode

For a deterministic local run without real OpenClaw:

```bash
python ./scripts/reset_demo.py --scenario small
python ./scripts/mock_openclaw_agent.py --mode log
python ./scripts/mock_openclaw_agent.py --mode fix
```

## Runtime Layout

Static-signal fixtures:

- `fixtures/static-signals/small-findings.json`
- `fixtures/static-signals/large-findings.json`
- `workspace/static-signals/current-findings.json`

Workspace:

- `workspace/project`

Agent prompt:

- `agent/STATIC_CHECK_AGENT.md`

Runners:

- `scripts/openclaw_demo_agent.py`
- `scripts/mock_openclaw_agent.py`

Helpers:

- `scripts/reset_demo.py`
- `scripts/use_signal_fixture.py`
- `scripts/build_demo.sh`
- `scripts/docker_up.sh`
- `scripts/docker_down.sh`

## Stop OpenClaw

```bash
docker compose down
```

Optional helper:

```bash
./scripts/docker_down.sh
```

## Push Safety

Before pushing:

- keep `.env` local only
- keep provider API keys local only
- keep gateway tokens local only
- keep logs and temporary files untracked
- keep `.env.example` aligned with the current image and env vars

## Demo Video

https://www.youtube.com/watch?v=GYFP4GEz5DE
