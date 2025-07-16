"""
Authentication router for user registration, login, and profile management.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db, User
from app.models import (
    UserCreate, UserLogin, UserResponse, UserUpdate, 
    Token, PasswordChange, MessageResponse
)
from app.services.auth_service import (
    AuthService, get_current_active_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES, security
)

# Create router
router = APIRouter()

# Initialize auth service
auth_service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_create: User creation data
        db: Database session
        
    Returns:
        UserResponse: Created user information
    """
    try:
        user = await auth_service.create_user(db, user_create)
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user and return JWT token.
    
    Args:
        user_login: User login credentials
        db: Database session
        
    Returns:
        Token: JWT token and user information
    """
    # Authenticate user
    user = await auth_service.authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User profile information
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile.
    
    Args:
        user_update: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user information
    """
    try:
        # Update user fields
        update_data = user_update.dict(exclude_unset=True)
        if update_data:
            await db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(**update_data)
            )
            await db.commit()
            
            # Refresh user data
            await db.refresh(current_user)
        
        return UserResponse.model_validate(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.
    
    Args:
        password_change: Password change data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Success message
    """
    # Verify current password
    if not auth_service.verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    try:
        # Update password
        new_hashed_password = auth_service.get_password_hash(password_change.new_password)
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(hashed_password=new_hashed_password)
        )
        await db.commit()
        
        return MessageResponse(message="Password changed successfully")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )


@router.get("/verify-token", response_model=UserResponse)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify JWT token and return user information.
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        UserResponse: User information if token is valid
    """
    from app.services.auth_service import get_current_user
    
    user = await get_current_user(credentials, db)
    return UserResponse.model_validate(user)


@router.get("/users", response_model=list[UserResponse])
async def get_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users (admin only).
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        list[UserResponse]: List of all users
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    return [UserResponse.model_validate(user) for user in users]
