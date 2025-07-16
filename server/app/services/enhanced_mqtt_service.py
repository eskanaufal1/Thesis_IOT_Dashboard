"""
Enhanced MQTT service for handling multiple MQTT broker connections.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from paho.mqtt.client import Client as MQTTClient, MQTTMessage, CallbackAPIVersion
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import async_session_factory, MQTTMessage as MQTTMessageModel, MQTTBroker, Device, SensorData


class MQTTBrokerConnection:
    """
    Individual MQTT broker connection handler.
    """
    
    def __init__(self, broker_id: int, broker_config: Dict[str, Any]):
        self.broker_id = broker_id
        self.broker_config = broker_config
        self.client: Optional[MQTTClient] = None
        self.is_connected: bool = False
        self.last_connected: Optional[datetime] = None
        self.last_message: Optional[datetime] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
    async def connect(self) -> bool:
        """
        Connect to the MQTT broker.
        """
        try:
            self.loop = asyncio.get_event_loop()
            self.client = MQTTClient(
                client_id=f"iot_dashboard_{self.broker_id}", 
                callback_api_version=CallbackAPIVersion.VERSION1
            )
            
            # Set username and password if provided
            if self.broker_config.get('username') and self.broker_config.get('password'):
                self.client.username_pw_set(
                    self.broker_config['username'], 
                    self.broker_config['password']
                )
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Connect to broker
            self.client.connect(
                self.broker_config['broker_host'], 
                self.broker_config['broker_port'], 
                60
            )
            
            # Start the loop in a separate thread
            self.client.loop_start()
            
            # Wait for connection
            await asyncio.sleep(2)
            
            # Update database connection status
            if self.is_connected:
                await self._update_broker_status(True, datetime.utcnow())
            
            return self.is_connected
            
        except Exception as e:
            print(f"MQTT connection error for broker {self.broker_id}: {e}")
            await self._update_broker_status(False, None)
            return False
    
    async def disconnect(self):
        """
        Disconnect from the MQTT broker.
        """
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            await self._update_broker_status(False, None)
    
    async def _update_broker_status(self, connected: bool, last_connected: Optional[datetime]):
        """
        Update broker connection status in database.
        """
        try:
            async with async_session_factory() as db:
                await db.execute(
                    update(MQTTBroker)
                    .where(MQTTBroker.id == self.broker_id)
                    .values(is_connected=connected, last_connected=last_connected)
                )
                await db.commit()
        except Exception as e:
            print(f"Error updating broker status: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for MQTT client connection.
        """
        if rc == 0:
            self.is_connected = True
            self.last_connected = datetime.utcnow()
            print(f"Connected to MQTT broker {self.broker_id} at {self.broker_config['broker_host']}:{self.broker_config['broker_port']}")
            
            # Subscribe to default topics
            self.client.subscribe("sensors/+/data")
            self.client.subscribe("devices/+/status")
        else:
            print(f"Failed to connect to MQTT broker {self.broker_id}, return code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        Callback for MQTT client disconnection.
        """
        self.is_connected = False
        print(f"Disconnected from MQTT broker {self.broker_id}, return code {rc}")
    
    def _on_message(self, client, userdata, msg: MQTTMessage):
        """
        Callback for received MQTT messages.
        """
        self.last_message = datetime.utcnow()
        
        # Schedule async message handling on the main event loop
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._handle_message_async(msg), 
                self.loop
            )
    
    async def _handle_message_async(self, msg: MQTTMessage):
        """
        Handle received MQTT message asynchronously.
        """
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Store message in database
            await self._store_message(topic, payload, msg.qos, msg.retain, "received")
            
            # Handle sensor data messages
            if topic.startswith("sensors/") and topic.endswith("/data"):
                await self._handle_sensor_data(topic, payload)
                
        except Exception as e:
            print(f"Error handling MQTT message for broker {self.broker_id}: {e}")
    
    async def _handle_sensor_data(self, topic: str, payload: str):
        """
        Handle sensor data messages and store in database.
        """
        try:
            # Parse sensor data from payload
            data = json.loads(payload)
            
            # Extract device ID from topic (sensors/{device_id}/data)
            device_id = topic.split('/')[1]
            
            # Find device in database
            async with async_session_factory() as db:
                result = await db.execute(
                    select(Device).where(Device.device_id == device_id)
                )
                device = result.scalar_one_or_none()
                
                if device:
                    # Store sensor data
                    sensor_data = SensorData(
                        user_id=device.user_id,
                        device_id=device_id,
                        device_table_id=device.id,
                        sensor_type=data.get('sensor_type', 'unknown'),
                        value=float(data.get('value', 0)),
                        unit=data.get('unit'),
                        location=data.get('location'),
                        metadata_json=json.dumps(data.get('metadata', {}))
                    )
                    
                    db.add(sensor_data)
                    
                    # Update device last seen
                    device.last_seen = datetime.utcnow()
                    await db.commit()
                else:
                    print(f"Device {device_id} not found in database")
                
        except Exception as e:
            print(f"Error handling sensor data for broker {self.broker_id}: {e}")
    
    async def _store_message(self, topic: str, payload: str, qos: int, retain: bool, message_type: str):
        """
        Store MQTT message in database.
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
            print(f"Error storing MQTT message for broker {self.broker_id}: {e}")
    
    async def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """
        Publish message to MQTT topic.
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
            print(f"Error publishing MQTT message for broker {self.broker_id}: {e}")
            return False
    
    async def subscribe(self, topic: str) -> bool:
        """
        Subscribe to MQTT topic.
        """
        if not self.is_connected or not self.client:
            return False
        
        try:
            result = self.client.subscribe(topic)
            return result[0] == 0
            
        except Exception as e:
            print(f"Error subscribing to MQTT topic for broker {self.broker_id}: {e}")
            return False
    
    async def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from MQTT topic.
        """
        if not self.is_connected or not self.client:
            return False
        
        try:
            result = self.client.unsubscribe(topic)
            return result[0] == 0
            
        except Exception as e:
            print(f"Error unsubscribing from MQTT topic for broker {self.broker_id}: {e}")
            return False


class EnhancedMQTTService:
    """
    Enhanced MQTT service for handling multiple MQTT broker connections.
    """
    
    def __init__(self):
        self.broker_connections: Dict[int, MQTTBrokerConnection] = {}
        self.is_initialized = False
    
    async def initialize(self):
        """
        Initialize the service by loading and connecting to all active brokers.
        """
        if self.is_initialized:
            return
        
        try:
            await self._load_and_connect_brokers()
            self.is_initialized = True
            print("Enhanced MQTT Service initialized successfully")
        except Exception as e:
            print(f"Error initializing MQTT service: {e}")
    
    async def _load_and_connect_brokers(self):
        """
        Load all active MQTT brokers from database and connect to them.
        """
        try:
            async with async_session_factory() as db:
                result = await db.execute(
                    select(MQTTBroker).where(MQTTBroker.is_active == True)
                )
                brokers = result.scalars().all()
                
                for broker in brokers:
                    broker_config = {
                        'broker_host': broker.broker_host,
                        'broker_port': broker.broker_port,
                        'username': broker.username,
                        'password': broker.password
                    }
                    
                    connection = MQTTBrokerConnection(broker.id, broker_config)
                    self.broker_connections[broker.id] = connection
                    
                    # Connect in background
                    asyncio.create_task(connection.connect())
                    
        except Exception as e:
            print(f"Error loading MQTT brokers: {e}")
    
    async def add_broker(self, broker_id: int, broker_config: Dict[str, Any]) -> bool:
        """
        Add a new MQTT broker connection.
        """
        try:
            connection = MQTTBrokerConnection(broker_id, broker_config)
            self.broker_connections[broker_id] = connection
            
            # Connect to the broker
            success = await connection.connect()
            
            if not success:
                # Remove connection if failed
                del self.broker_connections[broker_id]
            
            return success
            
        except Exception as e:
            print(f"Error adding MQTT broker {broker_id}: {e}")
            return False
    
    async def remove_broker(self, broker_id: int) -> bool:
        """
        Remove an MQTT broker connection.
        """
        try:
            if broker_id in self.broker_connections:
                await self.broker_connections[broker_id].disconnect()
                del self.broker_connections[broker_id]
                return True
            return False
            
        except Exception as e:
            print(f"Error removing MQTT broker {broker_id}: {e}")
            return False
    
    async def connect_broker(self, broker_id: int) -> bool:
        """
        Connect to a specific MQTT broker.
        """
        try:
            if broker_id in self.broker_connections:
                return await self.broker_connections[broker_id].connect()
            
            # Load broker config from database
            async with async_session_factory() as db:
                result = await db.execute(
                    select(MQTTBroker).where(MQTTBroker.id == broker_id, MQTTBroker.is_active == True)
                )
                broker = result.scalar_one_or_none()
                
                if broker:
                    broker_config = {
                        'broker_host': broker.broker_host,
                        'broker_port': broker.broker_port,
                        'username': broker.username,
                        'password': broker.password
                    }
                    
                    return await self.add_broker(broker_id, broker_config)
                    
            return False
            
        except Exception as e:
            print(f"Error connecting to MQTT broker {broker_id}: {e}")
            return False
    
    async def disconnect_broker(self, broker_id: int) -> bool:
        """
        Disconnect from a specific MQTT broker.
        """
        try:
            if broker_id in self.broker_connections:
                await self.broker_connections[broker_id].disconnect()
                return True
            return False
            
        except Exception as e:
            print(f"Error disconnecting from MQTT broker {broker_id}: {e}")
            return False
    
    async def publish_to_broker(self, broker_id: int, topic: str, payload: str, qos: int = 0, retain: bool = False) -> bool:
        """
        Publish message to a specific MQTT broker.
        """
        try:
            if broker_id in self.broker_connections:
                return await self.broker_connections[broker_id].publish(topic, payload, qos, retain)
            return False
            
        except Exception as e:
            print(f"Error publishing to MQTT broker {broker_id}: {e}")
            return False
    
    async def get_broker_status(self, broker_id: int) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific MQTT broker.
        """
        try:
            if broker_id in self.broker_connections:
                connection = self.broker_connections[broker_id]
                return {
                    "broker_id": broker_id,
                    "connected": connection.is_connected,
                    "last_connected": connection.last_connected,
                    "last_message": connection.last_message,
                    "broker_host": connection.broker_config['broker_host'],
                    "broker_port": connection.broker_config['broker_port']
                }
            return None
            
        except Exception as e:
            print(f"Error getting broker status {broker_id}: {e}")
            return None
    
    async def get_all_brokers_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all MQTT brokers.
        """
        try:
            statuses = []
            async with async_session_factory() as db:
                result = await db.execute(select(MQTTBroker))
                brokers = result.scalars().all()
                
                for broker in brokers:
                    status = {
                        "broker_id": broker.id,
                        "broker_name": broker.broker_name,
                        "broker_host": broker.broker_host,
                        "broker_port": broker.broker_port,
                        "is_active": broker.is_active,
                        "connected": False,
                        "last_connected": broker.last_connected,
                        "last_message": None
                    }
                    
                    # Check if connection exists and is active
                    if broker.id in self.broker_connections:
                        connection = self.broker_connections[broker.id]
                        status["connected"] = connection.is_connected
                        status["last_message"] = connection.last_message
                    
                    statuses.append(status)
                
                return statuses
            
        except Exception as e:
            print(f"Error getting all brokers status: {e}")
            return []
    
    async def shutdown(self):
        """
        Shutdown all MQTT connections.
        """
        try:
            for broker_id in list(self.broker_connections.keys()):
                await self.disconnect_broker(broker_id)
            
            self.broker_connections.clear()
            self.is_initialized = False
            print("Enhanced MQTT Service shutdown completed")
            
        except Exception as e:
            print(f"Error shutting down MQTT service: {e}")


# Global instance
enhanced_mqtt_service = EnhancedMQTTService()
