#!/usr/bin/env bash
set -e

echo "Starting local development server..."

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Django dev server (autoreload)..."
exec python manage.py runserver 0.0.0.0:8000