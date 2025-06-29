"""
Refactored MQTT Service with modern patterns and better maintainability.
Uses library-based patterns, async context managers, and clean separation of concerns.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from functools import wraps
import os

from aiomqtt import Client, MqttError
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.database import SessionLocal
from models.database import Device, TelemetryData, RelayState, SystemLog
from models.schemas import DeviceStatus, LogLevel

logger = logging.getLogger(__name__)


@dataclass
class MQTTConfig:
    """Configuration for MQTT service"""
    broker_host: str = field(default_factory=lambda: os.getenv("MQTT_BROKER_HOST", "localhost"))
    broker_port: int = field(default_factory=lambda: int(os.getenv("MQTT_BROKER_PORT", "1883")))
    username: Optional[str] = field(default_factory=lambda: os.getenv("MQTT_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("MQTT_PASSWORD"))
    client_id: str = field(default_factory=lambda: os.getenv("MQTT_CLIENT_ID", "iot_dashboard_backend"))
    connection_timeout: float = 5.0
    
    # Topic configuration
    topic_prefix: str = field(default_factory=lambda: os.getenv("MQTT_TOPIC_PREFIX", "iot/devices"))
    topic_telemetry: str = field(default_factory=lambda: os.getenv("MQTT_TOPIC_TELEMETRY", "telemetry"))
    topic_control: str = field(default_factory=lambda: os.getenv("MQTT_TOPIC_CONTROL", "control"))
    topic_status: str = field(default_factory=lambda: os.getenv("MQTT_TOPIC_STATUS", "status"))


class MQTTMessage(BaseModel):
    """Structured MQTT message"""
    topic: str
    device_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MQTTMessageHandler:
    """Base class for MQTT message handlers"""
    
    def __init__(self, db_session_factory: Callable[[], Session], socketio_manager=None):
        self.db_session_factory = db_session_factory
        self.socketio_manager = socketio_manager
    
    @asynccontextmanager
    async def get_db_session(self):
        """Async context manager for database sessions"""
        session = self.db_session_factory()
        try:
            yield session
        finally:
            session.close()
    
    async def handle_message(self, message: MQTTMessage) -> None:
        """Handle an MQTT message - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def broadcast_to_websocket(self, event: str, data: Dict[str, Any]) -> None:
        """Broadcast message to WebSocket clients"""
        if self.socketio_manager:
            await self.socketio_manager.broadcast_message(event, data)


class TelemetryHandler(MQTTMessageHandler):
    """Handler for telemetry messages"""
    
    async def handle_message(self, message: MQTTMessage) -> None:
        """Handle telemetry data from devices"""
        try:
            async with self.get_db_session() as db:
                # Update device status
                device = db.query(Device).filter(Device.device_id == message.device_id).first()
                if device:
                    device.status = DeviceStatus.ONLINE
                    device.last_seen = datetime.utcnow()
                    db.commit()
                
                # Store telemetry data
                telemetry_data = TelemetryData(
                    device_id=message.device_id,
                    voltage=message.payload.get("voltage"),
                    current=message.payload.get("current"),
                    power=message.payload.get("power"),
                    temperature=message.payload.get("temperature"),
                    humidity=message.payload.get("humidity"),
                    additional_data=json.dumps(message.payload.get("additional", {}))
                )
                db.add(telemetry_data)
                db.commit()
                
                # Broadcast to WebSocket clients
                await self.broadcast_to_websocket("telemetry_update", {
                    "device_id": message.device_id,
                    "data": message.payload,
                    "timestamp": message.timestamp.isoformat()
                })
                
                logger.info(f"Processed telemetry data for device {message.device_id}")
                
        except Exception as e:
            logger.error(f"Error handling telemetry message: {e}")


class StatusHandler(MQTTMessageHandler):
    """Handler for device status messages"""
    
    async def handle_message(self, message: MQTTMessage) -> None:
        """Handle device status messages"""
        try:
            async with self.get_db_session() as db:
                device = db.query(Device).filter(Device.device_id == message.device_id).first()
                if device:
                    device.status = message.payload.get("status", DeviceStatus.ONLINE)
                    device.last_seen = datetime.utcnow()
                    
                    # Update relay states if provided
                    relay_states = message.payload.get("relays", {})
                    for relay_num, state in relay_states.items():
                        relay_state = RelayState(
                            device_id=message.device_id,
                            relay_number=int(relay_num),
                            state=bool(state),
                            updated_by="device"
                        )
                        db.add(relay_state)
                    
                    db.commit()
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_to_websocket("status_update", {
                        "device_id": message.device_id,
                        "status": message.payload,
                        "timestamp": message.timestamp.isoformat()
                    })
                    
        except Exception as e:
            logger.error(f"Error handling status message: {e}")


