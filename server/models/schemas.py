from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CommandStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


# Device Models
class DeviceBase(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Human-readable device name")
    location: Optional[str] = Field(None, description="Device location")
    device_type: str = Field(default="IoT Device", description="Type of device")


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[DeviceStatus] = None


class DeviceResponse(DeviceBase):
    id: int
    status: DeviceStatus
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Telemetry Models
class TelemetryDataBase(BaseModel):
    device_id: str
    voltage: Optional[float] = None
    current: Optional[float] = None
    power: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None


class TelemetryDataCreate(TelemetryDataBase):
    pass


class TelemetryDataResponse(TelemetryDataBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Relay Models
class RelayStateBase(BaseModel):
    device_id: str
    relay_number: int = Field(..., ge=1, le=4, description="Relay number (1-4)")
    state: bool = Field(..., description="Relay state (True=ON, False=OFF)")


class RelayStateCreate(RelayStateBase):
    updated_by: str = "user"


class RelayStateResponse(RelayStateBase):
    id: int
    timestamp: datetime
    updated_by: str

    class Config:
        from_attributes = True


class RelayControlRequest(BaseModel):
    relay_number: int = Field(..., ge=1, le=4)
    state: bool
    device_id: str


class RelayBulkControlRequest(BaseModel):
    device_id: str
    relays: Dict[int, bool] = Field(..., description="Dictionary of relay_number: state")


# Command Models
class DeviceCommandBase(BaseModel):
    device_id: str
    command_type: str
    command_data: Optional[Dict[str, Any]] = None


class DeviceCommandCreate(DeviceCommandBase):
    pass


class DeviceCommandResponse(DeviceCommandBase):
    id: int
    status: CommandStatus
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# System Log Models
class SystemLogCreate(BaseModel):
    level: LogLevel
    message: str
    module: Optional[str] = None
    device_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class SystemLogResponse(SystemLogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Dashboard Models
class DashboardStats(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    maintenance_devices: int
    total_telemetry_records: int
    latest_telemetry: Optional[datetime] = None


class DeviceWithLatestData(BaseModel):
    device: DeviceResponse
    latest_telemetry: Optional[TelemetryDataResponse] = None
    relay_states: List[RelayStateResponse] = []


# WebSocket Models
class SocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MQTTMessage(BaseModel):
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
