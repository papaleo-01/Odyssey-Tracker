#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run.sh  —  Start the Odyssey Tracker app
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# Always run from the project root, regardless of where the script was called from
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "ERROR: venv not found. Run ./setup.sh first."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "ERROR: .env not found. Run ./setup.sh first."
  exit 1
fi

# Load PORT and HOST from .env (defaults if missing)
PORT=$(grep -E '^PORT=' .env 2>/dev/null | cut -d= -f2 | tr -d ' ' || echo "8000")
HOST=$(grep -E '^HOST=' .env 2>/dev/null | cut -d= -f2 | tr -d ' ' || echo "0.0.0.0")

echo "Starting Odyssey Tracker on http://${HOST}:${PORT}"
echo "Press Ctrl+C to stop."
echo

./venv/bin/uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
