#!/bin/sh

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 pick_pool.asgi:application
