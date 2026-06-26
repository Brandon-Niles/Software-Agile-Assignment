#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Installing dev tools (bandit, pytest)..."
python -m pip install --upgrade pip
pip install bandit pytest || true

echo "Running Django tests..."
cd task-management-app
python manage.py migrate --noinput
pytest -q || python manage.py test

echo "Starting dev server in background..."
python manage.py runserver 0.0.0.0:8000 &>/tmp/server.log &
SERVER_PID=$!
echo "Waiting for server..."
for i in {1..30}; do curl -sSf http://127.0.0.1:8000 && break || sleep 1; done

echo "Running Bandit..."
bandit -r . -f json -o ../bandit_report.json || true

echo "You can run OWASP ZAP against http://127.0.0.1:8000 (use zaproxy docker image or installed ZAP)."

echo "Stopping server..."
kill $SERVER_PID || true
