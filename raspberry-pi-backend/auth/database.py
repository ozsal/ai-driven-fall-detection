"""
Database functions for user authentication
"""

import aiosqlite
from typing import Optional, List, Dict, Any
from datetime import datetime
from auth.utils import hash_password
import os

# Database path (same as main database)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "fall_detection.db")

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

async def create_user(username: str, email: str, password: str, role: str = "viewer") -> int:
    """Create a new user"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Check if username already exists
        cursor = await db.execute(
            "SELECT id FROM auth_users WHERE username = ?",
            (username,)
        )
        existing = await cursor.fetchone()
        if existing:
            raise ValueError(f"Username '{username}' already exists")
        
        # Check if email already exists
        cursor = await db.execute(
            "SELECT id FROM auth_users WHERE email = ?",
            (email,)
        )
        existing = await cursor.fetchone()
        if existing:
            raise ValueError(f"Email '{email}' already exists")
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert user
        cursor = await db.execute("""
            INSERT INTO auth_users (username, email, hashed_password, role, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            hashed_password,
            role,
            True,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))
        
        await db.commit()
        return cursor.lastrowid

async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute(
            "SELECT * FROM auth_users WHERE username = ?",
            (username,)
        )
        return await cursor.fetchone()

async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute(
            "SELECT * FROM auth_users WHERE id = ?",
            (user_id,)
        )
        return await cursor.fetchone()

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute(
            "SELECT * FROM auth_users WHERE email = ?",
            (email,)
        )
        return await cursor.fetchone()

async def get_all_users() -> List[Dict[str, Any]]:
    """Get all users (admin only)"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute(
            "SELECT id, username, email, role, is_active, created_at, updated_at FROM auth_users ORDER BY created_at DESC"
        )
        return await cursor.fetchall()

async def update_user(user_id: int, email: Optional[str] = None, role: Optional[str] = None, 
                     is_active: Optional[bool] = None, password: Optional[str] = None) -> bool:
    """Update user information"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        updates = []
        params = []
        
        if email is not None:
            # Check if email is already taken by another user
            cursor = await db.execute(
                "SELECT id FROM auth_users WHERE email = ? AND id != ?",
                (email, user_id)
            )
            existing = await cursor.fetchone()
            if existing:
                raise ValueError(f"Email '{email}' is already taken")
            
            updates.append("email = ?")
            params.append(email)
        
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(int(is_active))
        
        if password is not None:
            hashed_password = hash_password(password)
            updates.append("hashed_password = ?")
            params.append(hashed_password)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(user_id)
        
        query = f"UPDATE auth_users SET {', '.join(updates)} WHERE id = ?"
        await db.execute(query, params)
        await db.commit()
        return True

async def delete_user(user_id: int) -> bool:
    """Delete a user (admin only)"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM auth_users WHERE id = ?", (user_id,))
        await db.commit()
        return cursor.rowcount > 0

async def create_default_admin():
    """Create default admin user if no users exist"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Check if any users exist
        cursor = await db.execute("SELECT COUNT(*) as count FROM auth_users")
        result = await cursor.fetchone()
        user_count = result["count"] if result else 0
        
        if user_count == 0:
            # Create default admin user
            default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            default_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@fall-detection.local")
            
            try:
                await create_user(
                    username=default_username,
                    email=default_email,
                    password=default_password,
                    role="admin"
                )
                print(f"✓ Created default admin user: {default_username}")
                print(f"  ⚠️  Please change the default password immediately!")
            except Exception as e:
                print(f"⚠️  Could not create default admin: {e}")


