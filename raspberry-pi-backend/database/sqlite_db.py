"""
SQLite Database Connection and Models
Replaces MongoDB with SQLite3 for simpler deployment
"""

import sqlite3
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager
import aiosqlite
from dotenv import load_dotenv

load_dotenv()

# Global database path
_db_path: Optional[str] = None
_db_initialized = False

def get_db_path() -> str:
    """Get database file path"""
    global _db_path
    if _db_path is None:
        db_dir = os.getenv("DB_DIR", ".")
        db_name = os.getenv("DB_NAME", "fall_detection.db")
        _db_path = os.path.join(db_dir, db_name)
    return _db_path

async def get_database():
    """Get database connection (async)"""
    db_path = get_db_path()
    return await aiosqlite.connect(db_path)

async def init_database():
    """Initialize SQLite database and create tables"""
    global _db_initialized
    
    if _db_initialized:
        return
    
    db_path = get_db_path()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    async with aiosqlite.connect(db_path) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Create sensor_readings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                location TEXT,
                sensor_type TEXT,
                timestamp INTEGER,
                received_at TEXT NOT NULL,
                data TEXT NOT NULL,
                topic TEXT
            )
        """)
        
        # Create fall_events table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS fall_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                severity_score REAL NOT NULL,
                verified INTEGER NOT NULL DEFAULT 0,
                location TEXT,
                sensor_data TEXT NOT NULL,
                acknowledged INTEGER NOT NULL DEFAULT 0,
                acknowledged_at TEXT
            )
        """)
        
        # Create devices table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                device_type TEXT,
                location TEXT,
                status TEXT NOT NULL DEFAULT 'offline',
                last_seen TEXT NOT NULL
            )
        """)
        
        # Create users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                preferences TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Create alert_logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                channels TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        
        # Create indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensor_device_id ON sensor_readings(device_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensor_received_at ON sensor_readings(received_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_fall_user_id ON fall_events(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_fall_timestamp ON fall_events(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_fall_severity ON fall_events(severity_score)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status)")
        
        await db.commit()
    
    _db_initialized = True
    print(f"SQLite database initialized: {db_path}")

# ==================== Helper Functions ====================

def dict_factory(cursor, row):
    """Convert SQLite row to dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

async def insert_sensor_reading(data: Dict[str, Any]) -> int:
    """Insert sensor reading"""
    async with await get_database() as db:
        db.row_factory = dict_factory
        cursor = await db.execute("""
            INSERT INTO sensor_readings 
            (device_id, location, sensor_type, timestamp, received_at, data, topic)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("device_id"),
            data.get("location"),
            data.get("sensor_type"),
            data.get("timestamp"),
            datetime.utcnow().isoformat(),
            json.dumps(data.get("data", {})),
            data.get("topic")
        ))
        await db.commit()
        return cursor.lastrowid

async def insert_fall_event(event: Dict[str, Any]) -> str:
    """Insert fall event and return event_id"""
    import uuid
    event_id = str(uuid.uuid4())
    
    async with await get_database() as db:
        db.row_factory = dict_factory
        await db.execute("""
            INSERT INTO fall_events 
            (event_id, user_id, timestamp, severity_score, verified, location, sensor_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            event.get("user_id"),
            event.get("timestamp").isoformat() if isinstance(event.get("timestamp"), datetime) else event.get("timestamp"),
            event.get("severity_score"),
            1 if event.get("verified") else 0,
            event.get("location"),
            json.dumps(event.get("sensor_data", {}))
        ))
        await db.commit()
    
    return event_id

