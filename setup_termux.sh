#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python git unzip
python -m pip install --upgrade pip
if [ ! -d .venv ]; then python -m venv .venv; fi
. .venv/bin/activate
pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; fi
echo "O‘rnatish tugadi. .env faylini to‘ldiring, so‘ng alembic upgrade head va testlarni bajaring."
