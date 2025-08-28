# PowerShell script to run the Django development server
# This script clears cache, activates the virtual environment and starts the server

# Clear Python cache
Write-Host "Clearing Python cache..." -ForegroundColor Cyan
$cacheCount = 0

# Remove all __pycache__ directories
Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    $cacheCount++
}

# Remove all .pyc files
Get-ChildItem -Path . -Filter "*.pyc" -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    $cacheCount++
}

# Clear Django static files cache if it exists
if (Test-Path "staticfiles\CACHE") {
    Remove-Item "staticfiles\CACHE" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Cleared Django static files cache" -ForegroundColor Green
}

Write-Host "Cleared $cacheCount cache items" -ForegroundColor Green

Write-Host "`nActivating virtual environment..." -ForegroundColor Green
& .\evolve_env\Scripts\Activate.ps1

Write-Host "`nStarting Django development server..." -ForegroundColor Green
Write-Host "The server will be available at http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

python manage.py runserver
