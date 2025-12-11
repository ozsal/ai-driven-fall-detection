"""
Pydantic models for authentication
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: str
    role: str = "viewer"  # Default role: viewer

class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate user role"""
        allowed_roles = ["admin", "viewer", "sensor_manager"]
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class UserUpdate(BaseModel):
    """Model for updating user"""
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        if v is None:
            return v
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate user role"""
        if v is None:
            return v
        allowed_roles = ["admin", "viewer", "sensor_manager"]
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class UserResponse(UserBase):
    """Model for user response (without password)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str

class Token(BaseModel):
    """Model for access token"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Model for token data"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None









