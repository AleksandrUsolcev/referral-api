#!/bin/sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn referral.wsgi:application --bind 0:8000
exec "$@"
