"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth.models import UserCreate, UserResponse, UserLogin, Token, UserUpdate
from auth.database import (
    create_user, get_user_by_username, get_all_users, 
    update_user, delete_user, get_user_by_id
)
from auth.utils import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_admin)
):
    """Register a new user (admin only)"""
    try:
        user_id = await create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        user = await get_user_by_id(user_id)
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            updated_at=user.get("updated_at")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    user = await get_user_by_username(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "user_id": user["id"],
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        updated_at=current_user.get("updated_at")
    )

@router.get("/users", response_model=List[UserResponse])
async def list_users(current_user: dict = Depends(require_admin)):
    """List all users (admin only)"""
    users = await get_all_users()
    return [
        UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            updated_at=user.get("updated_at")
        )
        for user in users
    ]

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_info(
    user_id: int,
    user_update: UserUpdate,
    current_user: dict = Depends(require_admin)
):
    """Update user information (admin only)"""
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    try:
        await update_user(
            user_id=user_id,
            email=user_update.email,
            role=user_update.role,
            is_active=user_update.is_active,
            password=user_update.password
        )
        
        # Get updated user
        updated_user = await get_user_by_id(user_id)
        return UserResponse(
            id=updated_user["id"],
            username=updated_user["username"],
            email=updated_user["email"],
            role=updated_user["role"],
            is_active=updated_user["is_active"],
            created_at=updated_user["created_at"],
            updated_at=updated_user.get("updated_at")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    current_user: dict = Depends(require_admin)
):
    """Delete a user (admin only)"""
    # Prevent deleting yourself
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Check if user exists
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return None

