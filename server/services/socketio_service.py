import socketio
import asyncio
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SocketIOManager:
    def __init__(self):
        # CORS settings
        cors_origins = os.getenv("SOCKETIO_CORS_ALLOWED_ORIGINS", "http://localhost:5173")
        if isinstance(cors_origins, str):
            cors_origins = cors_origins.split(",")
        
        # Create Socket.IO server
        self.sio = socketio.AsyncServer(
            cors_allowed_origins=cors_origins,
            logger=True,
            engineio_logger=True
        )
        
        # Store connected clients
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        
        # Setup event handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection"""
            try:
                logger.info(f"Client {sid} connected")
                self.connected_clients[sid] = {
                    "connected_at": asyncio.get_event_loop().time(),
                    "subscriptions": set()
                }
                
                # Send connection acknowledgment
                await self.sio.emit("connection_ack", {
                    "status": "connected",
                    "sid": sid,
                    "server_time": asyncio.get_event_loop().time()
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Error handling client connection: {e}")

        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            try:
                logger.info(f"Client {sid} disconnected")
                if sid in self.connected_clients:
                    del self.connected_clients[sid]
            except Exception as e:
                logger.error(f"Error handling client disconnection: {e}")

        @self.sio.event
        async def subscribe_device(sid, data):
            """Handle device subscription"""
            try:
                device_id = data.get("device_id")
                if device_id and sid in self.connected_clients:
                    self.connected_clients[sid]["subscriptions"].add(device_id)
                    await self.sio.emit("subscription_ack", {
                        "device_id": device_id,
                        "status": "subscribed"
                    }, room=sid)
                    logger.info(f"Client {sid} subscribed to device {device_id}")
            except Exception as e:
                logger.error(f"Error handling device subscription: {e}")

        @self.sio.event
        async def unsubscribe_device(sid, data):
            """Handle device unsubscription"""
            try:
                device_id = data.get("device_id")
                if device_id and sid in self.connected_clients:
                    self.connected_clients[sid]["subscriptions"].discard(device_id)
                    await self.sio.emit("unsubscription_ack", {
                        "device_id": device_id,
                        "status": "unsubscribed"
                    }, room=sid)
                    logger.info(f"Client {sid} unsubscribed from device {device_id}")
            except Exception as e:
                logger.error(f"Error handling device unsubscription: {e}")

        @self.sio.event
        async def relay_control(sid, data):
            """Handle relay control from client"""
            try:
                device_id = data.get("device_id")
                relay_number = data.get("relay_number")
                state = data.get("state")
                
                if device_id and relay_number is not None and state is not None:
                    # Broadcast relay control to all clients and MQTT
                    await self.broadcast_message("relay_control_request", {
                        "device_id": device_id,
                        "relay_number": relay_number,
                        "state": state,
                        "requested_by": sid
                    })
                    
                    logger.info(f"Relay control request from {sid}: Device {device_id}, Relay {relay_number}, State {state}")
                    
            except Exception as e:
                logger.error(f"Error handling relay control: {e}")

        @self.sio.event
        async def device_status_request(sid, data):
            """Handle device status request"""
            try:
                device_id = data.get("device_id")
                if device_id:
                    await self.broadcast_message("device_status_request", {
                        "device_id": device_id,
                        "requested_by": sid
                    })
                    logger.info(f"Device status request from {sid}: Device {device_id}")
            except Exception as e:
                logger.error(f"Error handling device status request: {e}")

        @self.sio.event
        async def get_dashboard_data(sid, data):
            """Handle dashboard data request"""
            try:
                # This would typically fetch data from database
                # For now, we'll emit a request for fresh data
                await self.broadcast_message("dashboard_data_request", {
                    "requested_by": sid
                })
                logger.info(f"Dashboard data request from {sid}")
            except Exception as e:
                logger.error(f"Error handling dashboard data request: {e}")

    async def broadcast_message(self, event: str, data: Dict[str, Any], room: Optional[str] = None):
        """Broadcast message to all connected clients or specific room"""
        try:
            if room:
                await self.sio.emit(event, data, room=room)
            else:
                await self.sio.emit(event, data)
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    async def send_to_device_subscribers(self, device_id: str, event: str, data: Dict[str, Any]):
        """Send message to clients subscribed to a specific device"""
        try:
            for sid, client_info in self.connected_clients.items():
                if device_id in client_info.get("subscriptions", set()):
                    await self.sio.emit(event, data, room=sid)
        except Exception as e:
            logger.error(f"Error sending to device subscribers: {e}")

    async def send_telemetry_update(self, device_id: str, telemetry_data: Dict[str, Any]):
        """Send telemetry update to subscribed clients"""
        await self.send_to_device_subscribers(device_id, "telemetry_update", {
            "device_id": device_id,
            "data": telemetry_data
        })

    async def send_device_status_update(self, device_id: str, status_data: Dict[str, Any]):
        """Send device status update to subscribed clients"""
        await self.send_to_device_subscribers(device_id, "device_status_update", {
            "device_id": device_id,
            "status": status_data
        })

    async def send_relay_state_update(self, device_id: str, relay_data: Dict[str, Any]):
        """Send relay state update to subscribed clients"""
        await self.send_to_device_subscribers(device_id, "relay_state_update", {
            "device_id": device_id,
            "relay_data": relay_data
        })

    async def send_dashboard_stats(self, stats: Dict[str, Any]):
        """Send dashboard statistics to all clients"""
        await self.broadcast_message("dashboard_stats", stats)

    async def send_system_notification(self, notification: Dict[str, Any]):
        """Send system notification to all clients"""
        await self.broadcast_message("system_notification", notification)

    def get_connected_clients_count(self) -> int:
        """Get number of connected clients"""
        return len(self.connected_clients)

    def get_client_info(self, sid: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific client"""
        return self.connected_clients.get(sid)

    async def disconnect_client(self, sid: str, reason: str = "Server initiated"):
        """Disconnect a specific client"""
        try:
            await self.sio.disconnect(sid)
            logger.info(f"Disconnected client {sid}: {reason}")
        except Exception as e:
            logger.error(f"Error disconnecting client {sid}: {e}")

    def create_asgi_app(self, app):
        """Create ASGI app with Socket.IO"""
        return socketio.ASGIApp(self.sio, app)

    # Additional methods for compatibility with main.py
    async def start(self):
        """Start the Socket.IO service"""
        self.is_running_flag = True
        logger.info("Socket.IO service started")

    async def stop(self):
        """Stop the Socket.IO service"""
        self.is_running_flag = False
        # Disconnect all clients
        for sid in list(self.connected_clients.keys()):
            await self.disconnect_client(sid, "Server shutdown")
        logger.info("Socket.IO service stopped")

    def is_running(self) -> bool:
        """Check if Socket.IO service is running"""
        return getattr(self, 'is_running_flag', False)


# Global instances for easy import
socketio_manager = SocketIOManager()
sio = socketio_manager.sio
sio_app = socketio.ASGIApp(sio)

# Alias for backward compatibility
SocketIOService = SocketIOManager
