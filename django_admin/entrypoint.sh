#!/bin/sh
set -e

python manage.py create_content_schema
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py create_default_superuser
python manage.py seed_data

gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
