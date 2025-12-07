"""
Extended Database Functions for v2 Schema
This module extends the existing database.py with new tables and functions
while maintaining backward compatibility with existing code.
"""

import os
import json
import aiosqlite
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database.sqlite_db import DB_PATH, dict_factory

# ============================================
# Database Schema Migration Functions
# ============================================

async def migrate_database_to_v2():
    """
    Migrate existing database to v2 schema
    This function safely updates the database structure without losing data
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        print("🔄 Starting database migration to v2 schema...")
        
        # 1. Update devices table - add id and device_name if they don't exist
        try:
            # Check if id column exists
            cursor = await db.execute("PRAGMA table_info(devices)")
            columns = await cursor.fetchall()
            column_names = [col["name"] for col in columns]
            
            if "id" not in column_names:
                print("   Adding 'id' column to devices table...")
                # SQLite doesn't support adding PRIMARY KEY column, so we'll create a new table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS devices_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT UNIQUE NOT NULL,
                        device_name TEXT,
                        device_type TEXT NOT NULL,
                        status TEXT DEFAULT 'active',
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        location TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Copy existing data
                await db.execute("""
                    INSERT INTO devices_new (device_id, device_type, status, last_seen, location, metadata, created_at)
                    SELECT device_id, device_type, status, last_seen, location, metadata, created_at
                    FROM devices
                """)
                
                # Drop old table and rename new one
                await db.execute("DROP TABLE devices")
                await db.execute("ALTER TABLE devices_new RENAME TO devices")
                print("   ✅ Updated devices table structure")
            
            if "device_name" not in column_names:
                await db.execute("ALTER TABLE devices ADD COLUMN device_name TEXT")
                print("   ✅ Added device_name column to devices table")
                
        except Exception as e:
            print(f"   ⚠️ Warning: Could not update devices table: {e}")
        
        # 2. Update sensors table - add sensor_name and device_id_fk
        try:
            cursor = await db.execute("PRAGMA table_info(sensors)")
            columns = await cursor.fetchall()
            column_names = [col["name"] for col in columns]
            
            if "sensor_name" not in column_names:
                await db.execute("ALTER TABLE sensors ADD COLUMN sensor_name TEXT")
                print("   ✅ Added sensor_name column to sensors table")
            
            if "device_id_fk" not in column_names:
                await db.execute("ALTER TABLE sensors ADD COLUMN device_id_fk INTEGER")
                print("   ✅ Added device_id_fk column to sensors table")
                
                # Try to populate device_id_fk from devices table
                try:
                    await db.execute("""
                        UPDATE sensors s
                        SET device_id_fk = (
                            SELECT d.id FROM devices d 
                            WHERE d.device_id = s.device_id 
                            LIMIT 1
                        )
                    """)
                    print("   ✅ Populated device_id_fk in sensors table")
                except Exception as e:
                    print(f"   ⚠️ Could not populate device_id_fk: {e}")
                    
        except Exception as e:
            print(f"   ⚠️ Warning: Could not update sensors table: {e}")
        
        # 3. Create new sensor-specific reading tables
        try:
            # PIR readings
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pir_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    motion_detected INTEGER NOT NULL,
                    timestamp INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
            """)
            
            # Ultrasonic readings
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ultrasonic_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    distance_cm REAL NOT NULL,
                    timestamp INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
            """)
            
            # DHT22 readings
            await db.execute("""
                CREATE TABLE IF NOT EXISTS dht22_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    temperature_c REAL NOT NULL,
                    humidity_percent REAL NOT NULL,
                    timestamp INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
            """)
            
            # WiFi readings
            await db.execute("""
                CREATE TABLE IF NOT EXISTS wifi_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    rssi INTEGER NOT NULL,
                    timestamp INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
            """)
            
            print("   ✅ Created sensor-specific reading tables")
            
        except Exception as e:
            print(f"   ⚠️ Warning: Could not create reading tables: {e}")
        
        # 4. Create indexes
        try:
            indexes = [
                ("idx_pir_sensor", "pir_readings", "sensor_id"),
                ("idx_pir_timestamp", "pir_readings", "timestamp"),
                ("idx_ultrasonic_sensor", "ultrasonic_readings", "sensor_id"),
                ("idx_ultrasonic_timestamp", "ultrasonic_readings", "timestamp"),
                ("idx_dht22_sensor", "dht22_readings", "sensor_id"),
                ("idx_dht22_timestamp", "dht22_readings", "timestamp"),
                ("idx_wifi_sensor", "wifi_readings", "sensor_id"),
                ("idx_wifi_timestamp", "wifi_readings", "timestamp"),
                ("idx_sensors_device_fk", "sensors", "device_id_fk"),
            ]
            
            for idx_name, table, column in indexes:
                try:
                    await db.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})")
                except Exception as e:
                    print(f"   ⚠️ Could not create index {idx_name}: {e}")
            
            print("   ✅ Created indexes")
            
        except Exception as e:
            print(f"   ⚠️ Warning: Could not create indexes: {e}")
        
        await db.commit()
        print("✅ Database migration to v2 completed!")

# ============================================
# Device Management Functions
# ============================================

async def get_or_create_device(device_id: str, device_name: Optional[str] = None, 
                               location: Optional[str] = None) -> Dict[str, Any]:
    """
    Get existing device or create new one
    Returns device dict with 'id' field
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Try to get existing device by device_id
        cursor = await db.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        device = await cursor.fetchone()
        
        if device:
            # Update last_seen and location if provided
            if location:
                await db.execute("""
                    UPDATE devices 
                    SET last_seen = CURRENT_TIMESTAMP, 
                        location = COALESCE(?, location),
                        status = 'online'
                    WHERE device_id = ?
                """, (location, device_id))
            else:
                await db.execute("""
                    UPDATE devices 
                    SET last_seen = CURRENT_TIMESTAMP, 
                        status = 'online'
                    WHERE device_id = ?
                """, (device_id,))
            
            await db.commit()
            
            # Get updated device
            cursor = await db.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
            device = await cursor.fetchone()
            
            # Ensure device has 'id' field (for v2 schema)
            if "id" not in device:
                # If no id, try to get it from device_id (legacy)
                device["id"] = device.get("device_id")
            
            return device
        else:
            # Create new device
            device_type = "esp8266"  # Default
            if "ESP8266" in device_id.upper() or "NODE" in device_id.upper():
                device_type = "esp8266"
            elif "RASPBERRY" in device_id.upper() or "PI" in device_id.upper():
                device_type = "raspberry_pi"
            
            # Check if devices table has 'id' column (v2 schema)
            cursor = await db.execute("PRAGMA table_info(devices)")
            columns = await cursor.fetchall()
            has_id_column = any(col["name"] == "id" for col in columns)
            
            if has_id_column:
                cursor = await db.execute("""
                    INSERT INTO devices (device_id, device_name, device_type, location, status, last_seen)
                    VALUES (?, ?, ?, ?, 'online', CURRENT_TIMESTAMP)
                """, (device_id, device_name or device_id, device_type, location))
                device_id_pk = cursor.lastrowid
            else:
                # Legacy schema - device_id is PRIMARY KEY
                await db.execute("""
                    INSERT INTO devices (device_id, device_type, location, status, last_seen)
                    VALUES (?, ?, ?, 'active', CURRENT_TIMESTAMP)
                """, (device_id, device_type, location))
                device_id_pk = device_id
            
            await db.commit()
            
            # Get created device
            if has_id_column:
                cursor = await db.execute("SELECT * FROM devices WHERE id = ?", (device_id_pk,))
            else:
                cursor = await db.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
            device = await cursor.fetchone()
            
            if not device:
                # Fallback: create dict manually
                device = {
                    "id": device_id_pk if has_id_column else device_id,
                    "device_id": device_id,
                    "device_name": device_name or device_id,
                    "device_type": device_type,
                    "location": location,
                    "status": "online" if has_id_column else "active",
                    "last_seen": datetime.utcnow().isoformat()
                }
            
            return device

