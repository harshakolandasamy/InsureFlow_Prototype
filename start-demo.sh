#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
( cd "$ROOT/backend"; python3 -m venv .venv; source .venv/bin/activate; pip install -r requirements.txt; uvicorn main:app --reload --port 8000 ) &
( cd "$ROOT/frontend"; npm install; npm run dev ) &
wait
