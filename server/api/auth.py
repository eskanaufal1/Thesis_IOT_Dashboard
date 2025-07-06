"""
Authentication API routes for the IoT Dashboard.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.database import get_db
from models.auth_schemas import LoginRequest, LoginResponse, UserCreate, UserResponse, PasswordChangeRequest
from models.user import User
from services.security_service import SecurityService
from services.auth_service import (
    authenticate_user, 
    create_access_token, 
    verify_token, 
    get_user_by_username,
    create_user,
    create_demo_user,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    
    # Ensure demo user exists
    try:
        create_demo_user(db)
    except Exception as e:
        # User might already exist, continue
        pass
    
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        company=user.company,
        location=user.location,
        bio=user.bio,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else ""
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    
    # Check if user already exists
    if get_user_by_username(db, user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user = create_user(db, user_create)
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        company=user.company,
        location=user.location,
        bio=user.bio,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else ""
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        company=current_user.company,
        location=current_user.location,
        bio=current_user.bio,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    
    # Sanitize and validate input
    try:
        # Only allow specific fields to be updated
        allowed_fields = ["email", "full_name", "phone", "company", "location", "bio"]
        clean_data = SecurityService.sanitize_dict(user_update, allowed_fields)
        
        # Additional validation for email if provided
        if "email" in clean_data:
            # Use the user validation function to validate email format
            temp_data = {"email": clean_data["email"]}
            SecurityService.validate_user_input(temp_data)
        
        # Update allowed fields
        for field in allowed_fields:
            if field in clean_data:
                setattr(current_user, field, clean_data[field])
        
        # Use safe query execution
        def update_user_transaction(db_session, user_obj):
            db_session.commit()
            db_session.refresh(user_obj)
            return user_obj
        
        updated_user = SecurityService.safe_query_execution(
            db,
            update_user_transaction,
            current_user
        )
        
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            full_name=updated_user.full_name,
            phone=updated_user.phone,
            company=updated_user.company,
            location=updated_user.location,
            bio=updated_user.bio,
            role=updated_user.role,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at.isoformat() if updated_user.created_at else ""
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.post("/change-password")
async def change_password(
    password_change: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password using safe query execution
    def update_password_transaction(db_session, user_obj, new_hash):
        user_obj.hashed_password = new_hash
        db_session.commit()
        return user_obj
    
    new_password_hash = get_password_hash(password_change.new_password)
    SecurityService.safe_query_execution(
        db,
        update_password_transaction,
        current_user,
        new_password_hash
    )
    
    return {"message": "Password updated successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (token blacklisting would be implemented here in production)."""
    return {"message": "Successfully logged out"}
