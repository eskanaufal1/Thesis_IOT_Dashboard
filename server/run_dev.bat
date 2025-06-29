@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting FastAPI development server...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
