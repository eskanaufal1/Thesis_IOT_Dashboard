"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re


# User Models
class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    company: Optional[str] = Field(None, max_length=100, description="Company")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    bio: Optional[str] = Field(None, max_length=500, description="Biography")


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8, description="Password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """User login model."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """User response model."""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change model."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


# Authentication Models
class Token(BaseModel):
    """JWT token model."""
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None


# Sensor Data Models
class SensorDataBase(BaseModel):
    """Base sensor data model."""
    device_id: str = Field(..., max_length=100, description="Device ID")
    sensor_type: str = Field(..., max_length=50, description="Sensor type")
    value: float = Field(..., description="Sensor value")
    unit: Optional[str] = Field(None, max_length=20, description="Unit of measurement")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    metadata_json: Optional[str] = Field(None, description="Additional metadata as JSON")


class SensorDataCreate(SensorDataBase):
    """Sensor data creation model."""
    pass


class SensorDataResponse(SensorDataBase):
    """Sensor data response model."""
    id: int
    user_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# MQTT Models
class MQTTPublish(BaseModel):
    """MQTT publish message model."""
    topic: str = Field(..., max_length=200, description="MQTT topic")
    payload: str = Field(..., description="Message payload")
    qos: int = Field(0, ge=0, le=2, description="Quality of Service level")
    retain: bool = Field(False, description="Retain message")


class MQTTMessageResponse(BaseModel):
    """MQTT message response model."""
    id: int
    topic: str
    payload: str
    qos: int
    retain: bool
    timestamp: datetime
    message_type: str
    
    class Config:
        from_attributes = True


class MQTTStatus(BaseModel):
    """MQTT connection status model."""
    connected: bool
    broker_host: str
    broker_port: int
    last_connected: Optional[datetime] = None
    last_message: Optional[datetime] = None


# Generic Response Models
class MessageResponse(BaseModel):
    """Generic message response model."""
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


# Pagination Models
class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int
