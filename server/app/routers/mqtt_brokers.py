"""
MQTT Broker management API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db, User, MQTTBroker, Device
from app.services.auth_service import get_current_active_user as get_current_user
from app.services.enhanced_mqtt_service import enhanced_mqtt_service


router = APIRouter()


class MQTTBrokerCreate(BaseModel):
    broker_name: str
    broker_host: str
    broker_port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None


class MQTTBrokerUpdate(BaseModel):
    broker_name: Optional[str] = None
    broker_host: Optional[str] = None
    broker_port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class MQTTBrokerResponse(BaseModel):
    id: int
    broker_name: str
    broker_host: str
    broker_port: int
    username: Optional[str] = None
    is_active: bool
    is_connected: bool
    last_connected: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceCreate(BaseModel):
    mqtt_broker_id: int
    device_name: str
    device_id: str
    device_type: str
    location: Optional[str] = None
    description: Optional[str] = None


class DeviceResponse(BaseModel):
    id: int
    mqtt_broker_id: int
    device_name: str
    device_id: str
    device_type: str
    location: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    mqtt_broker: MQTTBrokerResponse

    class Config:
        from_attributes = True


class MQTTBrokerStatusResponse(BaseModel):
    broker_id: int
    broker_name: str
    broker_host: str
    broker_port: int
    is_active: bool
    connected: bool
    last_connected: Optional[datetime] = None
    last_message: Optional[datetime] = None


class MQTTControlRequest(BaseModel):
    action: str  # "connect" or "disconnect"


@router.post("/brokers", response_model=MQTTBrokerResponse)
async def create_mqtt_broker(
    broker_data: MQTTBrokerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new MQTT broker configuration."""
    
    # Check if broker with same name already exists for this user
    result = await db.execute(
        select(MQTTBroker).where(
            MQTTBroker.user_id == current_user.id,
            MQTTBroker.broker_name == broker_data.broker_name
        )
    )
    existing_broker = result.scalar_one_or_none()
    
    if existing_broker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Broker with this name already exists"
        )
    
    # Create new broker
    new_broker = MQTTBroker(
        user_id=current_user.id,
        broker_name=broker_data.broker_name,
        broker_host=broker_data.broker_host,
        broker_port=broker_data.broker_port,
        username=broker_data.username,
        password=broker_data.password
    )
    
    db.add(new_broker)
    await db.commit()
    await db.refresh(new_broker)
    
    # Add to MQTT service
    broker_config = {
        'broker_host': new_broker.broker_host,
        'broker_port': new_broker.broker_port,
        'username': new_broker.username,
        'password': new_broker.password
    }
    
    await enhanced_mqtt_service.add_broker(new_broker.id, broker_config)
    
    return new_broker


@router.get("/brokers", response_model=List[MQTTBrokerResponse])
async def get_mqtt_brokers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all MQTT brokers for the current user."""
    
    result = await db.execute(
        select(MQTTBroker).where(MQTTBroker.user_id == current_user.id)
    )
    brokers = result.scalars().all()
    
    return brokers


@router.get("/brokers/{broker_id}", response_model=MQTTBrokerResponse)
async def get_mqtt_broker(
    broker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific MQTT broker."""
    
    result = await db.execute(
        select(MQTTBroker).where(
            MQTTBroker.id == broker_id,
            MQTTBroker.user_id == current_user.id
        )
    )
    broker = result.scalar_one_or_none()
    
    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )
    
    return broker


@router.put("/brokers/{broker_id}", response_model=MQTTBrokerResponse)
async def update_mqtt_broker(
    broker_id: int,
    broker_data: MQTTBrokerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an MQTT broker configuration."""
    
    result = await db.execute(
        select(MQTTBroker).where(
            MQTTBroker.id == broker_id,
            MQTTBroker.user_id == current_user.id
        )
    )
    broker = result.scalar_one_or_none()
    
    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )
    
    # Update broker fields
    update_data = broker_data.dict(exclude_unset=True)
    if update_data:
        update_data['updated_at'] = datetime.utcnow()
        
        await db.execute(
            update(MQTTBroker)
            .where(MQTTBroker.id == broker_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(broker)
    
    # Update MQTT service connection if broker config changed
    if any(key in update_data for key in ['broker_host', 'broker_port', 'username', 'password']):
        await enhanced_mqtt_service.remove_broker(broker_id)
        
        if broker.is_active:
            broker_config = {
                'broker_host': broker.broker_host,
                'broker_port': broker.broker_port,
                'username': broker.username,
                'password': broker.password
            }
            await enhanced_mqtt_service.add_broker(broker_id, broker_config)
    
    return broker


@router.delete("/brokers/{broker_id}")
async def delete_mqtt_broker(
    broker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an MQTT broker configuration."""
    
    result = await db.execute(
        select(MQTTBroker).where(
            MQTTBroker.id == broker_id,
            MQTTBroker.user_id == current_user.id
        )
    )
    broker = result.scalar_one_or_none()
    
    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )
    
    # Remove from MQTT service
    await enhanced_mqtt_service.remove_broker(broker_id)
    
    # Delete from database
    await db.execute(
        delete(MQTTBroker).where(MQTTBroker.id == broker_id)
    )
    await db.commit()
    
    return {"message": "Broker deleted successfully"}


