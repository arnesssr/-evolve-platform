# Test script to simulate production environment locally
Write-Host "Testing Django app with production settings..." -ForegroundColor Green

# Set DEBUG to False
$env:DEBUG = "False"

# Run collectstatic
Write-Host "Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

# Run the server
Write-Host "Starting server with DEBUG=False..." -ForegroundColor Yellow
Write-Host "Visit http://localhost:8000/login/ to test CSS loading" -ForegroundColor Cyan
Write-Host "Visit http://localhost:8000/static-diagnostic/ to check configuration" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
python manage.py runserver
