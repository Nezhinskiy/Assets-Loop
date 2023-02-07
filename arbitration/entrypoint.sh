#!/bin/bash -x

# Start Celery Gunicorn
gunicorn arbitration.wsgi:application --bind 0.0.0.0:8000

# Start Celery Workers
celery -A arbitration worker -l INFO

python manage.py collectstatic --noinput