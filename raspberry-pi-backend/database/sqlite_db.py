"""
SQLite Database Module
Asynchronous SQLite operations for the Fall Detection System
"""

import aiosqlite
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "fall_detection.db")

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

async def init_database():
    """Initialize database and create tables if they don't exist"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Sensor readings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                data TEXT NOT NULL,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location TEXT
            )
        """)
        
        # Fall events table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS fall_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                severity_score REAL NOT NULL,
                verified BOOLEAN DEFAULT 0,
                sensor_data TEXT NOT NULL,
                location TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Devices table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                device_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Users table (for future use)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Alert logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                channels TEXT NOT NULL,
                status TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES fall_events(id)
            )
        """)
        
        # Create indexes for better performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensor_device ON sensor_readings(device_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_fall_timestamp ON fall_events(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_fall_user ON fall_events(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen)")
        
        await db.commit()
        print(f"Database initialized at {DB_PATH}")

async def insert_sensor_reading(reading_data: Dict[str, Any]) -> int:
    """Insert a sensor reading into the database"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Extract fields
        device_id = reading_data.get("device_id", "unknown")
        sensor_type = reading_data.get("sensor_type", "unknown")
        timestamp = reading_data.get("timestamp", int(datetime.utcnow().timestamp()))
        location = reading_data.get("location")
        
        # Store data as JSON string
        data_json = json.dumps(reading_data.get("data", {}))
        
        cursor = await db.execute("""
            INSERT INTO sensor_readings (device_id, sensor_type, timestamp, data, location)
            VALUES (?, ?, ?, ?, ?)
        """, (device_id, sensor_type, timestamp, data_json, location))
        
        await db.commit()
        
        # Update or insert device
        await db.execute("""
            INSERT OR REPLACE INTO devices (device_id, device_type, last_seen, location)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?)
        """, (device_id, sensor_type, location))
        await db.commit()
        
        return cursor.lastrowid

async def insert_fall_event(event_data: Dict[str, Any]) -> int:
    """Insert a fall event into the database"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        user_id = event_data.get("user_id", "unknown")
        timestamp = event_data.get("timestamp", datetime.utcnow())
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()
        
        severity_score = event_data.get("severity_score", 0.0)
        verified = 1 if event_data.get("verified", False) else 0
        location = event_data.get("location")
        sensor_data_json = json.dumps(event_data.get("sensor_data", {}))
        
        cursor = await db.execute("""
            INSERT INTO fall_events (user_id, timestamp, severity_score, verified, sensor_data, location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, timestamp, severity_score, verified, sensor_data_json, location))
        
        await db.commit()
        return cursor.lastrowid

async def get_sensor_readings(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Get sensor readings with optional filters"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        query = "SELECT * FROM sensor_readings WHERE 1=1"
        params = []
        
        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)
        
        if sensor_type:
            query += " AND sensor_type = ?"
            params.append(sensor_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        # Parse JSON data field
        for row in rows:
            if row.get("data"):
                try:
                    row["data"] = json.loads(row["data"])
                except (json.JSONDecodeError, TypeError):
                    row["data"] = {}
        
        return rows

async def get_fall_events(
    user_id: Optional[str] = None,
    limit: int = 50,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Get fall events with optional filters"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        query = "SELECT * FROM fall_events WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if filters:
            if "timestamp_gte" in filters:
                query += " AND timestamp >= ?"
                params.append(filters["timestamp_gte"].isoformat())
            
            if "acknowledged" in filters:
                query += " AND acknowledged = ?"
                params.append(1 if filters["acknowledged"] else 0)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        # Parse JSON sensor_data field
        for row in rows:
            if row.get("sensor_data"):
                try:
                    row["sensor_data"] = json.loads(row["sensor_data"])
                except (json.JSONDecodeError, TypeError):
                    row["sensor_data"] = {}
            
            # Convert boolean fields
            row["verified"] = bool(row.get("verified", 0))
            row["acknowledged"] = bool(row.get("acknowledged", 0))
        
        return rows

async def get_fall_event(event_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific fall event by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT * FROM fall_events WHERE id = ?", (event_id,))
        row = await cursor.fetchone()
        
        if row:
            # Parse JSON sensor_data field
            if row.get("sensor_data"):
                try:
                    row["sensor_data"] = json.loads(row["sensor_data"])
                except (json.JSONDecodeError, TypeError):
                    row["sensor_data"] = {}
            
            # Convert boolean fields
            row["verified"] = bool(row.get("verified", 0))
            row["acknowledged"] = bool(row.get("acknowledged", 0))
        
        return row

async def acknowledge_fall_event(event_id: int) -> bool:
    """Acknowledge a fall event"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("""
            UPDATE fall_events 
            SET acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (event_id,))
        
        await db.commit()
        return cursor.rowcount > 0

async def get_devices() -> List[Dict[str, Any]]:
    """Get all devices"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT * FROM devices ORDER BY last_seen DESC")
        rows = await cursor.fetchall()
        
        # Parse JSON metadata field
        for row in rows:
            if row.get("metadata"):
                try:
                    row["metadata"] = json.loads(row["metadata"])
                except (json.JSONDecodeError, TypeError):
                    row["metadata"] = {}
        
        return rows

async def get_recent_room_sensor_data(minutes: int = 5, limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent room sensor data for ML analysis"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        cursor = await db.execute("""
            SELECT * FROM sensor_readings
            WHERE timestamp >= ? 
            AND sensor_type IN ('room_sensor', 'esp8266', 'dht22', 'pir', 'ultrasonic')
            ORDER BY timestamp DESC
            LIMIT ?
        """, (cutoff_timestamp, limit))
        
        rows = await cursor.fetchall()
        
        # Parse JSON data field
        for row in rows:
            if row.get("data"):
                try:
                    row["data"] = json.loads(row["data"])
                except (json.JSONDecodeError, TypeError):
                    row["data"] = {}
        
        return rows

async def count_fall_events(filters: Optional[Dict[str, Any]] = None) -> int:
    """Count fall events with optional filters"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        query = "SELECT COUNT(*) as count FROM fall_events WHERE 1=1"
        params = []
        
        if filters:
            if "timestamp_gte" in filters:
                query += " AND timestamp >= ?"
                params.append(filters["timestamp_gte"].isoformat())
            
            if "acknowledged" in filters:
                query += " AND acknowledged = ?"
                params.append(1 if filters["acknowledged"] else 0)
        
        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
        return row[0] if row else 0

async def count_sensor_readings() -> int:
    """Count total sensor readings"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT COUNT(*) as count FROM sensor_readings")
        row = await cursor.fetchone()
        return row[0] if row else 0

async def count_active_devices() -> int:
    """Count active devices (seen in last 24 hours)"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        cursor = await db.execute("""
            SELECT COUNT(DISTINCT device_id) as count 
            FROM devices 
            WHERE last_seen >= ?
        """, (cutoff_time.isoformat(),))
        
        row = await cursor.fetchone()
        return row[0] if row else 0

async def insert_alert_log(event_id: int, channels: List[str], status: str):
    """Insert an alert log entry"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        channels_json = json.dumps(channels)
        
        await db.execute("""
            INSERT INTO alert_logs (event_id, channels, status)
            VALUES (?, ?, ?)
        """, (event_id, channels_json, status))
        
        await db.commit()

