"""
Authentication Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from auth.models import UserCreate, UserLogin, UserResponse, Token
from auth.utils import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_HOURS
from auth.database import (
    create_user, get_user_by_username, get_user_by_email,
    get_user_by_id, get_all_users, update_user, delete_user
)
from auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Register a new user (Admin only)
    
    Roles:
    - admin: Full access
    - sensor_manager: Can manage devices and sensors
    - viewer: Read-only dashboard access
    """
    # Validate role
    valid_roles = ["admin", "sensor_manager", "viewer"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Check if username already exists
    existing_user = await get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = await get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    try:
        user_id = await create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        # Get created user
        user = await get_user_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Login and get access token
    """
    # Get user by username
    user = await get_user_by_username(user_credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.get("is_active", 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "user_id": user["id"],
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    # Remove password from response
    user_response = {k: v for k, v in current_user.items() if k != "hashed_password"}
    return user_response

@router.get("/users", response_model=list[UserResponse])
async def list_users(current_user: dict = Depends(require_role(["admin"]))):
    """
    List all users (Admin only)
    """
    users = await get_all_users()
    # Remove passwords from response
    return [{k: v for k, v in user.items() if k != "hashed_password"} for user in users]

@router.put("/users/{user_id}")
async def update_user_info(
    user_id: int,
    user_data: dict,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Update user information (Admin only)
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Hash password if provided
    if "password" in user_data:
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
    
    success = await update_user(user_id, **user_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user"
        )
    
    updated_user = await get_user_by_id(user_id)
    return {k: v for k, v in updated_user.items() if k != "hashed_password"}

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Deactivate a user (Admin only)
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate user"
        )
    
    return {"message": "User deactivated successfully"}

