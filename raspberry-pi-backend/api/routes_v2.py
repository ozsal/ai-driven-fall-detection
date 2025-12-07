"""
Extended API Routes for v2 Schema
This module adds new API endpoints while maintaining existing ones.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from database.database_v2 import (
    get_device_with_sensors, get_sensor_latest_reading,
    get_all_devices_with_sensors
)
from database.sqlite_db import get_sensor_readings  # Keep for backward compatibility

router = APIRouter()

# ============================================
# Device Endpoints
# ============================================

@router.get("/devices")
async def get_devices_v2():
    """
    Get all devices with their sensors and latest readings
    Returns devices in v2 format with nested sensors
    """
    try:
        devices = await get_all_devices_with_sensors()
        return {
            "devices": devices,
            "count": len(devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching devices: {str(e)}")

@router.get("/devices/{device_id}")
async def get_device_v2(device_id: str):
    """
    Get specific device with its sensors and latest readings
    """
    try:
        device = await get_device_with_sensors(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        return device
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching device: {str(e)}")

# ============================================
# Sensor Reading Endpoints
# ============================================

@router.get("/sensor-readings")
async def get_sensor_readings_v2(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    sensor_type: Optional[str] = Query(None, description="Filter by sensor type")
):
    """
    Get sensor readings with optional filters
    Maintains backward compatibility with existing endpoint
    """
    try:
        # Use existing function for backward compatibility
        readings = await get_sensor_readings(
            device_id=device_id,
            sensor_type=sensor_type,
            limit=100
        )
        return {
            "readings": readings,
            "count": len(readings)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching readings: {str(e)}")

@router.get("/sensor/{sensor_id}/latest-reading")
async def get_sensor_latest_reading_v2(sensor_id: int):
    """
    Get latest reading for a specific sensor by sensor_id
    """
    try:
        reading = await get_sensor_latest_reading(sensor_id)
        if not reading:
            raise HTTPException(
                status_code=404, 
                detail=f"Latest reading for sensor {sensor_id} not found"
            )
        return reading
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching latest reading: {str(e)}"
        )

# ============================================
# Sensor-Specific Reading Endpoints
# ============================================

@router.get("/readings/pir")
async def get_pir_readings(
    sensor_id: Optional[int] = Query(None, description="Filter by sensor ID"),
    limit: int = Query(100, description="Number of readings to return")
):
    """Get PIR sensor readings"""
    import aiosqlite
    from database.sqlite_db import DB_PATH, dict_factory
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = dict_factory
            
            query = "SELECT * FROM pir_readings WHERE 1=1"
            params = []
            
            if sensor_id:
                query += " AND sensor_id = ?"
                params.append(sensor_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await db.execute(query, params)
            readings = await cursor.fetchall()
            
            # Convert motion_detected to boolean
            for reading in readings:
                reading["motion_detected"] = bool(reading.get("motion_detected", 0))
            
            return {"readings": readings, "count": len(readings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching PIR readings: {str(e)}")

@router.get("/readings/ultrasonic")
async def get_ultrasonic_readings(
    sensor_id: Optional[int] = Query(None, description="Filter by sensor ID"),
    limit: int = Query(100, description="Number of readings to return")
):
    """Get Ultrasonic sensor readings"""
    import aiosqlite
    from database.sqlite_db import DB_PATH, dict_factory
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = dict_factory
            
            query = "SELECT * FROM ultrasonic_readings WHERE 1=1"
            params = []
            
            if sensor_id:
                query += " AND sensor_id = ?"
                params.append(sensor_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await db.execute(query, params)
            readings = await cursor.fetchall()
            
            return {"readings": readings, "count": len(readings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Ultrasonic readings: {str(e)}")

@router.get("/readings/dht22")
async def get_dht22_readings(
    sensor_id: Optional[int] = Query(None, description="Filter by sensor ID"),
    limit: int = Query(100, description="Number of readings to return")
):
    """Get DHT22 sensor readings"""
    import aiosqlite
    from database.sqlite_db import DB_PATH, dict_factory
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = dict_factory
            
            query = "SELECT * FROM dht22_readings WHERE 1=1"
            params = []
            
            if sensor_id:
                query += " AND sensor_id = ?"
                params.append(sensor_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await db.execute(query, params)
            readings = await cursor.fetchall()
            
            return {"readings": readings, "count": len(readings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching DHT22 readings: {str(e)}")

@router.get("/readings/wifi")
async def get_wifi_readings(
    sensor_id: Optional[int] = Query(None, description="Filter by sensor ID"),
    limit: int = Query(100, description="Number of readings to return")
):
    """Get WiFi sensor readings"""
    import aiosqlite
    from database.sqlite_db import DB_PATH, dict_factory
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = dict_factory
            
            query = "SELECT * FROM wifi_readings WHERE 1=1"
            params = []
            
            if sensor_id:
                query += " AND sensor_id = ?"
                params.append(sensor_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = await db.execute(query, params)
            readings = await cursor.fetchall()
            
            return {"readings": readings, "count": len(readings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching WiFi readings: {str(e)}")

