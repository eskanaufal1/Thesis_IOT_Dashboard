"""
Data router for IoT sensor data operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta

from app.database import get_db, User, SensorData
from app.models import (
    SensorDataCreate, SensorDataResponse, 
    MessageResponse, PaginatedResponse
)
from app.services.auth_service import get_current_active_user

# Create router
router = APIRouter()


@router.post("/sensors", response_model=SensorDataResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor_data(
    sensor_data: SensorDataCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new sensor data entry.
    
    Args:
        sensor_data: Sensor data to create
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        SensorDataResponse: Created sensor data
    """
    try:
        # Create sensor data entry
        db_sensor_data = SensorData(
            user_id=current_user.id,
            device_id=sensor_data.device_id,
            sensor_type=sensor_data.sensor_type,
            value=sensor_data.value,
            unit=sensor_data.unit,
            location=sensor_data.location,
            metadata_json=sensor_data.metadata_json
        )
        
        db.add(db_sensor_data)
        await db.commit()
        await db.refresh(db_sensor_data)
        
        return SensorDataResponse.model_validate(db_sensor_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sensor data: {str(e)}"
        )


@router.get("/sensors", response_model=List[SensorDataResponse])
async def get_sensor_data(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sensor data with optional filters.
    
    Args:
        device_id: Filter by device ID (optional)
        sensor_type: Filter by sensor type (optional)
        location: Filter by location (optional)
        limit: Maximum number of records to return
        offset: Number of records to skip
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[SensorDataResponse]: List of sensor data
    """
    try:
        # Build query
        query = select(SensorData).where(SensorData.user_id == current_user.id)
        
        if device_id:
            query = query.where(SensorData.device_id == device_id)
        
        if sensor_type:
            query = query.where(SensorData.sensor_type == sensor_type)
        
        if location:
            query = query.where(SensorData.location == location)
        
        query = query.order_by(desc(SensorData.timestamp))
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        sensor_data = result.scalars().all()
        
        return [SensorDataResponse.model_validate(data) for data in sensor_data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sensor data: {str(e)}"
        )


@router.get("/sensors/recent", response_model=List[SensorDataResponse])
async def get_recent_sensor_data(
    hours: int = 24,
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent sensor data from the last N hours.
    
    Args:
        hours: Number of hours to look back
        device_id: Filter by device ID (optional)
        sensor_type: Filter by sensor type (optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[SensorDataResponse]: List of recent sensor data
    """
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = select(SensorData).where(
            SensorData.user_id == current_user.id,
            SensorData.timestamp >= time_threshold
        )
        
        if device_id:
            query = query.where(SensorData.device_id == device_id)
        
        if sensor_type:
            query = query.where(SensorData.sensor_type == sensor_type)
        
        query = query.order_by(desc(SensorData.timestamp))
        
        # Execute query
        result = await db.execute(query)
        sensor_data = result.scalars().all()
        
        return [SensorDataResponse.model_validate(data) for data in sensor_data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent sensor data: {str(e)}"
        )


@router.get("/sensors/devices", response_model=List[str])
async def get_devices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of unique device IDs for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[str]: List of unique device IDs
    """
    try:
        # Get unique device IDs
        result = await db.execute(
            select(SensorData.device_id)
            .where(SensorData.user_id == current_user.id)
            .distinct()
        )
        device_ids = result.scalars().all()
        
        return device_ids
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve devices: {str(e)}"
        )


@router.get("/sensors/types", response_model=List[str])
async def get_sensor_types(
    device_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of unique sensor types for current user.
    
    Args:
        device_id: Filter by device ID (optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[str]: List of unique sensor types
    """
    try:
        # Build query
        query = select(SensorData.sensor_type).where(
            SensorData.user_id == current_user.id
        )
        
        if device_id:
            query = query.where(SensorData.device_id == device_id)
        
        query = query.distinct()
        
        # Execute query
        result = await db.execute(query)
        sensor_types = result.scalars().all()
        
        return sensor_types
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sensor types: {str(e)}"
        )


@router.get("/sensors/statistics")
async def get_sensor_statistics(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    hours: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sensor data statistics.
    
    Args:
        device_id: Filter by device ID (optional)
        sensor_type: Filter by sensor type (optional)
        hours: Number of hours to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Statistics including count, min, max, avg values
    """
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = select(
            func.count(SensorData.id).label('count'),
            func.min(SensorData.value).label('min_value'),
            func.max(SensorData.value).label('max_value'),
            func.avg(SensorData.value).label('avg_value')
        ).where(
            SensorData.user_id == current_user.id,
            SensorData.timestamp >= time_threshold
        )
        
        if device_id:
            query = query.where(SensorData.device_id == device_id)
        
        if sensor_type:
            query = query.where(SensorData.sensor_type == sensor_type)
        
        # Execute query
        result = await db.execute(query)
        stats = result.first()
        
        return {
            "count": stats.count or 0,
            "min_value": float(stats.min_value) if stats.min_value else None,
            "max_value": float(stats.max_value) if stats.max_value else None,
            "avg_value": float(stats.avg_value) if stats.avg_value else None,
            "time_range_hours": hours
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.delete("/sensors", response_model=MessageResponse)
async def delete_sensor_data(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete sensor data with optional filters.
    
    Args:
        device_id: Filter by device ID (optional)
        sensor_type: Filter by sensor type (optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Success message
    """
    try:
        # Build delete query
        query = SensorData.__table__.delete().where(
            SensorData.user_id == current_user.id
        )
        
        if device_id:
            query = query.where(SensorData.device_id == device_id)
        
        if sensor_type:
            query = query.where(SensorData.sensor_type == sensor_type)
        
        # Execute delete
        result = await db.execute(query)
        await db.commit()
        
        return MessageResponse(
            message=f"Deleted {result.rowcount} sensor data records"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sensor data: {str(e)}"
        )
