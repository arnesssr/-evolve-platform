# PowerShell script to run the Django development server
# This script activates the virtual environment and starts the server

Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\evolve_env\Scripts\Activate.ps1

Write-Host "`nStarting Django development server..." -ForegroundColor Green
Write-Host "The server will be available at http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

python manage.py runserver
