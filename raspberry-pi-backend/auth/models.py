"""
User Authentication Models
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re

class UserCreate(BaseModel):
    """Model for creating a new user"""
    username: str
    email: str
    password: str
    role: str = "viewer"  # Default role
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v

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

