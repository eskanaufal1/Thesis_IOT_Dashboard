# IoT Dashboard Backend

A FastAPI-based backend for IoT device management with real-time data visualization.

## Features

- Real-time MQTT communication with IoT devices
- WebSocket integration using Socket.IO
- SQLite database for data persistence
- RESTful API endpoints
- Device management and telemetry data collection

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Install uv** (if not already installed):

   ```powershell
   winget install --id=astral-sh.uv -e
   ```

2. **Run setup script** (Windows):

   ```powershell
   setup.bat
   ```

   Or manually:

   ```powershell
   # Create virtual environment
   uv venv

   # Install dependencies
   uv pip install -r requirements.txt --python venv

   # Setup environment variables
   copy .env.template .env
   # Edit .env with your configuration
   ```

3. **Start development server**:

   ```powershell
   run_dev.bat
   ```

   Or manually:

   ```powershell
   venv\Scripts\activate
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Development

### Package Management with uv

```powershell
# Add new dependency
uv pip install package-name --python venv

# Remove dependency
uv pip uninstall package-name --python venv

# Update requirements.txt
uv pip freeze --python venv > requirements.txt

# Install development tools
uv pip install pytest black isort flake8 --python venv
```

### Code Quality

```powershell
# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8 .

# Run tests
uv run pytest
```

## Environment Variables

See `.env.template` for all configuration options. Key variables:

- `DATABASE_PATH`: Path to SQLite database
- `MQTT_BROKER_HOST`: MQTT broker hostname
- `MQTT_BROKER_PORT`: MQTT broker port
- `SECRET_KEY`: JWT secret key (change in production!)
- `SOCKETIO_CORS_ORIGINS`: Allowed CORS origins for Socket.IO

## Project Structure

```
server/
├── .env                 # Environment configuration
├── .env.template        # Environment template
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── main.py             # FastAPI application entry point
├── models/             # Database models and schemas
├── services/           # Business logic services
├── config/             # Configuration modules
├── venv/               # Virtual environment (uv managed)
└── data/               # Database files
```

## API Documentation

Once running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
