"""
Device management API routes for the IoT Dashboard.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from config.database import get_db
from models.user import User
from models.database import Device, TelemetryData, RelayState
from services.device_service import DeviceService
from services.security_service import SecurityService
from api.auth import get_current_user

router = APIRouter(prefix="/api/devices", tags=["Device Management"])


@router.get("/", response_model=List[dict])
async def get_all_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all devices for the current user."""
    try:
        devices = SecurityService.safe_query_execution(
            db,
            lambda db_session: db_session.query(Device).all()
        )
        
        return [
            {
                "id": device.id,
                "device_id": device.device_id,
                "name": device.name,
                "location": device.location,
                "status": device.status,
                "device_type": device.device_type,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "created_at": device.created_at.isoformat() if device.created_at else None,
                "updated_at": device.updated_at.isoformat() if device.updated_at else None,
            }
            for device in devices
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve devices"
        )


@router.get("/{device_id}")
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific device by ID."""
    device = DeviceService.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return {
        "id": device.id,
        "device_id": device.device_id,
        "name": device.name,
        "location": device.location,
        "status": device.status,
        "device_type": device.device_type,
        "last_seen": device.last_seen.isoformat() if device.last_seen else None,
        "created_at": device.created_at.isoformat() if device.created_at else None,
        "updated_at": device.updated_at.isoformat() if device.updated_at else None,
    }


@router.post("/", response_model=dict)
async def create_device(
    device_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new device."""
    try:
        device = DeviceService.create_device(db, device_data)
        return {
            "id": device.id,
            "device_id": device.device_id,
            "name": device.name,
            "location": device.location,
            "status": device.status,
            "device_type": device.device_type,
            "created_at": device.created_at.isoformat() if device.created_at else None,
            "updated_at": device.updated_at.isoformat() if device.updated_at else None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create device"
        )


@router.put("/{device_id}")
async def update_device(
    device_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a device."""
    try:
        device = DeviceService.update_device(db, device_id, update_data)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        return {
            "id": device.id,
            "device_id": device.device_id,
            "name": device.name,
            "location": device.location,
            "status": device.status,
            "device_type": device.device_type,
            "updated_at": device.updated_at.isoformat() if device.updated_at else None,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device"
        )


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a device."""
    try:
        device = DeviceService.get_device_by_id(db, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Delete device using safe query execution
        SecurityService.safe_query_execution(
            db,
            lambda db_session, dev: _delete_device_transaction(db_session, dev),
            device
        )
        
        return {"message": "Device deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete device"
        )


def _delete_device_transaction(db: Session, device: Device):
    """Internal function to handle device deletion transaction."""
    db.delete(device)
    db.commit()


@router.get("/search")
async def search_devices(
    q: str = Query(..., description="Search term"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search devices by name, location, or device ID."""
    try:
        devices = DeviceService.search_devices(db, q, limit)
        
        return [
            {
                "id": device.id,
                "device_id": device.device_id,
                "name": device.name,
                "location": device.location,
                "status": device.status,
                "device_type": device.device_type,
            }
            for device in devices
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search devices"
        )


@router.get("/status/{status}")
async def get_devices_by_status(
    status: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get devices by status (online, offline, maintenance)."""
    try:
        devices = DeviceService.get_devices_by_status(db, status, limit)
        
        return [
            {
                "id": device.id,
                "device_id": device.device_id,
                "name": device.name,
                "location": device.location,
                "status": device.status,
                "device_type": device.device_type,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
            }
            for device in devices
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get devices by status"
        )


@router.get("/{device_id}/telemetry")
async def get_device_telemetry(
    device_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get telemetry data for a specific device."""
    try:
        # Verify device exists
        device = DeviceService.get_device_by_id(db, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Get telemetry data with safe query execution
        telemetry_data = SecurityService.safe_query_execution(
            db,
            lambda db_session, dev_id, lim: (
                db_session.query(TelemetryData)
                .filter(TelemetryData.device_id == dev_id)
                .order_by(TelemetryData.timestamp.desc())
                .limit(lim)
                .all()
            ),
            device_id,
            limit
        )
        
        return [
            {
                "id": data.id,
                "device_id": data.device_id,
                "timestamp": data.timestamp.isoformat() if data.timestamp else None,
                "voltage": data.voltage,
                "current": data.current,
                "power": data.power,
                "temperature": data.temperature,
                "humidity": data.humidity,
                "additional_data": data.additional_data,
            }
            for data in telemetry_data
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve telemetry data"
        )


@router.post("/{device_id}/relay/{relay_number}")
async def control_relay(
    device_id: str,
    relay_number: int,
    relay_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Control device relay state."""
    try:
        # Validate relay number
        if relay_number not in [1, 2, 3, 4]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Relay number must be between 1 and 4"
            )
        
        # Verify device exists
        device = DeviceService.get_device_by_id(db, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Sanitize relay data
        clean_data = SecurityService.sanitize_dict(relay_data, ["state"])
        if "state" not in clean_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Relay state is required"
            )
        
        # Convert state to boolean
        state = str(clean_data["state"]).lower() in ["true", "1", "on"]
        
        # Update relay state
        relay_state = DeviceService.update_relay_state(
            db, device_id, relay_number, state, current_user.username
        )
        
        if not relay_state:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update relay state"
            )
        
        return {
            "device_id": device_id,
            "relay_number": relay_number,
            "state": state,
            "updated_by": current_user.username,
            "timestamp": relay_state.timestamp.isoformat() if relay_state.timestamp else None,
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to control relay"
        )


@router.get("/{device_id}/relays")
async def get_device_relays(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current relay states for a device."""
    try:
        # Verify device exists
        device = DeviceService.get_device_by_id(db, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Get relay states with safe query execution
        relay_states = SecurityService.safe_query_execution(
            db,
            lambda db_session, dev_id: (
                db_session.query(RelayState)
                .filter(RelayState.device_id == dev_id)
                .order_by(RelayState.relay_number, RelayState.timestamp.desc())
                .all()
            ),
            device_id
        )
        
        # Group by relay number and get latest state
        relay_dict = {}
        for relay in relay_states:
            if relay.relay_number not in relay_dict:
                relay_dict[relay.relay_number] = {
                    "relay_number": relay.relay_number,
                    "state": relay.state,
                    "timestamp": relay.timestamp.isoformat() if relay.timestamp else None,
                    "updated_by": relay.updated_by,
                }
        
        return list(relay_dict.values())
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve relay states"
        )
