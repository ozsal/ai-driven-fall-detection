"""
User Database Operations
"""
import aiosqlite
from typing import Optional, List
from datetime import datetime
from database.sqlite_db import DB_PATH, dict_factory

async def create_user(username: str, email: str, hashed_password: str, role: str = "viewer") -> int:
    """Create a new user in the database"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        try:
            cursor = await db.execute("""
                INSERT INTO users (username, email, hashed_password, role, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (username, email, hashed_password, role))
            await db.commit()
            return cursor.lastrowid
        except aiosqlite.IntegrityError as e:
            if "username" in str(e):
                raise ValueError(f"Username '{username}' already exists")
            elif "email" in str(e):
                raise ValueError(f"Email '{email}' already exists")
            raise

async def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = await cursor.fetchone()
        return row

async def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = await cursor.fetchone()
        return row

async def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return row

async def get_all_users() -> List[dict]:
    """Get all users"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT id, username, email, role, is_active, created_at, updated_at FROM users ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return rows

async def update_user(user_id: int, **kwargs) -> bool:
    """Update user fields"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        allowed_fields = ["username", "email", "hashed_password", "role", "is_active"]
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        await db.execute(query, values)
        await db.commit()
        return True

async def delete_user(user_id: int) -> bool:
    """Delete a user (soft delete by setting is_active = 0)"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("""
            UPDATE users 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (user_id,))
        await db.commit()
        return cursor.rowcount > 0

async def create_default_admin():
    """Create a default admin user if no users exist"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Check if any users exist
        cursor = await db.execute("SELECT COUNT(*) as count FROM users")
        result = await cursor.fetchone()
        
        if result and result["count"] == 0:
            # Create default admin user
            from auth.utils import hash_password
            default_password = hash_password("admin123")  # Change this in production!
            
            await db.execute("""
                INSERT INTO users (username, email, hashed_password, role, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, ("admin", "admin@example.com", default_password, "admin"))
            await db.commit()
            print("✅ Created default admin user: username='admin', password='admin123'")
            print("⚠️  IMPORTANT: Change the default admin password in production!")

