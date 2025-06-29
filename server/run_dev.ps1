# PowerShell script to run development server
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

Write-Host "Starting FastAPI development server..." -ForegroundColor Green
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
