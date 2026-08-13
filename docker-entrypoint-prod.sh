#!/usr/bin/env bash
set -e

echo "Starting production deployment..."

# Navigate to Django project directory (змінити якщо manage.py в іншій папці)
cd socialnetwork  # <-- ЗМІНИТИ НА НАЗВУ ТВОЄЇ ПАПКИ З manage.py

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn server..."
exec gunicorn socialnetwork.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info