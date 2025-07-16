"""
MQTT router for MQTT operations and status monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta

from app.database import get_db, User, MQTTMessage as MQTTMessageModel
from app.models import (
    MQTTPublish, MQTTStatus, MQTTMessageResponse, 
    MessageResponse, PaginatedResponse
)
from app.services.auth_service import get_current_active_user
from app.dependencies import get_enhanced_mqtt_service

# Create router
router = APIRouter()


@router.get("/status")
async def get_mqtt_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get MQTT connection status for all brokers.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict: MQTT connection status for all brokers
    """
    mqtt_service = get_enhanced_mqtt_service()
    if not mqtt_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not available"
        )
    
    try:
        statuses = await mqtt_service.get_all_brokers_status()
        user_brokers = [status for status in statuses if status["broker_id"]]
        
        # Legacy format for backwards compatibility
        connected_count = sum(1 for status in user_brokers if status["connected"])
        
        return {
            "connected": connected_count > 0,
            "broker_count": len(user_brokers),
            "connected_brokers": connected_count,
            "brokers": user_brokers,
            "last_connected": max(
                (status["last_connected"] for status in user_brokers if status["last_connected"]),
                default=None
            ),
            "last_message": max(
                (status["last_message"] for status in user_brokers if status["last_message"]),
                default=None
            )
        }
    except Exception as e:
        return {
            "connected": False,
            "broker_count": 0,
            "connected_brokers": 0,
            "brokers": [],
            "last_connected": None,
            "last_message": None,
            "error": str(e)
        }


@router.post("/publish", response_model=MessageResponse)
async def publish_message(
    message: MQTTPublish,
    current_user: User = Depends(get_current_active_user)
):
    """
    Publish message to MQTT topic.
    
    Args:
        message: MQTT message to publish
        current_user: Current authenticated user
        
    Returns:
        MessageResponse: Success message
    """
    mqtt_service = get_mqtt_service()
    if not mqtt_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not available"
        )
    
    if not mqtt_service.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not connected"
        )
    
    success = await mqtt_service.publish(
        topic=message.topic,
        payload=message.payload,
        qos=message.qos,
        retain=message.retain
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish message"
        )
    
    return MessageResponse(message="Message published successfully")


@router.post("/subscribe", response_model=MessageResponse)
async def subscribe_topic(
    topic: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Subscribe to MQTT topic.
    
    Args:
        topic: MQTT topic to subscribe to
        current_user: Current authenticated user
        
    Returns:
        MessageResponse: Success message
    """
    mqtt_service = get_mqtt_service()
    if not mqtt_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not available"
        )
    
    if not mqtt_service.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not connected"
        )
    
    success = await mqtt_service.subscribe(topic)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to subscribe to topic"
        )
    
    return MessageResponse(message=f"Subscribed to topic: {topic}")


@router.post("/unsubscribe", response_model=MessageResponse)
async def unsubscribe_topic(
    topic: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Unsubscribe from MQTT topic.
    
    Args:
        topic: MQTT topic to unsubscribe from
        current_user: Current authenticated user
        
    Returns:
        MessageResponse: Success message
    """
    mqtt_service = get_mqtt_service()
    if not mqtt_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not available"
        )
    
    if not mqtt_service.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not connected"
        )
    
    success = await mqtt_service.unsubscribe(topic)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe from topic"
        )
    
    return MessageResponse(message=f"Unsubscribed from topic: {topic}")


@router.get("/messages", response_model=List[MQTTMessageResponse])
async def get_mqtt_messages(
    topic: Optional[str] = None,
    message_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get MQTT messages from database.
    
    Args:
        topic: Filter by topic (optional)
        message_type: Filter by message type (optional)
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[MQTTMessageResponse]: List of MQTT messages
    """
    try:
        # Build query
        query = select(MQTTMessageModel)
        
        if topic:
            query = query.where(MQTTMessageModel.topic == topic)
        
        if message_type:
            query = query.where(MQTTMessageModel.message_type == message_type)
        
        query = query.order_by(desc(MQTTMessageModel.timestamp))
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return [MQTTMessageResponse.model_validate(msg) for msg in messages]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.get("/messages/recent", response_model=List[MQTTMessageResponse])
async def get_recent_messages(
    hours: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent MQTT messages from the last N hours.
    
    Args:
        hours: Number of hours to look back
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[MQTTMessageResponse]: List of recent MQTT messages
    """
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = select(MQTTMessageModel).where(
            MQTTMessageModel.timestamp >= time_threshold
        ).order_by(desc(MQTTMessageModel.timestamp))
        
        # Execute query
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return [MQTTMessageResponse.model_validate(msg) for msg in messages]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent messages: {str(e)}"
        )


@router.delete("/messages", response_model=MessageResponse)
async def clear_mqtt_messages(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear all MQTT messages (admin only).
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Success message
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        # Delete all messages
        await db.execute(MQTTMessageModel.__table__.delete())
        await db.commit()
        
        return MessageResponse(message="All MQTT messages cleared")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear messages: {str(e)}"
        )
