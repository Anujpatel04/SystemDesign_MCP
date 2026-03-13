#!/usr/bin/env bash
# Run React frontend (dev server with API proxy to port 8000)
# Start the API first in another terminal: ./run_api.sh
set -e
cd "$(dirname "$0")/web"
npm run dev
