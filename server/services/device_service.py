"""
Secure device service for the IoT Dashboard.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.database import Device, TelemetryData, RelayState, DeviceCommand
from services.security_service import SecurityService, sanitize_inputs, SecureQueryBuilder
import logging

logger = logging.getLogger(__name__)


class DeviceService:
    """
    Secure device management service with SQL injection protection.
    """
    
    @staticmethod
    @sanitize_inputs()
    def create_device(db: Session, device_data: Dict[str, Any]) -> Device:
        """
        Create a new device with input validation and sanitization.
        
        Args:
            db: Database session
            device_data: Device data dictionary
            
        Returns:
            Created device object
            
        Raises:
            ValueError: If input validation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            # Validate and sanitize device input
            clean_data = SecurityService.validate_device_input(device_data)
            
            # Check if device ID already exists
            existing_device = DeviceService.get_device_by_id(db, clean_data.get('device_id', ''))
            if existing_device:
                raise ValueError("Device ID already exists")
            
            # Create device with sanitized data
            device = Device(
                device_id=clean_data['device_id'],
                name=clean_data.get('name', 'Unnamed Device'),
                location=clean_data.get('location'),
                status=clean_data.get('status', 'offline'),
                device_type=clean_data.get('device_type', 'IoT Device'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return SecurityService.safe_query_execution(
                db,
                lambda db, dev: _create_device_transaction(db, dev),
                device
            )
            
        except ValueError as e:
            logger.error(f"Device validation error: {str(e)}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error creating device: {str(e)}")
            raise
    
    @staticmethod
    @sanitize_inputs()
    def get_device_by_id(db: Session, device_id: str) -> Optional[Device]:
        """
        Get device by ID with input sanitization.
        
        Args:
            db: Database session
            device_id: Device ID
            
        Returns:
            Device object or None
        """
        clean_device_id = SecurityService.sanitize_string(device_id, max_length=50)
        if not clean_device_id:
            return None
        
        return SecurityService.safe_query_execution(
            db,
            lambda db, dev_id: db.query(Device).filter(Device.device_id == dev_id).first(),
            clean_device_id
        )
    
    @staticmethod
    @sanitize_inputs()
    def update_device(db: Session, device_id: str, update_data: Dict[str, Any]) -> Optional[Device]:
        """
        Update device with input validation and sanitization.
        
        Args:
            db: Database session
            device_id: Device ID
            update_data: Data to update
            
        Returns:
            Updated device object or None
        """
        # Get existing device
        device = DeviceService.get_device_by_id(db, device_id)
        if not device:
            return None
        
        try:
            # Validate and sanitize update data
            clean_data = SecurityService.validate_device_input(update_data)
            
            # Update fields
            allowed_updates = ['name', 'location', 'status', 'device_type']
            for field in allowed_updates:
                if field in clean_data:
                    setattr(device, field, clean_data[field])
            
            device.updated_at = datetime.utcnow()
            
            return SecurityService.safe_query_execution(
                db,
                lambda db, dev: _update_device_transaction(db, dev),
                device
            )
            
        except ValueError as e:
            logger.error(f"Device update validation error: {str(e)}")
            raise
    
    @staticmethod
    @sanitize_inputs()
    def search_devices(db: Session, search_term: str, limit: int = 50) -> List[Device]:
        """
        Search devices with secure query building.
        
        Args:
            db: Database session
            search_term: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching devices
        """
        # Validate limit
        safe_limit = min(max(int(limit), 1), 100)  # Limit between 1 and 100
        
        return SecureQueryBuilder.build_device_search_query(db, search_term, safe_limit)
    
    @staticmethod
    @sanitize_inputs()
    def get_devices_by_status(db: Session, status: str, limit: int = 100) -> List[Device]:
        """
        Get devices by status with input validation.
        
        Args:
            db: Database session
            status: Device status
            limit: Maximum number of results
            
        Returns:
            List of devices with specified status
        """
        # Validate status
        clean_status = SecurityService.sanitize_string(status, max_length=20).lower()
        if clean_status not in ['online', 'offline', 'maintenance']:
            raise ValueError("Invalid status. Must be 'online', 'offline', or 'maintenance'")
        
        # Validate limit
        safe_limit = min(max(int(limit), 1), 1000)
        
        return SecurityService.safe_query_execution(
            db,
            lambda db, stat, lim: db.query(Device).filter(Device.status == stat).limit(lim).all(),
            clean_status,
            safe_limit
        )
    
    @staticmethod
    @sanitize_inputs()
    def update_relay_state(db: Session, device_id: str, relay_number: int, state: bool, updated_by: str = "system") -> Optional[RelayState]:
        """
        Update relay state with input validation.
        
        Args:
            db: Database session
            device_id: Device ID
            relay_number: Relay number (1-4)
            state: Relay state (True/False)
            updated_by: Who updated the relay
            
        Returns:
            Updated relay state object or None
        """
        # Validate inputs
        clean_device_id = SecurityService.sanitize_string(device_id, max_length=50)
        clean_updated_by = SecurityService.sanitize_string(updated_by, max_length=50)
        
        if not clean_device_id:
            raise ValueError("Invalid device ID")
        
        if not isinstance(relay_number, int) or relay_number < 1 or relay_number > 4:
            raise ValueError("Relay number must be between 1 and 4")
        
        if not isinstance(state, bool):
            raise ValueError("Relay state must be boolean")
        
        # Check if device exists
        device = DeviceService.get_device_by_id(db, clean_device_id)
        if not device:
            raise ValueError("Device not found")
        
        # Create or update relay state
        relay_state = RelayState(
            device_id=clean_device_id,
            relay_number=relay_number,
            state=state,
            timestamp=datetime.utcnow(),
            updated_by=clean_updated_by
        )
        
        return SecurityService.safe_query_execution(
            db,
            lambda db, relay: _create_relay_state_transaction(db, relay),
            relay_state
        )
    
    @staticmethod
    @sanitize_inputs()
    def add_telemetry_data(db: Session, device_id: str, telemetry: Dict[str, Any]) -> Optional[TelemetryData]:
        """
        Add telemetry data with input validation.
        
        Args:
            db: Database session
            device_id: Device ID
            telemetry: Telemetry data
            
        Returns:
            Created telemetry data object or None
        """
        # Validate device ID
        clean_device_id = SecurityService.sanitize_string(device_id, max_length=50)
        if not clean_device_id:
            raise ValueError("Invalid device ID")
        
        # Check if device exists
        device = DeviceService.get_device_by_id(db, clean_device_id)
        if not device:
            raise ValueError("Device not found")
        
        # Sanitize telemetry data
        clean_telemetry = SecurityService.sanitize_dict(telemetry)
        
        # Validate numeric fields
        numeric_fields = ['voltage', 'current', 'power', 'temperature', 'humidity']
        validated_telemetry = {}
        
        for field in numeric_fields:
            if field in clean_telemetry:
                try:
                    value = float(clean_telemetry[field])
                    # Basic range validation
                    if field in ['voltage', 'current', 'power'] and (value < 0 or value > 10000):
                        logger.warning(f"Unusual {field} value: {value}")
                    if field in ['temperature'] and (value < -100 or value > 200):
                        logger.warning(f"Unusual temperature value: {value}")
                    if field in ['humidity'] and (value < 0 or value > 100):
                        logger.warning(f"Unusual humidity value: {value}")
                    
                    validated_telemetry[field] = value
                except (ValueError, TypeError):
                    logger.warning(f"Invalid {field} value: {clean_telemetry[field]}")
        
        # Create telemetry data
        telemetry_data = TelemetryData(
            device_id=clean_device_id,
            timestamp=datetime.utcnow(),
            voltage=validated_telemetry.get('voltage'),
            current=validated_telemetry.get('current'),
            power=validated_telemetry.get('power'),
            temperature=validated_telemetry.get('temperature'),
            humidity=validated_telemetry.get('humidity'),
            additional_data=str(clean_telemetry) if clean_telemetry else None
        )
        
        return SecurityService.safe_query_execution(
            db,
            lambda db, data: _create_telemetry_transaction(db, data),
            telemetry_data
        )


# Internal transaction functions
def _create_device_transaction(db: Session, device: Device) -> Device:
    """Internal function to handle device creation transaction."""
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def _update_device_transaction(db: Session, device: Device) -> Device:
    """Internal function to handle device update transaction."""
    db.commit()
    db.refresh(device)
    return device


def _create_relay_state_transaction(db: Session, relay_state: RelayState) -> RelayState:
    """Internal function to handle relay state creation transaction."""
    db.add(relay_state)
    db.commit()
    db.refresh(relay_state)
    return relay_state


def _create_telemetry_transaction(db: Session, telemetry_data: TelemetryData) -> TelemetryData:
    """Internal function to handle telemetry data creation transaction."""
    db.add(telemetry_data)
    db.commit()
    db.refresh(telemetry_data)
    return telemetry_data
