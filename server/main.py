"""
FastAPI main application for IoT Dashboard Backend.
"""
import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import services
from services.mqtt_service import MQTTService
from services.socketio_service import SocketIOService

# Import database
from config.database import engine, get_db
from models.database import Base
from models.user import User  # Import user model

# Import API routes
from api.auth import router as auth_router

# Load environment variables
load_dotenv()

# Global service instances
mqtt_service = None
socketio_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown events."""
    global mqtt_service, socketio_service
    
    # Startup
    print("🚀 Starting IoT Dashboard Backend...")
    
    # Create database tables
    print("📊 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️  Database setup warning: {e}")
    
    # Initialize services
    print("🔌 Initializing services...")
    try:
        mqtt_service = MQTTService()
        socketio_service = SocketIOService()
        print("✅ Services initialized")
    except Exception as e:
        print(f"⚠️  Service initialization warning: {e}")
    
    # Start services (with error handling)
    if mqtt_service:
        try:
            await mqtt_service.start()
            print("✅ MQTT service started")
        except Exception as e:
            print(f"⚠️  MQTT service start warning: {e}")
    
    if socketio_service:
        try:
            await socketio_service.start()
            print("✅ Socket.IO service started")
        except Exception as e:
            print(f"⚠️  Socket.IO service start warning: {e}")
    
    print("🎉 Server startup completed!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down services...")
    
    if mqtt_service:
        try:
            await mqtt_service.stop()
            print("✅ MQTT service stopped")
        except Exception as e:
            print(f"⚠️  MQTT service stop warning: {e}")
        
    if socketio_service:
        try:
            await socketio_service.stop()
            print("✅ Socket.IO service stopped")
        except Exception as e:
            print(f"⚠️  Socket.IO service stop warning: {e}")
    
    print("👋 IoT Dashboard Backend stopped")


# Create FastAPI app
app = FastAPI(
    title="IoT Dashboard Backend",
    description="Backend API for IoT device management with real-time data visualization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("SOCKETIO_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: Socket.IO will be handled by the socketio service directly

# Include API routers
app.include_router(auth_router)


# Basic routes
@app.get("/")
async def root():
    """Root endpoint - API status."""
    return {
        "message": "IoT Dashboard Backend API",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "mqtt": mqtt_service.is_connected() if mqtt_service else False,
            "socketio": socketio_service.is_running() if socketio_service else False,
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "mqtt": "connected" if mqtt_service and mqtt_service.is_connected() else "disconnected",
            "socketio": "running" if socketio_service and socketio_service.is_running() else "stopped",
        }
    }


# API Routes (basic examples - expand these)
@app.get("/api/devices")
async def get_devices(db = Depends(get_db)):
    """Get all devices."""
    # TODO: Implement device retrieval from database
    return {"devices": [], "message": "Device endpoints not fully implemented yet"}


@app.get("/api/telemetry/{device_id}")
async def get_device_telemetry(device_id: str, db = Depends(get_db)):
    """Get telemetry data for a specific device."""
    # TODO: Implement telemetry data retrieval
    return {"device_id": device_id, "telemetry": [], "message": "Telemetry endpoints not fully implemented yet"}


@app.post("/api/devices/{device_id}/relay/{relay_id}")
async def control_relay(device_id: str, relay_id: int, state: bool):
    """Control device relay."""
    if mqtt_service:
        success = await mqtt_service.send_relay_command(device_id, relay_id, state)
        if success:
            return {"message": f"Relay {relay_id} {'turned on' if state else 'turned off'} for device {device_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send relay command")
    else:
        raise HTTPException(status_code=503, detail="MQTT service not available")



def main():
    """Main entry point for the IoT Dashboard Backend."""
    import uvicorn
    
    # Configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
