#!/bin/bash

echo "Starting Django application on Render..."

# Print environment info
echo "Environment variables:"
echo "DEBUG: $DEBUG"
echo "RENDER: $RENDER"
echo "RENDER_EXTERNAL_HOSTNAME: $RENDER_EXTERNAL_HOSTNAME"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
echo "Static directory contents before collection:"
ls -la static/ | head -10 || echo "No static directory found"

python manage.py collectstatic --noinput --verbosity=2

echo "Static files collected. Checking staticfiles directory:"
ls -la staticfiles/css/ | head -5 || echo "No staticfiles/css directory found"

# Create superuser if it doesn't exist (only in development)
if [ "$DEBUG" = "True" ]; then
    echo "Creating superuser for development..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print('Superuser created: admin/password')
else:
    print('Superuser already exists')
"
fi

# Start the application with gunicorn
echo "Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --worker-class sync --timeout 120 config.wsgi:application
