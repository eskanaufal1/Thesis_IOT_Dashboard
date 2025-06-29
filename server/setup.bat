@echo off
REM Setup script for new developers
echo Setting up IoT Dashboard Backend...

echo Checking if uv is installed...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv...
    winget install --id=astral-sh.uv -e
)

echo Creating virtual environment...
uv venv

echo Installing dependencies...
uv pip install -r requirements.txt --python venv

echo Creating .env file from template...
if not exist .env (
    copy .env.template .env
    echo Please edit .env file with your configuration
    notepad .env
)

echo Setup complete!
echo Run 'run_dev.bat' to start the development server
pause
