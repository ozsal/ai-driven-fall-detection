# PowerShell script to start the backend server
# Run this script to start the FastAPI backend

Write-Host "Starting Fall Detection Backend Server..." -ForegroundColor Green
Write-Host ""

# Change to the api directory
Set-Location -Path "$PSScriptRoot\api"

# Check if virtual environment exists
if (Test-Path "..\venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "..\venv\Scripts\Activate.ps1"
} else {
    Write-Host "Warning: Virtual environment not found. Using system Python." -ForegroundColor Yellow
}

# Set environment variables
$env:API_HOST = "0.0.0.0"
$env:API_PORT = "8000"

Write-Host "Starting server on http://0.0.0.0:8000" -ForegroundColor Cyan
Write-Host "API will be accessible at:" -ForegroundColor Cyan
Write-Host "  - http://localhost:8000" -ForegroundColor White
Write-Host "  - http://10.162.131.191:8000" -ForegroundColor White
Write-Host ""

# Start the server
python main.py




