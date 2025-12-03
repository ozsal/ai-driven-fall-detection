"""
MongoDB Database Connection and Models
"""

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    # Fallback if motor not available
    AsyncIOMotorClient = None

from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Global database instance
_database = None
_client = None

async def get_database():
    """Get database instance"""
    global _database
    if _database is None:
        await init_database()
    return _database

async def init_database():
    """Initialize MongoDB connection"""
    global _database, _client
    
    if AsyncIOMotorClient is None:
        raise ImportError("motor package not installed. Install with: pip install motor")
    
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB_NAME", "fall_detection_db")
    
    try:
        _client = AsyncIOMotorClient(mongodb_uri)
        _database = _client[db_name]
        
        # Create indexes for better performance
        await create_indexes()
        
        print(f"MongoDB connected: {db_name}")
        return _database
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        raise

async def create_indexes():
    """Create database indexes"""
    if _database is None:
        return
    
    try:
        # Indexes for sensor_readings
        await _database.sensor_readings.create_index("device_id")
        await _database.sensor_readings.create_index("timestamp")
        await _database.sensor_readings.create_index("received_at")
        await _database.sensor_readings.create_index([("device_id", 1), ("timestamp", -1)])
        
        # Indexes for fall_events
        await _database.fall_events.create_index("user_id")
        await _database.fall_events.create_index("timestamp")
        await _database.fall_events.create_index([("user_id", 1), ("timestamp", -1)])
        await _database.fall_events.create_index("severity_score")
        
        # Indexes for devices
        await _database.devices.create_index("device_id", unique=True)
        await _database.devices.create_index("status")
        
        # Indexes for users
        await _database.users.create_index("email", unique=True)
        await _database.users.create_index("user_id", unique=True)
        
        print("Database indexes created")
    except Exception as e:
        print(f"Error creating indexes: {e}")

async def close_database():
    """Close database connection"""
    global _client
    if _client:
        _client.close()
        print("MongoDB connection closed")