# ============================================
# Sensor Management Functions
# ============================================

async def get_or_create_sensor(device_id: str, sensor_type: str, 
                               sensor_name: Optional[str] = None,
                               device_obj: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Get existing sensor or create new one
    device_id can be string (device_id) or int (devices.id)
    Returns sensor dict with 'id' field
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Get device if not provided
        if device_obj is None:
            device_obj = await get_or_create_device(device_id)
        
        device_db_id = device_obj.get("id") or device_obj.get("device_id")
        
        # Try to get existing sensor
        cursor = await db.execute("""
            SELECT * FROM sensors 
            WHERE device_id = ? AND sensor_type = ?
        """, (device_id, sensor_type))
        sensor = await cursor.fetchone()
        
        if sensor:
            # Update last_seen and status
            await db.execute("""
                UPDATE sensors 
                SET last_seen = CURRENT_TIMESTAMP, 
                    status = 'active',
                    device_id_fk = ?
                WHERE device_id = ? AND sensor_type = ?
            """, (device_db_id, device_id, sensor_type))
            await db.commit()
            
            # Get updated sensor
            cursor = await db.execute("""
                SELECT * FROM sensors 
                WHERE device_id = ? AND sensor_type = ?
            """, (device_id, sensor_type))
            sensor = await cursor.fetchone()
            
            return sensor
        else:
            # Create new sensor
            sensor_name = sensor_name or f"{sensor_type.upper()} Sensor"
            
            # Check if sensors table has device_id_fk column
            cursor = await db.execute("PRAGMA table_info(sensors)")
            columns = await cursor.fetchall()
            has_fk_column = any(col["name"] == "device_id_fk" for col in columns)
            
            if has_fk_column:
                cursor = await db.execute("""
                    INSERT INTO sensors (device_id, sensor_type, sensor_name, device_id_fk, status, last_seen)
                    VALUES (?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
                """, (device_id, sensor_type, sensor_name, device_db_id))
            else:
                cursor = await db.execute("""
                    INSERT INTO sensors (device_id, sensor_type, status, last_seen)
                    VALUES (?, ?, 'active', CURRENT_TIMESTAMP)
                """, (device_id, sensor_type))
            
            sensor_id = cursor.lastrowid
            await db.commit()
            
            # Get created sensor
            cursor = await db.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,))
            sensor = await cursor.fetchone()
            
            return sensor

