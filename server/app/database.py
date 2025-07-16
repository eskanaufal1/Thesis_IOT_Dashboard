"""
Database configuration and models using SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Convert SQLite URL to async format
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()


class MQTTBroker(Base):
    """
    MQTT Broker configuration model for storing broker connection details.
    """
    __tablename__ = "mqtt_brokers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    broker_name = Column(String(100), nullable=False)
    broker_host = Column(String(200), nullable=False)
    broker_port = Column(Integer, default=1883)
    username = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    last_connected = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="mqtt_brokers")
    devices = relationship("Device", back_populates="mqtt_broker")


class Device(Base):
    """
    Device model for storing IoT device configurations.
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mqtt_broker_id = Column(Integer, ForeignKey("mqtt_brokers.id"), nullable=False)
    device_name = Column(String(100), nullable=False)
    device_id = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="devices")
    mqtt_broker = relationship("MQTTBroker", back_populates="devices")
    sensor_data = relationship("SensorData", back_populates="device")


class User(Base):
    """
    User model for authentication and user management.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sensor_data = relationship("SensorData", back_populates="user")
    mqtt_brokers = relationship("MQTTBroker", back_populates="user")
    devices = relationship("Device", back_populates="user")


class SensorData(Base):
    """
    Sensor data model for storing IoT device measurements.
    """
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(100), nullable=False)
    device_table_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    sensor_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text, nullable=True)  # JSON string for additional data

    # Relationships
    user = relationship("User", back_populates="sensor_data")
    device = relationship("Device", back_populates="sensor_data")


class MQTTMessage(Base):
    """
    MQTT message model for logging MQTT communications.
    """
    __tablename__ = "mqtt_messages"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(200), nullable=False)
    payload = Column(Text, nullable=False)
    qos = Column(Integer, default=0)
    retain = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_type = Column(String(20), default="received")  # "sent" or "received"


# Database dependency
async def get_db():
    """
    Database dependency for FastAPI routes.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize database
async def init_db():
    """
    Initialize the database by creating all tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create default admin user if not exists
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    await auth_service.create_default_admin()