@router.post("/brokers/{broker_id}/control")
async def control_mqtt_broker(
    broker_id: int,
    control_data: MQTTControlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Control MQTT broker connection (connect/disconnect)."""
    
    result = await db.execute(
        select(MQTTBroker).where(
            MQTTBroker.id == broker_id,
            MQTTBroker.user_id == current_user.id
        )
    )
    broker = result.scalar_one_or_none()
    
    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )
    
    if control_data.action == "connect":
        success = await enhanced_mqtt_service.connect_broker(broker_id)
        if success:
            return {"message": "Broker connected successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to connect to broker"
            )
    
    elif control_data.action == "disconnect":
        success = await enhanced_mqtt_service.disconnect_broker(broker_id)
        if success:
            return {"message": "Broker disconnected successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to disconnect from broker"
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Use 'connect' or 'disconnect'"
        )


@router.get("/status", response_model=List[MQTTBrokerStatusResponse])
async def get_mqtt_brokers_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of all MQTT brokers for the current user."""
    
    # Get all brokers for current user
    result = await db.execute(
        select(MQTTBroker).where(MQTTBroker.user_id == current_user.id)
    )
    brokers = result.scalars().all()
    
    # Get status from MQTT service
    all_statuses = await enhanced_mqtt_service.get_all_brokers_status()
    
    # Filter statuses for current user's brokers
    user_broker_ids = {broker.id for broker in brokers}
    user_statuses = [
        status for status in all_statuses 
        if status["broker_id"] in user_broker_ids
    ]
    
    return user_statuses


@router.get("/brokers/{broker_id}/status", response_model=MQTTBrokerStatusResponse)
async def get_mqtt_broker_status(
    broker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of a specific MQTT broker."""
    
    result = await db.execute(
        select(MQTTBroker).where(
            MQTTBroker.id == broker_id,
            MQTTBroker.user_id == current_user.id
        )
    )
    broker = result.scalar_one_or_none()
    
    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker not found"
        )
    
    status = await enhanced_mqtt_service.get_broker_status(broker_id)
    
    if not status:
        # Return broker info with disconnected status
        return MQTTBrokerStatusResponse(
            broker_id=broker.id,
            broker_name=broker.broker_name,
            broker_host=broker.broker_host,
            broker_port=broker.broker_port,
            is_active=broker.is_active,
            connected=False,
            last_connected=broker.last_connected,
            last_message=None
        )
    
    return MQTTBrokerStatusResponse(
        broker_id=broker.id,
        broker_name=broker.broker_name,
        broker_host=broker.broker_host,
        broker_port=broker.broker_port,
        is_active=broker.is_active,
        connected=status["connected"],
        last_connected=status["last_connected"],
        last_message=status["last_message"]
    )


# Device management endpoints
@router.post("/devices", response_model=DeviceResponse)
async def create_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new device."""
    
    # Check if broker exists and belongs to user
    result = await db.execute(
        select(MQTTBroker).where(
            MQTTBroker.id == device_data.mqtt_broker_id,
            MQTTBroker.user_id == current_user.id
        )
    )
    broker = result.scalar_one_or_none()
    
    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MQTT broker not found"
        )
    
    # Check if device with same device_id already exists
    result = await db.execute(
        select(Device).where(
            Device.device_id == device_data.device_id,
            Device.user_id == current_user.id
        )
    )
    existing_device = result.scalar_one_or_none()
    
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    
    # Create new device
    new_device = Device(
        user_id=current_user.id,
        mqtt_broker_id=device_data.mqtt_broker_id,
        device_name=device_data.device_name,
        device_id=device_data.device_id,
        device_type=device_data.device_type,
        location=device_data.location,
        description=device_data.description
    )
    
    db.add(new_device)
    await db.commit()
    await db.refresh(new_device)
    
    return new_device


@router.get("/devices", response_model=List[DeviceResponse])
async def get_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all devices for the current user."""
    
    result = await db.execute(
        select(Device).where(Device.user_id == current_user.id)
    )
    devices = result.scalars().all()
    
    return devices
