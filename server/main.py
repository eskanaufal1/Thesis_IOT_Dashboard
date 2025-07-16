"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import init_db
from app.routers import auth, mqtt_simple as mqtt, data, mqtt_brokers
from app.services.enhanced_mqtt_service import enhanced_mqtt_service

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    """
    # Startup
    await init_db()
    
    # Initialize enhanced MQTT service
    await enhanced_mqtt_service.initialize()
    
    yield
    
    # Shutdown
    await enhanced_mqtt_service.shutdown()


# Create FastAPI app
app = FastAPI(
    title="IoT Dashboard API",
    description="A simple and reusable FastAPI backend for IoT Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(mqtt.router, prefix="/api/mqtt", tags=["MQTT"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(mqtt_brokers.router, prefix="/api/mqtt-brokers", tags=["MQTT Brokers"])


@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    """
    return JSONResponse({
        "message": "IoT Dashboard API",
        "version": "1.0.0",
        "status": "running"
    })


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    # Get MQTT service status
    mqtt_status = "disconnected"
    try:
        statuses = await enhanced_mqtt_service.get_all_brokers_status()
        connected_count = sum(1 for status in statuses if status["connected"])
        if connected_count > 0:
            mqtt_status = f"connected ({connected_count} brokers)"
    except Exception:
        pass
    
    return JSONResponse({
        "status": "healthy",
        "database": "connected",
        "mqtt": mqtt_status
    })
