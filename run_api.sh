#!/usr/bin/env bash
# Run FastAPI backend (after: pip install -r requirements.txt && pip install -e .)
set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
uvicorn system_design_mcp.api.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
