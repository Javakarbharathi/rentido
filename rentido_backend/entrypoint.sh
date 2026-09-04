#!/bin/sh
set -e

# Default environment fallbacks
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

echo "[Rentido Entrypoint] Checking database connection at ${DB_HOST}:${DB_PORT}..."
while ! nc -z "${DB_HOST}" "${DB_PORT}" 2>/dev/null; do
  echo "[Rentido Entrypoint] Database not ready yet, sleeping 1s..."
  sleep 1
done
echo "[Rentido Entrypoint] MySQL database is reachable!"

# If this is the main web container, run migrations and collectstatic
if [ "$1" = "gunicorn" ] || [ "$1" = "python" ]; then
  echo "[Rentido Entrypoint] Applying database migrations..."
  python manage.py migrate --noinput

  echo "[Rentido Entrypoint] Collecting static assets..."
  python manage.py collectstatic --noinput --clear 2>/dev/null || true
fi

echo "[Rentido Entrypoint] Executing: $@"
exec "$@"
