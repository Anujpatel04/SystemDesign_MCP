#!/usr/bin/env bash
# Run Streamlit UI from project root (after: pip install -r requirements.txt && pip install -e .)
set -e
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"
streamlit run system_design_mcp/frontend/app.py --server.port "${STREAMLIT_PORT:-8501}" --server.address 0.0.0.0