class ControlResponseHandler(MQTTMessageHandler):
    """Handler for control command responses"""
    
    async def handle_message(self, message: MQTTMessage) -> None:
        """Handle control command responses from devices"""
        try:
            logger.info(f"Received control response from {message.device_id}: {message.payload}")
            
            # Broadcast to WebSocket clients
            await self.broadcast_to_websocket("control_response", {
                "device_id": message.device_id,
                "response": message.payload,
                "timestamp": message.timestamp.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling control response: {e}")


def connection_required(func):
    """Decorator to ensure MQTT connection is available"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.is_connected():
            logger.warning(f"MQTT client not connected for {func.__name__}")
            return False
        return await func(self, *args, **kwargs)
    return wrapper


class MQTTService:
    """
    Modern MQTT service with clean separation of concerns and library-based patterns.
    """
    
    def __init__(self, config: Optional[MQTTConfig] = None, socketio_manager=None):
        self.config = config or MQTTConfig()
        self.socketio_manager = socketio_manager
        self.client: Optional[Client] = None
        self._connected = False
        self._message_handlers: Dict[str, MQTTMessageHandler] = {}
        self._background_tasks: List[asyncio.Task] = []
        
        # Initialize message handlers
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup message handlers for different topics"""
        self._message_handlers = {
            "telemetry": TelemetryHandler(SessionLocal, self.socketio_manager),
            "status": StatusHandler(SessionLocal, self.socketio_manager),
            "control/response": ControlResponseHandler(SessionLocal, self.socketio_manager),
        }
    
    @asynccontextmanager
    async def mqtt_client(self):
        """Async context manager for MQTT client"""
        client = Client(
            hostname=self.config.broker_host,
            port=self.config.broker_port,
            username=self.config.username,
            password=self.config.password,
            identifier=self.config.client_id,
        )
        
        try:
            await asyncio.wait_for(client.__aenter__(), timeout=self.config.connection_timeout)
            yield client
        except asyncio.TimeoutError:
            logger.warning(f"MQTT connection timeout - broker may not be available at {self.config.broker_host}:{self.config.broker_port}")
            raise
        except MqttError as e:
            logger.error(f"MQTT connection error: {e}")
            raise
        finally:
            try:
                await client.__aexit__(None, None, None)
            except:
                pass  # Ignore cleanup errors
    
    async def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = Client(
                hostname=self.config.broker_host,
                port=self.config.broker_port,
                username=self.config.username,
                password=self.config.password,
                identifier=self.config.client_id,
            )
            
            await asyncio.wait_for(self.client.__aenter__(), timeout=self.config.connection_timeout)
            self._connected = True
            
            # Subscribe to topics
            await self._subscribe_to_topics()
            
            logger.info(f"Connected to MQTT broker at {self.config.broker_host}:{self.config.broker_port}")
            await self._log_system_event(LogLevel.INFO, "MQTT", "Connected to MQTT broker")
            return True
            
        except asyncio.TimeoutError:
            logger.warning(f"MQTT connection timeout - broker may not be available")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        if self.client and self._connected:
            try:
                await self.client.__aexit__(None, None, None)
                self._connected = False
                logger.info("Disconnected from MQTT broker")
                await self._log_system_event(LogLevel.INFO, "MQTT", "Disconnected from MQTT broker")
            except Exception as e:
                logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    async def _subscribe_to_topics(self) -> None:
        """Subscribe to all relevant MQTT topics"""
        if not self.client:
            return
        
        topics = [
            f"{self.config.topic_prefix}/+/{self.config.topic_telemetry}",
            f"{self.config.topic_prefix}/+/{self.config.topic_status}",
            f"{self.config.topic_prefix}/+/{self.config.topic_control}/response",
        ]
        
        for topic in topics:
            await self.client.subscribe(topic)
            logger.info(f"Subscribed to topic: {topic}")
    
    def _parse_message(self, message) -> Optional[MQTTMessage]:
        """Parse incoming MQTT message into structured format"""
        try:
            topic = message.topic.value
            payload = json.loads(message.payload.decode())
            
            # Extract device ID and message type from topic
            topic_parts = topic.split("/")
            if len(topic_parts) >= 3:
                device_id = topic_parts[2]
                message_type = "/".join(topic_parts[3:])
                
                return MQTTMessage(
                    topic=topic,
                    device_id=device_id,
                    message_type=message_type,
                    payload=payload
                )
        except Exception as e:
            logger.error(f"Error parsing MQTT message: {e}")
        
        return None
    
    async def _process_message(self, message) -> None:
        """Process incoming MQTT message"""
        try:
            parsed_message = self._parse_message(message)
            if not parsed_message:
                return
            
            # Handle the message based on type
            handler = self._message_handlers.get(parsed_message.message_type)
            if handler:
                await handler.handle_message(parsed_message)
            else:
                logger.warning(f"No handler for message type: {parsed_message.message_type}")
            
            # Broadcast raw message to WebSocket clients
            if self.socketio_manager:
                await self.socketio_manager.broadcast_message("mqtt_message", {
                    "topic": parsed_message.topic,
                    "payload": parsed_message.payload,
                    "timestamp": parsed_message.timestamp.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    async def listen_for_messages(self) -> None:
        """Listen for incoming MQTT messages"""
        if not self.client or not self._connected:
            logger.warning("MQTT client not connected")
            return
        
        try:
            async for message in self.client.messages:
                await self._process_message(message)
        except Exception as e:
            logger.error(f"Error listening for MQTT messages: {e}")
            self._connected = False
    
    @connection_required
    async def publish_message(self, device_id: str, message_type: str, payload: Dict[str, Any]) -> bool:
        """Generic method to publish messages to devices"""
        try:
            topic = f"{self.config.topic_prefix}/{device_id}/{message_type}"
            message = json.dumps(payload)
            
            await self.client.publish(topic, message)
            logger.info(f"Published {message_type} to {device_id}: {payload}")
            
            await self._log_system_event(LogLevel.INFO, "MQTT", f"Published {message_type} to {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            await self._log_system_event(LogLevel.ERROR, "MQTT", f"Error publishing message: {e}")
            return False
    
    async def send_control_command(self, device_id: str, command: Dict[str, Any]) -> bool:
        """Send control command to device"""
        command_with_timestamp = {
            **command,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.publish_message(device_id, self.config.topic_control, command_with_timestamp)
    
    async def send_relay_command(self, device_id: str, relay_number: int, state: bool) -> bool:
        """Send relay control command to device"""
        command = {
            "type": "relay_control",
            "relay": relay_number,
            "state": state,
            "command_id": f"relay_{relay_number}_{int(state)}_{int(datetime.utcnow().timestamp())}"
        }
        return await self.send_control_command(device_id, command)
    
    async def request_device_status(self, device_id: str) -> bool:
        """Request device status update"""
        command = {
            "type": "status_request"
        }
        return await self.send_control_command(device_id, command)
    
    async def _log_system_event(self, level: LogLevel, module: str, message: str, device_id: Optional[str] = None) -> None:
        """Log system events to database"""
        try:
            db = SessionLocal()
            try:
                log_entry = SystemLog(
                    level=level.value,
                    message=message,
                    module=module,
                    device_id=device_id
                )
                db.add(log_entry)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.debug(f"Could not log to database: {e}")
    
    async def start(self) -> None:
        """Start the MQTT service"""
        try:
            logger.info("Starting MQTT service...")
            connected = await self.connect()
            
            if connected:
                # Start listening in background
                listen_task = asyncio.create_task(self.listen_for_messages())
                self._background_tasks.append(listen_task)
                logger.info("MQTT service started successfully")
            else:
                logger.warning("MQTT service started but not connected to broker")
                
        except Exception as e:
            logger.error(f"Error starting MQTT service: {e}")
    
    async def stop(self) -> None:
        """Stop the MQTT service"""
        try:
            # Cancel background tasks
            for task in self._background_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            # Disconnect from broker
            await self.disconnect()
            
            logger.info("MQTT service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping MQTT service: {e}")
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self._connected
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status"""
        return {
            "connected": self._connected,
            "broker_host": self.config.broker_host,
            "broker_port": self.config.broker_port,
            "client_id": self.config.client_id,
            "background_tasks": len(self._background_tasks)
        }
