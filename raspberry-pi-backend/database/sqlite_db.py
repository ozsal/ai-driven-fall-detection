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
                location TEXT,
                topic TEXT
            )
        """)
        
        # Add topic column if it doesn't exist (for existing databases)
        try:
            await db.execute("ALTER TABLE sensor_readings ADD COLUMN topic TEXT")
        except Exception:
            pass  # Column already exists
        
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
        
        # Sensors table - tracks each sensor separately with its own status
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                total_readings INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_id, sensor_type)
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
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensor_type ON sensor_readings(sensor_type)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_fall_timestamp ON fall_events(timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_fall_user ON fall_events(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensors_device_type ON sensors(device_id, sensor_type)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensors_status ON sensors(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sensors_last_seen ON sensors(last_seen)")
        
        await db.commit()
        print(f"Database initialized at {DB_PATH}")

async def insert_sensor_reading(reading_data: Dict[str, Any]) -> int:
    """Insert a sensor reading into the database"""
    try:
        # Ensure database directory exists
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Ensure database file exists and is initialized
        if not os.path.exists(DB_PATH):
            print(f"⚠️ Database file not found at {DB_PATH}, initializing...")
            await init_database()
        
        # Use a persistent connection approach to ensure data is saved
        db = await aiosqlite.connect(DB_PATH)
        try:
            db.row_factory = dict_factory
            
            # Extract fields
            device_id = reading_data.get("device_id", "unknown")
            sensor_type = reading_data.get("sensor_type", "unknown")
            timestamp = reading_data.get("timestamp", int(datetime.utcnow().timestamp()))
            location = reading_data.get("location")
            topic = reading_data.get("topic")
            
            # Store data as JSON string
            try:
                data_json = json.dumps(reading_data.get("data", {}))
            except Exception as json_error:
                print(f"⚠️ Error serializing data to JSON: {json_error}")
                data_json = json.dumps({"error": "failed_to_serialize", "raw": str(reading_data.get("data", {}))})
            
            print(f"   📝 Inserting: device_id={device_id}, sensor_type={sensor_type}, timestamp={timestamp}")
            print(f"   📝 Data JSON length: {len(data_json)} bytes")
            
            # Insert sensor reading
            cursor = await db.execute("""
                INSERT INTO sensor_readings (device_id, sensor_type, timestamp, data, location, topic)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (device_id, sensor_type, timestamp, data_json, location, topic))
            
            await db.commit()
            reading_id = cursor.lastrowid
            print(f"   ✅ Inserted reading with ID: {reading_id}")
            
            # Verify the insert worked
            verify_cursor = await db.execute("SELECT COUNT(*) as count FROM sensor_readings WHERE id = ?", (reading_id,))
            verify_row = await verify_cursor.fetchone()
            if verify_row and verify_row["count"] > 0:
                print(f"   ✅ Verified: Reading {reading_id} exists in database")
            else:
                print(f"   ❌ WARNING: Reading {reading_id} was inserted but not found in database!")
            
            # Update or insert device
            try:
                await db.execute("""
                    INSERT OR REPLACE INTO devices (device_id, device_type, last_seen, location)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?)
                """, (device_id, sensor_type, location))
                await db.commit()
                print(f"   ✅ Updated device: {device_id}")
            except Exception as device_error:
                print(f"   ⚠️ Warning: Failed to update device: {device_error}")
                # Don't fail the whole operation if device update fails
            
            # Update or insert sensor with its own status
            try:
                # Check if sensor exists
                check_cursor = await db.execute("""
                    SELECT id, total_readings FROM sensors 
                    WHERE device_id = ? AND sensor_type = ?
                """, (device_id, sensor_type))
                sensor_row = await check_cursor.fetchone()
                
                if sensor_row:
                    # Update existing sensor
                    new_total = (sensor_row["total_readings"] or 0) + 1
                    await db.execute("""
                        UPDATE sensors 
                        SET status = 'active', 
                            last_seen = CURRENT_TIMESTAMP,
                            total_readings = ?,
                            location = ?
                        WHERE device_id = ? AND sensor_type = ?
                    """, (new_total, location, device_id, sensor_type))
                    print(f"   ✅ Updated sensor: {device_id}/{sensor_type} (total readings: {new_total})")
                else:
                    # Insert new sensor
                    await db.execute("""
                        INSERT INTO sensors (device_id, sensor_type, status, last_seen, location, total_readings)
                        VALUES (?, ?, 'active', CURRENT_TIMESTAMP, ?, 1)
                    """, (device_id, sensor_type, location))
                    print(f"   ✅ Created new sensor: {device_id}/{sensor_type}")
                
                await db.commit()
            except Exception as sensor_error:
                print(f"   ⚠️ Warning: Failed to update sensor: {sensor_error}")
                # Don't fail the whole operation if sensor update fails
            
            return reading_id
        finally:
            await db.close()
    except Exception as e:
        print(f"❌ CRITICAL: Error inserting sensor reading: {e}")
        print(f"   Database path: {DB_PATH}")
        print(f"   Database exists: {os.path.exists(DB_PATH)}")
        print(f"   Reading data: {reading_data}")
        import traceback
        traceback.print_exc()
        raise

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
    try:
        # Ensure database exists
        if not os.path.exists(DB_PATH):
            print(f"Warning: Database file not found at {DB_PATH}. Initializing...")
            await init_database()
        
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
            
            # Order by id (most recent first) - simpler and more reliable
            query += " ORDER BY id DESC LIMIT ?"
            params.append(limit)
            
            try:
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
            except Exception as query_error:
                print(f"Query error: {query_error}")
                # Fallback: try without ordering
                try:
                    fallback_query = "SELECT * FROM sensor_readings LIMIT ?"
                    cursor = await db.execute(fallback_query, (limit,))
                    rows = await cursor.fetchall()
                except Exception as fallback_error:
                    print(f"Fallback query also failed: {fallback_error}")
                    # Return empty list if table doesn't exist or has issues
                    return []
            
            # Parse JSON data field and ensure all fields are properly formatted
            result = []
            for row in rows:
                # Convert row to dict if it's not already
                if not isinstance(row, dict):
                    row = dict(row)
                
                # Parse JSON data field
                if row.get("data"):
                    try:
                        if isinstance(row["data"], str):
                            row["data"] = json.loads(row["data"])
                        elif not isinstance(row["data"], dict):
                            row["data"] = {}
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"Warning: Failed to parse JSON data for reading {row.get('id')}: {e}")
                        row["data"] = {}
                else:
                    row["data"] = {}
                
                result.append(row)
            
            return result
    except Exception as e:
        print(f"Error in get_sensor_readings: {e}")
        import traceback
        traceback.print_exc()
        raise

