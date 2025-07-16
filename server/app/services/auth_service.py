"""
Authentication service for JWT token management and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import hashlib
import secrets

from app.database import get_db, User
from app.models import UserCreate, UserResponse, TokenData

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthService:
    """
    Authentication service for handling user registration, login, and token management.
    """
    
    def __init__(self):
        pass
    
    def _hash_password_with_salt(self, password: str, salt: str = None) -> str:
        """
        Hash password with salt using SHA-256.
        
        Args:
            password: The plain text password
            salt: Optional salt, if not provided, generates one
            
        Returns:
            str: The hashed password with salt
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine password and salt
        password_salt = f"{password}{salt}"
        
        # Hash multiple times for security
        hashed = password_salt
        for _ in range(10000):  # 10,000 iterations
            hashed = hashlib.sha256(hashed.encode()).hexdigest()
        
        return f"{salt}:{hashed}"
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        
        Args:
            plain_password: The plain text password
            hashed_password: The hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            salt, stored_hash = hashed_password.split(':', 1)
            return self._hash_password_with_salt(plain_password, salt) == hashed_password
        except (ValueError, IndexError):
            return False
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain password.
        
        Args:
            password: The plain text password
            
        Returns:
            str: The hashed password
        """
        return self._hash_password_with_salt(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: The data to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            str: The encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        Get user by username from database.
        
        Args:
            db: Database session
            username: The username to search for
            
        Returns:
            Optional[User]: The user object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email from database.
        
        Args:
            db: Database session
            email: The email to search for
            
        Returns:
            Optional[User]: The user object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def authenticate_user(self, db: AsyncSession, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            db: Database session
            username: The username
            password: The plain text password
            
        Returns:
            Optional[User]: The user object if authenticated, None otherwise
        """
        user = await self.get_user_by_username(db, username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def create_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        """
        Create a new user in the database.
        
        Args:
            db: Database session
            user_create: User creation data
            
        Returns:
            User: The created user object
        """
        # Check if user already exists
        existing_user = await self.get_user_by_username(db, user_create.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        existing_email = await self.get_user_by_email(db, user_create.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = self.get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            phone=user_create.phone,
            company=user_create.company,
            location=user_create.location,
            bio=user_create.bio
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    async def create_default_admin(self):
        """
        Create a default admin user if no users exist.
        """
        from app.database import async_session_factory
        
        async with async_session_factory() as db:
            # Check if any users exist
            result = await db.execute(select(User))
            existing_users = result.scalars().all()
            
            if not existing_users:
                # Create default admin user
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=self.get_password_hash("admin123"),
                    full_name="Administrator",
                    role="admin",
                    is_active=True
                )
                
                db.add(admin_user)
                await db.commit()
                print("Default admin user created: admin/admin123")


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    auth_service = AuthService()
    user = await auth_service.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
