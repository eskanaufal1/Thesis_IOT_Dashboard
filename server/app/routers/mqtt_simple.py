"""
MQTT router for MQTT operations and status monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta

from app.database import get_db, User, MQTTMessage as MQTTMessageModel
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


@router.get("/messages")
async def get_mqtt_messages(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get MQTT message history.
    
    Args:
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[MQTTMessage]: List of MQTT messages
    """
    try:
        # Get MQTT messages from database
        query = select(MQTTMessageModel).order_by(desc(MQTTMessageModel.timestamp))
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return {
            "messages": [
                {
                    "id": msg.id,
                    "topic": msg.topic,
                    "payload": msg.payload,
                    "qos": msg.qos,
                    "retain": msg.retain,
                    "timestamp": msg.timestamp,
                    "message_type": msg.message_type
                }
                for msg in messages
            ],
            "total": len(messages),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve MQTT messages: {str(e)}"
        )


@router.post("/publish")
async def publish_message(
    topic: str,
    payload: str,
    qos: int = 0,
    retain: bool = False,
    broker_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Publish a message to MQTT broker.
    
    Args:
        topic: MQTT topic
        payload: Message payload
        qos: Quality of service (0, 1, or 2)
        retain: Retain flag
        broker_id: Specific broker ID (optional)
        current_user: Current authenticated user
        
    Returns:
        Dict: Publication result
    """
    mqtt_service = get_enhanced_mqtt_service()
    if not mqtt_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MQTT service not available"
        )
    
    try:
        if broker_id:
            # Publish to specific broker
            success = await mqtt_service.publish_to_broker(broker_id, topic, payload, qos, retain)
            if success:
                return {
                    "message": "Message published successfully",
                    "topic": topic,
                    "broker_id": broker_id,
                    "timestamp": datetime.utcnow()
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to publish message"
                )
        else:
            # Publish to all connected brokers
            statuses = await mqtt_service.get_all_brokers_status()
            connected_brokers = [status for status in statuses if status["connected"]]
            
            if not connected_brokers:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="No connected MQTT brokers available"
                )
            
            results = []
            for broker_status in connected_brokers:
                broker_id = broker_status["broker_id"]
                success = await mqtt_service.publish_to_broker(broker_id, topic, payload, qos, retain)
                results.append({
                    "broker_id": broker_id,
                    "success": success
                })
            
            return {
                "message": "Message published to all connected brokers",
                "topic": topic,
                "results": results,
                "timestamp": datetime.utcnow()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish message: {str(e)}"
        )
