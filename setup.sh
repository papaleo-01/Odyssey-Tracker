#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# setup.sh  —  Setup / Update / Uninstall for Odyssey Tracker
#
# Usage:
#   ./setup.sh              First-time setup
#   ./setup.sh --update     Update dependencies (keeps .env and data)
#   ./setup.sh --uninstall  Remove the app (interactive prompts for data)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# Always run from the project root, regardless of where the script was called from
cd "$(dirname "$0")"

MODE="${1:-install}"

# ── Uninstall ─────────────────────────────────────────────────────────────────
if [ "$MODE" = "--uninstall" ]; then
  echo "=============================="
  echo "  Odyssey Tracker — Uninstall"
  echo "=============================="
  echo
  echo "This will remove the virtual environment."
  echo

  # Confirm venv removal
  read -r -p "Remove venv/ (Python environment)? [y/N] " CONFIRM_VENV
  if [[ "$CONFIRM_VENV" =~ ^[Yy]$ ]]; then
    rm -rf venv
    echo "  ✓ venv/ removed."
  else
    echo "  – venv/ kept."
  fi

  # Confirm data removal
  read -r -p "Remove data/ (your SQLite database and temp files)? [y/N] " CONFIRM_DATA
  if [[ "$CONFIRM_DATA" =~ ^[Yy]$ ]]; then
    rm -rf data
    echo "  ✓ data/ removed."
  else
    echo "  – data/ kept."
  fi

  # Confirm .env removal
  read -r -p "Remove .env (your config + secret key)? [y/N] " CONFIRM_ENV
  if [[ "$CONFIRM_ENV" =~ ^[Yy]$ ]]; then
    rm -f .env
    echo "  ✓ .env removed."
  else
    echo "  – .env kept."
  fi

  echo
  echo "  Done. Application files (Python code, templates) are still in place."
  echo "  To fully remove, delete this directory: $(pwd)"
  echo
  exit 0
fi

# ── Update ─────────────────────────────────────────────────────────────────────
if [ "$MODE" = "--update" ]; then
  echo "=============================="
  echo "  Odyssey Tracker — Update"
  echo "=============================="
  echo

  if [ ! -d "venv" ]; then
    echo "ERROR: No venv/ found. Run ./setup.sh first."
    exit 1
  fi

  echo "[1/2] Upgrading pip..."
  ./venv/bin/pip install --quiet --upgrade pip

  echo "[2/2] Installing/updating dependencies..."
  ./venv/bin/pip install --quiet --upgrade -r requirements.txt
  echo "      Dependencies up to date."

  echo
  echo "=============================="
  echo "  Update complete!"
  echo "  Restart the app: sudo systemctl restart odyssey-tracker"
  echo "  (or press Ctrl+C and re-run ./run.sh)"
  echo "=============================="
  exit 0
fi

# ── Install (default) ──────────────────────────────────────────────────────────
echo "=============================="
echo "  Odyssey Tracker — Setup"
echo "=============================="
echo

# 1. Python check
if ! command -v python3 &>/dev/null; then
  echo "ERROR: python3 not found. Install it with: sudo apt install python3 python3-venv python3-pip"
  exit 1
fi
PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[1/4] Python $PYTHON_VER found."

# 2. Create virtual environment
if [ ! -d "venv" ]; then
  echo "[2/4] Creating virtual environment..."
  python3 -m venv venv
else
  echo "[2/4] Virtual environment already exists, skipping."
fi

# 3. Install dependencies
echo "[3/4] Installing dependencies..."
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet -r requirements.txt
echo "      Dependencies installed."

# 4. Create .env if missing
if [ ! -f ".env" ]; then
  echo "[4/4] Creating .env from template..."
  cp .env.example .env

  # Generate a random secret key
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  # Use sed to replace the placeholder (works on both Linux and macOS)
  sed -i.bak "s/change_this_to_a_random_secret_key/$SECRET/" .env && rm -f .env.bak

  echo
  echo "  ┌─────────────────────────────────────────────────────┐"
  echo "  │  ACTION REQUIRED: Set your password in .env         │"
  echo "  │  Open .env and change APP_PASSWORD=changeme         │"
  echo "  └─────────────────────────────────────────────────────┘"
else
  echo "[4/4] .env already exists, skipping."
fi

# 5. Create data directories
mkdir -p data/temp

echo
echo "=============================="
echo "  Setup complete!"
echo "  Next: edit .env then run ./run.sh"
echo "  To update later: ./setup.sh --update"
echo "  To uninstall:    ./setup.sh --uninstall"
echo "=============================="
