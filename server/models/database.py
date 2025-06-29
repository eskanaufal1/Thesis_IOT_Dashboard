from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    status = Column(String(20), default="offline")  # online, offline, maintenance
    device_type = Column(String(50), default="IoT Device")
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    telemetry_data = relationship("TelemetryData", back_populates="device")
    relay_states = relationship("RelayState", back_populates="device")


class TelemetryData(Base):
    __tablename__ = "telemetry_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Sensor readings
    voltage = Column(Float)
    current = Column(Float)
    power = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    
    # Additional data as JSON string
    additional_data = Column(Text)
    
    # Relationship
    device = relationship("Device", back_populates="telemetry_data")


class RelayState(Base):
    __tablename__ = "relay_states"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    relay_number = Column(Integer, nullable=False)  # 1, 2, 3, 4
    state = Column(Boolean, default=False)  # True = ON, False = OFF
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    updated_by = Column(String(50), default="system")  # system, user, mqtt
    
    # Relationship
    device = relationship("Device", back_populates="relay_states")


class DeviceCommand(Base):
    __tablename__ = "device_commands"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), nullable=False)
    command_type = Column(String(50), nullable=False)  # relay_control, status_request, etc.
    command_data = Column(Text)  # JSON string with command parameters
    status = Column(String(20), default="pending")  # pending, sent, acknowledged, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    response_data = Column(Text)


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    module = Column(String(50))
    device_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    additional_data = Column(Text)
