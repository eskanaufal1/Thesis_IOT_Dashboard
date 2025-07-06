"""
Database service with modern patterns for better maintainability.
Provides high-level database operations with proper error handling and security.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from config.database import SessionLocal
from models.database import Device, TelemetryData, RelayState, SystemLog
from models.schemas import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    TelemetryDataCreate, TelemetryDataResponse,
    RelayStateCreate, RelayStateResponse,
    SystemLogCreate, SystemLogResponse,
    DeviceStatus, LogLevel
)
from services.security_service import SecurityService

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    High-level database service with clean abstractions.
    """
    
    @asynccontextmanager
    async def get_session(self):
        """Async context manager for database sessions"""
        session = SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    # Device operations
    async def create_device(self, device_data: DeviceCreate) -> Optional[DeviceResponse]:
        """Create a new device with input validation and sanitization"""
        try:
            async with self.get_session() as db:
                # Validate and sanitize device input
                device_dict = device_data.dict()
                clean_data = SecurityService.validate_device_input(device_dict)
                
                # Check if device already exists
                existing = SecurityService.safe_query_execution(
                    db,
                    lambda db_session, dev_id: db_session.query(Device).filter(Device.device_id == dev_id).first(),
                    clean_data['device_id']
                )
                
                if existing:
                    logger.warning(f"Device {clean_data['device_id']} already exists")
                    return None
                
                device = Device(**clean_data)
                
                def create_device_transaction(db_session, dev):
                    db_session.add(dev)
                    db_session.commit()
                    db_session.refresh(dev)
                    return dev
                
                device = SecurityService.safe_query_execution(
                    db,
                    create_device_transaction,
                    device
                )
                
                return DeviceResponse.from_orm(device)
        except ValueError as e:
            logger.error(f"Device validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating device: {e}")
            return None
    
    async def get_device(self, device_id: str) -> Optional[DeviceResponse]:
        """Get device by ID with input sanitization"""
        try:
            # Sanitize device ID
            clean_device_id = SecurityService.sanitize_string(device_id, max_length=50)
            if not clean_device_id:
                return None
            
            async with self.get_session() as db:
                device = SecurityService.safe_query_execution(
                    db,
                    lambda db_session, dev_id: db_session.query(Device).filter(Device.device_id == dev_id).first(),
                    clean_device_id
                )
                return DeviceResponse.from_orm(device) if device else None
        except Exception as e:
            logger.error(f"Error getting device: {e}")
            return None
    
    async def get_all_devices(self) -> List[DeviceResponse]:
        """Get all devices with safe query execution"""
        try:
            async with self.get_session() as db:
                devices = SecurityService.safe_query_execution(
                    db,
                    lambda db_session: db_session.query(Device).all()
                )
                return [DeviceResponse.from_orm(device) for device in devices]
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            return []
    
    async def update_device(self, device_id: str, updates: DeviceUpdate) -> Optional[DeviceResponse]:
        """Update device with input validation and sanitization"""
        try:
            # Sanitize device ID
            clean_device_id = SecurityService.sanitize_string(device_id, max_length=50)
            if not clean_device_id:
                return None
            
            async with self.get_session() as db:
                device = SecurityService.safe_query_execution(
                    db,
                    lambda db_session, dev_id: db_session.query(Device).filter(Device.device_id == dev_id).first(),
                    clean_device_id
                )
                
                if not device:
                    return None
                
                # Validate and sanitize update data
                update_dict = updates.dict(exclude_unset=True)
                clean_updates = SecurityService.validate_device_input(update_dict)
                
                # Update device fields
                for field, value in clean_updates.items():
                    if hasattr(device, field):
                        setattr(device, field, value)
                
                device.updated_at = datetime.utcnow()
                
                def update_device_transaction(db_session, dev):
                    db_session.commit()
                    db_session.refresh(dev)
                    return dev
                
                device = SecurityService.safe_query_execution(
                    db,
                    update_device_transaction,
                    device
                )
                
                return DeviceResponse.from_orm(device)
        except ValueError as e:
            logger.error(f"Device update validation error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error updating device: {e}")
            return None
    
    async def update_device_status(self, device_id: str, status: str) -> bool:
        """Update device status and last seen"""
        try:
            async with self.get_session() as db:
                device = db.query(Device).filter(Device.device_id == device_id).first()
                if device:
                    device.status = status
                    device.last_seen = datetime.utcnow()
                    device.updated_at = datetime.utcnow()
                    db.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Error updating device status: {e}")
            return False
    
    # Telemetry operations
    async def store_telemetry(self, telemetry_data: TelemetryDataCreate) -> Optional[TelemetryDataResponse]:
        """Store telemetry data"""
        try:
            async with self.get_session() as db:
                telemetry = TelemetryData(**telemetry_data.dict())
                db.add(telemetry)
                db.commit()
                db.refresh(telemetry)
                
                return TelemetryDataResponse.from_orm(telemetry)
        except Exception as e:
            logger.error(f"Error storing telemetry: {e}")
            return None
    
    async def get_latest_telemetry(self, device_id: str, limit: int = 10) -> List[TelemetryDataResponse]:
        """Get latest telemetry data for a device"""
        try:
            async with self.get_session() as db:
                telemetry = db.query(TelemetryData).filter(
                    TelemetryData.device_id == device_id
                ).order_by(desc(TelemetryData.timestamp)).limit(limit).all()
                
                return [TelemetryDataResponse.from_orm(t) for t in telemetry]
        except Exception as e:
            logger.error(f"Error getting telemetry: {e}")
            return []
    
    async def get_telemetry_summary(self, device_id: str) -> Dict[str, Any]:
        """Get telemetry summary statistics"""
        try:
            async with self.get_session() as db:
                # Get latest reading
                latest = db.query(TelemetryData).filter(
                    TelemetryData.device_id == device_id
                ).order_by(desc(TelemetryData.timestamp)).first()
                
                if not latest:
                    return {}
                
                # Get averages for the last 24 hours
                yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                
                avg_data = db.query(
                    func.avg(TelemetryData.voltage).label('avg_voltage'),
                    func.avg(TelemetryData.current).label('avg_current'),
                    func.avg(TelemetryData.power).label('avg_power'),
                    func.avg(TelemetryData.temperature).label('avg_temperature'),
                    func.avg(TelemetryData.humidity).label('avg_humidity'),
                    func.count(TelemetryData.id).label('reading_count')
                ).filter(
                    TelemetryData.device_id == device_id,
                    TelemetryData.timestamp >= yesterday
                ).first()
                
                return {
                    "latest": TelemetryDataResponse.from_orm(latest).dict(),
                    "daily_averages": {
                        "voltage": float(avg_data.avg_voltage) if avg_data.avg_voltage else None,
                        "current": float(avg_data.avg_current) if avg_data.avg_current else None,
                        "power": float(avg_data.avg_power) if avg_data.avg_power else None,
                        "temperature": float(avg_data.avg_temperature) if avg_data.avg_temperature else None,
                        "humidity": float(avg_data.avg_humidity) if avg_data.avg_humidity else None,
                        "reading_count": avg_data.reading_count
                    }
                }
        except Exception as e:
            logger.error(f"Error getting telemetry summary: {e}")
            return {}
    
    # Relay state operations
    async def store_relay_state(self, relay_data: RelayStateCreate) -> Optional[RelayStateResponse]:
        """Store relay state"""
        try:
            async with self.get_session() as db:
                relay_state = RelayState(**relay_data.dict())
                db.add(relay_state)
                db.commit()
                db.refresh(relay_state)
                
                return RelayStateResponse.from_orm(relay_state)
        except Exception as e:
            logger.error(f"Error storing relay state: {e}")
            return None
    
    async def get_latest_relay_states(self, device_id: str) -> List[RelayStateResponse]:
        """Get latest relay states for a device"""
        try:
            async with self.get_session() as db:
                # Get the latest state for each relay
                subquery = db.query(
                    RelayState.relay_number,
                    func.max(RelayState.timestamp).label('max_timestamp')
                ).filter(RelayState.device_id == device_id).group_by(RelayState.relay_number).subquery()
                
                relay_states = db.query(RelayState).join(
                    subquery,
                    (RelayState.relay_number == subquery.c.relay_number) &
                    (RelayState.timestamp == subquery.c.max_timestamp)
                ).filter(RelayState.device_id == device_id).all()
                
                return [RelayStateResponse.from_orm(rs) for rs in relay_states]
        except Exception as e:
            logger.error(f"Error getting relay states: {e}")
            return []
    
    # System log operations
    async def log_system_event(self, log_data: SystemLogCreate) -> Optional[SystemLogResponse]:
        """Log system event"""
        try:
            async with self.get_session() as db:
                log_entry = SystemLog(**log_data.dict())
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                
                return SystemLogResponse.from_orm(log_entry)
        except Exception as e:
            logger.error(f"Error logging system event: {e}")
            return None
    
    async def get_system_logs(self, limit: int = 100, level: Optional[LogLevel] = None) -> List[SystemLogResponse]:
        """Get system logs"""
        try:
            async with self.get_session() as db:
                query = db.query(SystemLog)
                
                if level:
                    query = query.filter(SystemLog.level == level.value)
                
                logs = query.order_by(desc(SystemLog.timestamp)).limit(limit).all()
                return [SystemLogResponse.from_orm(log) for log in logs]
        except Exception as e:
            logger.error(f"Error getting system logs: {e}")
            return []
    
    # Dashboard operations
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary data"""
        try:
            async with self.get_session() as db:
                # Device counts
                total_devices = db.query(Device).count()
                online_devices = db.query(Device).filter(Device.status == DeviceStatus.ONLINE.value).count()
                offline_devices = db.query(Device).filter(Device.status == DeviceStatus.OFFLINE.value).count()
                
                # Recent telemetry count
                recent_telemetry = db.query(TelemetryData).filter(
                    TelemetryData.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
                
                # Recent system logs
                recent_errors = db.query(SystemLog).filter(
                    SystemLog.level == LogLevel.ERROR.value,
                    SystemLog.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
                
                return {
                    "devices": {
                        "total": total_devices,
                        "online": online_devices,
                        "offline": offline_devices,
                        "maintenance": total_devices - online_devices - offline_devices
                    },
                    "activity": {
                        "telemetry_readings_today": recent_telemetry,
                        "errors_today": recent_errors
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            return {}


# Global database service instance
db_service = DatabaseService()
