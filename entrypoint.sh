#!/bin/sh
set -e

echo "==> Applying migrations..."
python manage.py migrate --noinput

echo "==> Ensuring superuser exists..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'StrongPass123!')"

echo "==> Starting gunicorn..."
exec gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers 3