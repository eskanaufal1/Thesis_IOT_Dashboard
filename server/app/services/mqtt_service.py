"""
MQTT service for handling MQTT client connections and message publishing/subscribing.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from paho.mqtt.client import Client as MQTTClient, MQTTMessage, CallbackAPIVersion
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, MQTTMessage as MQTTMessageModel


class MQTTService:
    """
    MQTT service for handling MQTT client connections and message operations.
    """
    
    def __init__(self):
        self.client: Optional[MQTTClient] = None
        self.is_connected: bool = False
        self.broker_host: str = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        self.username: Optional[str] = os.getenv("MQTT_USERNAME")
        self.password: Optional[str] = os.getenv("MQTT_PASSWORD")
        self.last_connected: Optional[datetime] = None
        self.last_message: Optional[datetime] = None
        self.message_callbacks: Dict[str, Callable] = {}
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    async def connect(self) -> bool:
        """
        Connect to MQTT broker.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.loop = asyncio.get_event_loop()
            self.client = MQTTClient(callback_api_version=CallbackAPIVersion.VERSION1)
            
            # Set username and password if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Connect to broker
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # Start the loop in a separate thread
            self.client.loop_start()
            
            # Wait for connection
            await asyncio.sleep(1)
            
            return self.is_connected
            
        except Exception as e:
            print(f"MQTT connection error: {e}")
            return False
    
    async def disconnect(self):
        """
        Disconnect from MQTT broker.
        """
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for MQTT client connection.
        
        Args:
            client: MQTT client instance
            userdata: User data
            flags: Response flags
            rc: Response code
        """
        if rc == 0:
            self.is_connected = True
            self.last_connected = datetime.utcnow()
            print(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            
            # Subscribe to default topics
            self.client.subscribe("sensors/+/data")
            self.client.subscribe("devices/+/status")
        else:
            print(f"Failed to connect to MQTT broker, return code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        Callback for MQTT client disconnection.
        
        Args:
            client: MQTT client instance
            userdata: User data
            rc: Response code
        """
        self.is_connected = False
        print(f"Disconnected from MQTT broker, return code {rc}")
    
    def _on_message(self, client, userdata, msg: MQTTMessage):
        """
        Callback for received MQTT messages.
        
        Args:
            client: MQTT client instance
            userdata: User data
            msg: MQTT message
        """
        self.last_message = datetime.utcnow()
        
        # Schedule async message handling
        if self.loop and self.loop.is_running():
            asyncio.create_task(self._handle_message_async(msg))
    
    async def _handle_message_async(self, msg: MQTTMessage):
        """
        Handle received MQTT message asynchronously.
        
        Args:
            msg: MQTT message
        """
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Store message in database
            await self._store_message(topic, payload, msg.qos, msg.retain, "received")
            
            # Handle specific topic callbacks
            for topic_pattern, callback in self.message_callbacks.items():
                if self._topic_matches(topic, topic_pattern):
                    await callback(topic, payload)
            
            # Handle sensor data messages
            if topic.startswith("sensors/") and topic.endswith("/data"):
                await self._handle_sensor_data(topic, payload)
                
        except Exception as e:
            print(f"Error handling MQTT message: {e}")
    
    def _topic_matches(self, topic: str, pattern: str) -> bool:
        """
        Check if topic matches pattern (supports + and # wildcards).
        
        Args:
            topic: The topic to check
            pattern: The pattern to match against
            
        Returns:
            bool: True if topic matches pattern
        """
        topic_parts = topic.split('/')
        pattern_parts = pattern.split('/')
        
        if len(pattern_parts) > len(topic_parts):
            return False
        
        for i, pattern_part in enumerate(pattern_parts):
            if pattern_part == "#":
                return True
            elif pattern_part == "+":
                continue
            elif i >= len(topic_parts) or pattern_part != topic_parts[i]:
                return False
        
        return len(pattern_parts) == len(topic_parts)
    
    async def _handle_sensor_data(self, topic: str, payload: str):
        """
        Handle sensor data messages and store in database.
        
        Args:
            topic: MQTT topic
            payload: Message payload
        """
        try:
            # Parse sensor data from payload
            data = json.loads(payload)
            
            # Extract device ID from topic (sensors/{device_id}/data)
            device_id = topic.split('/')[1]
            
            # Store sensor data (would need user authentication for real implementation)
            # For now, store with user_id = 1 (admin)
            from app.database import SensorData
            
            async with async_session_factory() as db:
                sensor_data = SensorData(
                    user_id=1,  # Default to admin user
                    device_id=device_id,
                    sensor_type=data.get('sensor_type', 'unknown'),
                    value=float(data.get('value', 0)),
                    unit=data.get('unit'),
                    location=data.get('location'),
                    metadata_json=json.dumps(data.get('metadata', {}))
                )
                
                db.add(sensor_data)
                await db.commit()
                
        except Exception as e:
            print(f"Error handling sensor data: {e}")
    
    async def _store_message(self, topic: str, payload: str, qos: int, retain: bool, message_type: str):
        """
        Store MQTT message in database.
        
        Args:
            topic: MQTT topic
            payload: Message payload
            qos: Quality of service
            retain: Retain flag
            message_type: Message type ("sent" or "received")
        """
        try:
            async with async_session_factory() as db:
                mqtt_message = MQTTMessageModel(
                    topic=topic,
                    payload=payload,
                    qos=qos,
                    retain=retain,
                    message_type=message_type
                )
                
                db.add(mqtt_message)
                await db.commit()
                
        except Exception as e:
            print(f"Error storing MQTT message: {e}")
    
    async def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """
        Publish message to MQTT topic.
        
        Args:
            topic: MQTT topic
            payload: Message payload
            qos: Quality of service (0, 1, or 2)
            retain: Retain flag
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self.is_connected or not self.client:
            return False
        
        try:
            # Publish message
            result = self.client.publish(topic, payload, qos, retain)
            
            # Store message in database
            await self._store_message(topic, payload, qos, retain, "sent")
            
            return result.rc == 0
            
        except Exception as e:
            print(f"Error publishing MQTT message: {e}")
            return False
    
    async def subscribe(self, topic: str, callback: Optional[Callable] = None) -> bool:
        """
        Subscribe to MQTT topic.
        
        Args:
            topic: MQTT topic to subscribe to
            callback: Optional callback function for messages
            
        Returns:
            bool: True if subscribed successfully, False otherwise
        """
        if not self.is_connected or not self.client:
            return False
        
        try:
            result = self.client.subscribe(topic)
            
            if callback:
                self.message_callbacks[topic] = callback
            
            return result[0] == 0
            
        except Exception as e:
            print(f"Error subscribing to MQTT topic: {e}")
            return False
    
    async def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from MQTT topic.
        
        Args:
            topic: MQTT topic to unsubscribe from
            
        Returns:
            bool: True if unsubscribed successfully, False otherwise
        """
        if not self.is_connected or not self.client:
            return False
        
        try:
            result = self.client.unsubscribe(topic)
            
            # Remove callback
            if topic in self.message_callbacks:
                del self.message_callbacks[topic]
            
            return result[0] == 0
            
        except Exception as e:
            print(f"Error unsubscribing from MQTT topic: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get MQTT connection status.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            "connected": self.is_connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "last_connected": self.last_connected,
            "last_message": self.last_message
        }
