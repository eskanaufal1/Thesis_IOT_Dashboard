"""
Authentication schemas for the IoT Dashboard API.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    company: Optional[str] = Field(None, max_length=100, description="Company")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    bio: Optional[str] = Field(None, max_length=500, description="Bio")
    role: Optional[str] = Field(default="user", description="User role")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class TokenData(BaseModel):
    username: Optional[str] = None
