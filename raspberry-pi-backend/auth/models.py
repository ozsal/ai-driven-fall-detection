"""
User Authentication Models
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Model for creating a new user"""
    username: str
    email: EmailStr
    password: str
    role: str = "viewer"  # Default role

class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Model for user response (without password)"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Model for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Model for token data"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

