#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python -m venv .venv; fi
. .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
