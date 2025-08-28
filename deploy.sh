#!/bin/bash
# Deployment script for Render.com
# This script handles migrations and starts the Django application

set -e  # Exit on any error

echo "Starting deployment..."

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (optional, only for first deployment)
# Uncomment the following lines if you want to create a default superuser
# echo "Creating superuser if it doesn't exist..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'changeme123')
#     print('Default admin user created')
# "

echo "Deployment completed successfully!"
