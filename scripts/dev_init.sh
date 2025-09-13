#!/usr/bin/env bash
set -e
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env || true
echo "✅ Dev env ready. Run: make ingest && make dev (API) and make ui (UI)"
