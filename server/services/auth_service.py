"""
Authentication service for the IoT Dashboard.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.user import User
from models.auth_schemas import UserCreate, TokenData
from services.security_service import SecurityService, sanitize_inputs

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        return None


@sanitize_inputs()
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username with input sanitization."""
    # Additional validation for username
    clean_username = SecurityService.sanitize_string(username, max_length=50)
    if not clean_username:
        return None
    
    return SecurityService.safe_query_execution(
        db, 
        lambda db, uname: db.query(User).filter(User.username == uname).first(),
        clean_username
    )


@sanitize_inputs()
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email with input sanitization."""
    # Additional validation for email
    clean_email = SecurityService.sanitize_string(email, max_length=255).lower()
    if not clean_email or '@' not in clean_email:
        return None
    
    return SecurityService.safe_query_execution(
        db,
        lambda db, email_addr: db.query(User).filter(User.email == email_addr).first(),
        clean_email
    )


@sanitize_inputs()
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with input sanitization."""
    # Sanitize username input
    clean_username = SecurityService.sanitize_string(username, max_length=50)
    if not clean_username:
        return None
    
    user = get_user_by_username(db, clean_username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with input validation and sanitization."""
    # Convert Pydantic model to dict for sanitization
    user_data = user.model_dump()
    
    # Validate and sanitize user input
    try:
        clean_data = SecurityService.validate_user_input(user_data)
    except ValueError as e:
        raise ValueError(f"Invalid user data: {str(e)}")
    
    # Check if user already exists
    existing_user = get_user_by_username(db, clean_data['username'])
    if existing_user:
        raise ValueError("Username already exists")
    
    existing_email = get_user_by_email(db, clean_data['email'])
    if existing_email:
        raise ValueError("Email already exists")
    
    # Hash password
    hashed_password = get_password_hash(user_data['password'])  # Use original password for hashing
    
    # Create user with sanitized data
    db_user = User(
        username=clean_data['username'],
        email=clean_data['email'],
        hashed_password=hashed_password,
        full_name=clean_data.get('full_name'),
        phone=clean_data.get('phone'),
        company=clean_data.get('company'),
        location=clean_data.get('location'),
        bio=clean_data.get('bio'),
        role=clean_data.get('role', 'user')
    )
    
    return SecurityService.safe_query_execution(
        db,
        lambda db, user_obj: _create_user_transaction(db, user_obj),
        db_user
    )


def _create_user_transaction(db: Session, db_user: User) -> User:
    """Internal function to handle user creation transaction."""
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_demo_user(db: Session) -> User:
    """Create the demo user if it doesn't exist."""
    existing_user = get_user_by_username(db, "jelly")
    if existing_user:
        return existing_user
    
    demo_user = UserCreate(
        username="jelly",
        email="jelly@iotdashboard.com",
        password="Jelly123#",
        full_name="Jelly User",
        phone="+1 (555) 123-4567",
        company="IoT Solutions Inc.",
        location="San Francisco, CA",
        bio="IoT Dashboard Administrator",
        role="admin"
    )
    
    return create_user(db, demo_user)