# ============================================
# Sensor Reading Insertion Functions
# ============================================

async def insert_pir_reading(sensor_id: int, motion_detected: bool, timestamp: int) -> int:
    """Insert PIR reading into pir_readings table"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO pir_readings (sensor_id, motion_detected, timestamp)
            VALUES (?, ?, ?)
        """, (sensor_id, 1 if motion_detected else 0, timestamp))
        await db.commit()
        return cursor.lastrowid

async def insert_ultrasonic_reading(sensor_id: int, distance_cm: float, timestamp: int) -> int:
    """Insert ultrasonic reading into ultrasonic_readings table"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO ultrasonic_readings (sensor_id, distance_cm, timestamp)
            VALUES (?, ?, ?)
        """, (sensor_id, distance_cm, timestamp))
        await db.commit()
        return cursor.lastrowid

async def insert_dht22_reading(sensor_id: int, temperature_c: float, 
                               humidity_percent: float, timestamp: int) -> int:
    """Insert DHT22 reading into dht22_readings table"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO dht22_readings (sensor_id, temperature_c, humidity_percent, timestamp)
            VALUES (?, ?, ?, ?)
        """, (sensor_id, temperature_c, humidity_percent, timestamp))
        await db.commit()
        return cursor.lastrowid

async def insert_wifi_reading(sensor_id: int, rssi: int, timestamp: int) -> int:
    """Insert WiFi reading into wifi_readings table"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO wifi_readings (sensor_id, rssi, timestamp)
            VALUES (?, ?, ?)
        """, (sensor_id, rssi, timestamp))
        await db.commit()
        return cursor.lastrowid

# ============================================
# Query Functions
# ============================================

async def get_device_with_sensors(device_id: str) -> Optional[Dict[str, Any]]:
    """Get device with all its sensors and latest readings"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Get device
        cursor = await db.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        device = await cursor.fetchone()
        
        if not device:
            return None
        
        # Get all sensors for this device
        cursor = await db.execute("""
            SELECT * FROM sensors 
            WHERE device_id = ?
            ORDER BY sensor_type
        """, (device_id,))
        sensors = await cursor.fetchall()
        
        # Get latest reading for each sensor
        for sensor in sensors:
            sensor_id = sensor["id"]
            sensor_type = sensor["sensor_type"]
            
            # Get latest reading based on sensor type
            if sensor_type == "pir":
                cursor = await db.execute("""
                    SELECT * FROM pir_readings 
                    WHERE sensor_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (sensor_id,))
            elif sensor_type == "ultrasonic":
                cursor = await db.execute("""
                    SELECT * FROM ultrasonic_readings 
                    WHERE sensor_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (sensor_id,))
            elif sensor_type == "dht22":
                cursor = await db.execute("""
                    SELECT * FROM dht22_readings 
                    WHERE sensor_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (sensor_id,))
            elif sensor_type == "wifi":
                cursor = await db.execute("""
                    SELECT * FROM wifi_readings 
                    WHERE sensor_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (sensor_id,))
            else:
                sensor["latest_reading"] = None
                continue
            
            latest_reading = await cursor.fetchone()
            sensor["latest_reading"] = latest_reading
        
        device["sensors"] = sensors
        return device

async def get_sensor_latest_reading(sensor_id: int) -> Optional[Dict[str, Any]]:
    """Get latest reading for a specific sensor"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Get sensor info
        cursor = await db.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,))
        sensor = await cursor.fetchone()
        
        if not sensor:
            return None
        
        sensor_type = sensor["sensor_type"]
        
        # Get latest reading based on sensor type
        if sensor_type == "pir":
            cursor = await db.execute("""
                SELECT * FROM pir_readings 
                WHERE sensor_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (sensor_id,))
        elif sensor_type == "ultrasonic":
            cursor = await db.execute("""
                SELECT * FROM ultrasonic_readings 
                WHERE sensor_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (sensor_id,))
        elif sensor_type == "dht22":
            cursor = await db.execute("""
                SELECT * FROM dht22_readings 
                WHERE sensor_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (sensor_id,))
        elif sensor_type == "wifi":
            cursor = await db.execute("""
                SELECT * FROM wifi_readings 
                WHERE sensor_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (sensor_id,))
        else:
            return None
        
        reading = await cursor.fetchone()
        return reading

async def get_all_devices_with_sensors() -> List[Dict[str, Any]]:
    """Get all devices with their sensors"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT * FROM devices ORDER BY device_id")
        devices = await cursor.fetchall()
        
        result = []
        for device in devices:
            device_with_sensors = await get_device_with_sensors(device["device_id"])
            if device_with_sensors:
                result.append(device_with_sensors)
        
        return result

