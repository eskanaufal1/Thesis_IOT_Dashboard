# IoT Dashboard Backend - UV Setup

This project uses [uv](https://github.com/astral-sh/uv) for Python package and environment management.

## Setup

### 1. Install uv (if not already installed)

```powershell
winget install --id=astral-sh.uv -e
```

### 2. Create and activate virtual environment

```powershell
# Create virtual environment
uv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
# Install dependencies using uv pip
uv pip install -r requirements.txt --python venv
```

### 4. Environment configuration

```powershell
# Copy environment template
copy .env.template .env

# Edit .env with your configuration
notepad .env
```

## Development Commands

### Running the server

```powershell
# Activate virtual environment first
venv\Scripts\activate

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Package management

```powershell
# Add a new dependency
uv pip install package-name --python venv

# Remove a dependency
uv pip uninstall package-name --python venv

# Update requirements.txt after adding/removing packages
uv pip freeze --python venv > requirements.txt
```

### Development tools

```powershell
# Install development dependencies
uv pip install pytest pytest-asyncio httpx black isort flake8 --python venv

# Format code
uv run black .
uv run isort .

# Run linting
uv run flake8 .

# Run tests
uv run pytest
```

## Project Structure

```
server/
├── .env                 # Environment configuration (create from .env.template)
├── .env.template        # Environment template
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── main.py             # FastAPI application entry point
├── models/             # Database models and schemas
├── services/           # Business logic services (MQTT, Socket.IO)
├── config/             # Configuration modules
├── venv/               # Virtual environment (created by uv)
└── data/               # SQLite database files
```

## Environment Variables

See `.env.template` for all available configuration options.

Key variables:

- `DATABASE_PATH`: SQLite database file path
- `MQTT_BROKER_HOST`: MQTT broker hostname
- `MQTT_BROKER_PORT`: MQTT broker port
- `SECRET_KEY`: JWT secret key (change in production)
- `SOCKETIO_CORS_ORIGINS`: Allowed CORS origins for Socket.IO