async def get_fall_events(
    user_id: Optional[str] = None,
    limit: int = 50,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Get fall events with optional filters"""
    try:
        # Ensure database exists
        if not os.path.exists(DB_PATH):
            print(f"Warning: Database file not found at {DB_PATH}. Initializing...")
            await init_database()
        
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
            
            try:
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
            except Exception as e:
                print(f"Error querying fall_events table: {e}")
                # Table might not exist, return empty list
                return []
            
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
    except Exception as e:
        print(f"Error in get_fall_events: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of raising to prevent API errors
        return []

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
    try:
        # Ensure database exists
        if not os.path.exists(DB_PATH):
            print(f"Warning: Database file not found at {DB_PATH}. Initializing...")
            await init_database()
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = dict_factory
            
            try:
                cursor = await db.execute("SELECT * FROM devices ORDER BY last_seen DESC")
                rows = await cursor.fetchall()
            except Exception as e:
                print(f"Error querying devices table: {e}")
                # Table might not exist, return empty list
                return []
            
            # Parse JSON metadata field
            for row in rows:
                if row.get("metadata"):
                    try:
                        row["metadata"] = json.loads(row["metadata"])
                    except (json.JSONDecodeError, TypeError):
                        row["metadata"] = {}
            
            return rows
    except Exception as e:
        print(f"Error in get_devices: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of raising to prevent API errors
        return []

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
    try:
        # Ensure database exists
        if not os.path.exists(DB_PATH):
            print(f"Warning: Database file not found at {DB_PATH}. Initializing...")
            await init_database()
        
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
            
            try:
                cursor = await db.execute(query, params)
                row = await cursor.fetchone()
                return row["count"] if row else 0
            except Exception as e:
                print(f"Error counting fall_events: {e}")
                # Table might not exist, return 0
                return 0
    except Exception as e:
        print(f"Error in count_fall_events: {e}")
        return 0

async def count_sensor_readings() -> int:
    """Count total sensor readings"""
    try:
        # Ensure database exists
        if not os.path.exists(DB_PATH):
            print(f"Warning: Database file not found at {DB_PATH}. Initializing...")
            await init_database()
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = dict_factory
            
            try:
                cursor = await db.execute("SELECT COUNT(*) as count FROM sensor_readings")
                row = await cursor.fetchone()
                return row["count"] if row else 0
            except Exception as e:
                print(f"Error counting sensor_readings: {e}")
                # Table might not exist, return 0
                return 0
    except Exception as e:
        print(f"Error in count_sensor_readings: {e}")
        return 0

async def count_active_devices() -> int:
    """Count active devices (seen in last 24 hours)"""
    try:
        # Ensure database exists
        if not os.path.exists(DB_PATH):
            print(f"Warning: Database file not found at {DB_PATH}. Initializing...")
            await init_database()
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = dict_factory
            
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            try:
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT device_id) as count 
                    FROM devices 
                    WHERE last_seen >= ?
                """, (cutoff_time.isoformat(),))
                
                row = await cursor.fetchone()
                return row["count"] if row else 0
            except Exception as e:
                print(f"Error counting active devices: {e}")
                # Table might not exist, return 0
                return 0
    except Exception as e:
        print(f"Error in count_active_devices: {e}")
        return 0

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

