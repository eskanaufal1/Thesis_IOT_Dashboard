# FastAPI Backend for IoT Dashboard

A simple and reusable FastAPI backend with authentication, database integration, and MQTT support.

## Features

- FastAPI web framework
- JWT Authentication
- SQLite database with SQLAlchemy ORM
- MQTT client integration
- Pydantic models for validation
- Modular and reusable components

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Run the development server:
```bash
uv run python -m fastapi dev main.py --port 8000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile
- `POST /api/auth/change-password` - Change password

### IoT Data
- `GET /api/mqtt/status` - Get MQTT connection status
- `POST /api/mqtt/publish` - Publish message to MQTT topic
- `GET /api/data/sensors` - Get sensor data
- `POST /api/data/sensors` - Create sensor data entry

## Environment Variables

Create a `.env` file in the server directory:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./app.db
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
```