async def get_sensor_readings(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """Get sensor readings with filters"""
    async with await get_database() as db:
        db.row_factory = dict_factory
        
        query = "SELECT * FROM sensor_readings WHERE 1=1"
        params = []
        
        if device_id:
            query += " AND device_id LIKE ?"
            params.append(f"%{device_id}%")
        
        if sensor_type:
            query += " AND sensor_type = ?"
            params.append(sensor_type)
        
        query += " ORDER BY received_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        # Parse JSON data field
        for row in rows:
            if row.get("data"):
                try:
                    row["data"] = json.loads(row["data"])
                except:
                    pass
        
        return rows

async def get_fall_events(
    user_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """Get fall events"""
    async with await get_database() as db:
        db.row_factory = dict_factory
        
        query = "SELECT * FROM fall_events WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        # Parse JSON and convert types
        for row in rows:
            if row.get("sensor_data"):
                try:
                    row["sensor_data"] = json.loads(row["sensor_data"])
                except:
                    pass
            row["verified"] = bool(row.get("verified", 0))
            row["acknowledged"] = bool(row.get("acknowledged", 0))
            # Convert timestamp string back to datetime format for API
            if row.get("timestamp"):
                row["timestamp"] = row["timestamp"]  # Keep as ISO string
        
        return rows

async def get_fall_event(event_id: str) -> Optional[Dict]:
    """Get specific fall event by event_id"""
    async with await get_database() as db:
        db.row_factory = dict_factory
        cursor = await db.execute(
            "SELECT * FROM fall_events WHERE event_id = ?",
            (event_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            # Parse JSON
            if row.get("sensor_data"):
                try:
                    row["sensor_data"] = json.loads(row["sensor_data"])
                except:
                    pass
            row["verified"] = bool(row.get("verified", 0))
            row["acknowledged"] = bool(row.get("acknowledged", 0))
        
        return row

async def acknowledge_fall_event(event_id: str) -> bool:
    """Acknowledge a fall event"""
    async with await get_database() as db:
        cursor = await db.execute("""
            UPDATE fall_events 
            SET acknowledged = 1, acknowledged_at = ?
            WHERE event_id = ?
        """, (datetime.utcnow().isoformat(), event_id))
        await db.commit()
        return cursor.rowcount > 0

async def get_devices() -> List[Dict]:
    """Get all devices"""
    async with await get_database() as db:
        db.row_factory = dict_factory
        cursor = await db.execute("SELECT * FROM devices ORDER BY last_seen DESC")
        rows = await cursor.fetchall()
        return rows

async def get_recent_room_sensor_data(seconds: int = 30) -> List[Dict]:
    """Get recent room sensor readings"""
    cutoff_time = (datetime.utcnow() - timedelta(seconds=seconds)).isoformat()
    
    async with await get_database() as db:
        db.row_factory = dict_factory
        cursor = await db.execute("""
            SELECT * FROM sensor_readings 
            WHERE device_id LIKE '%ESP8266%' 
            AND received_at >= ?
            ORDER BY received_at DESC 
            LIMIT 10
        """, (cutoff_time,))
        rows = await cursor.fetchall()
        
        # Parse JSON data
        for row in rows:
            if row.get("data"):
                try:
                    row["data"] = json.loads(row["data"])
                except:
                    pass
        
        return rows

async def count_fall_events(filters: Optional[Dict] = None) -> int:
    """Count fall events with optional filters"""
    async with await get_database() as db:
        query = "SELECT COUNT(*) as count FROM fall_events WHERE 1=1"
        params = []
        
        if filters:
            if "timestamp_gte" in filters:
                query += " AND timestamp >= ?"
                params.append(filters["timestamp_gte"].isoformat() if isinstance(filters["timestamp_gte"], datetime) else filters["timestamp_gte"])
        
        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
        return row[0] if row else 0

async def count_sensor_readings() -> int:
    """Count total sensor readings"""
    async with await get_database() as db:
        cursor = await db.execute("SELECT COUNT(*) as count FROM sensor_readings")
        row = await cursor.fetchone()
        return row[0] if row else 0

async def count_active_devices() -> int:
    """Count active devices"""
    async with await get_database() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM devices WHERE status = 'online'"
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

async def insert_alert_log(event_id: str, channels: List[str], status: str = "sent"):
    """Insert alert log"""
    async with await get_database() as db:
        await db.execute("""
            INSERT INTO alert_logs (event_id, channels, sent_at, status)
            VALUES (?, ?, ?, ?)
        """, (
            event_id,
            json.dumps(channels),
            datetime.utcnow().isoformat(),
            status
        ))
        await db.commit()

async def close_database():
    """Close database connection"""
    # SQLite connections are closed automatically when using context managers
    print("SQLite database connection closed")

