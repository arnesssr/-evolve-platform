#!/usr/bin/env bash
set -euo pipefail

echo "[render-start] Starting Evolve Platform..."
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings}

# Show essential env (non-secret)
echo "[render-start] DEBUG=${DEBUG:-}"
echo "[render-start] RENDER_EXTERNAL_HOSTNAME=${RENDER_EXTERNAL_HOSTNAME:-}"
echo "[render-start] PORT=${PORT:-8000}"

# Determine DB engine and host using Django settings
DB_ENGINE=$(python - <<'PY'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE','config.settings'))
import django
from django.conf import settings
try:
    django.setup()
    cfg = settings.DATABASES['default']
    print(cfg.get('ENGINE',''))
except Exception as e:
    print('ERROR:', e)
PY
)

DB_HOST=$(python - <<'PY'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE','config.settings'))
import django
from django.conf import settings
try:
    django.setup()
    cfg = settings.DATABASES['default']
    print(cfg.get('HOST',''))
except Exception as e:
    print('ERROR:', e)
PY
)

echo "[render-start] Database engine: ${DB_ENGINE} host: ${DB_HOST}"

# Choose worker count safely: use 1 worker for SQLite to avoid lock errors
DEFAULT_WORKERS=3
if [[ "${DB_ENGINE}" == *"sqlite3"* ]]; then
  echo "[render-start] SQLite detected. Limiting Gunicorn workers to 1 to avoid database locking."
  DEFAULT_WORKERS=1
fi
WORKERS=${GUNICORN_WORKERS:-$DEFAULT_WORKERS}
THREADS=${GUNICORN_THREADS:-2}
TIMEOUT=${GUNICORN_TIMEOUT:-120}

# Run migrations (idempotent)
echo "[render-start] Running database migrations..."
python manage.py migrate --noinput

# Collect static files (optional; set COLLECTSTATIC=0 to skip)
COLLECT=${COLLECTSTATIC:-1}
if [ "$COLLECT" != "0" ] && [ "$COLLECT" != "false" ] && [ "$COLLECT" != "False" ] && [ "$COLLECT" != "FALSE" ]; then
  echo "[render-start] Collecting static files..."
  python manage.py collectstatic --noinput --verbosity=1
fi

echo "[render-start] Starting Gunicorn (workers=${WORKERS}, threads=${THREADS}, timeout=${TIMEOUT})..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${WORKERS} \
  --threads ${THREADS} \
  --timeout ${TIMEOUT}

