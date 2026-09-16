#!/usr/bin/env bash
set -euo pipefail
cd /srv
# Run migrations when DATABASE_URL is available. The application still uses
# create_all as a safe bootstrap for the local test harness.
if command -v alembic >/dev/null 2>&1; then
  alembic -c backend/alembic.ini upgrade head
fi
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8080}" --proxy-headers
