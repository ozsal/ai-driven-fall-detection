"""
Database functions for alerts
"""

import aiosqlite
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import os

# Database path (same as main database)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "fall_detection.db")

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

async def insert_alert(alert_data: Dict[str, Any]) -> int:
    """Insert a new alert into the database"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        device_id = alert_data.get("device_id", "unknown")
        alert_type = alert_data.get("alert_type", "unknown")
        message = alert_data.get("message", "")
        severity = alert_data.get("severity", "low")
        sensor_values = json.dumps(alert_data.get("sensor_values", {}))
        triggered_at = alert_data.get("triggered_at", datetime.utcnow().isoformat())
        
        cursor = await db.execute("""
            INSERT INTO alerts (device_id, alert_type, message, severity, sensor_values, triggered_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (device_id, alert_type, message, severity, sensor_values, triggered_at))
        
        await db.commit()
        return cursor.lastrowid

async def get_alerts(
    device_id: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get alerts with optional filters"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        query = "SELECT * FROM alerts WHERE 1=1"
        params = []
        
        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)
        
        if alert_type:
            query += " AND alert_type = ?"
            params.append(alert_type)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        if acknowledged is not None:
            query += " AND acknowledged = ?"
            params.append(1 if acknowledged else 0)
        
        query += " ORDER BY triggered_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        # Parse JSON sensor_values
        for row in rows:
            if row.get("sensor_values"):
                try:
                    if isinstance(row["sensor_values"], str):
                        row["sensor_values"] = json.loads(row["sensor_values"])
                except:
                    row["sensor_values"] = {}
        
        return rows

async def get_latest_alerts(limit: int = 10, unacknowledged_only: bool = False) -> List[Dict[str, Any]]:
    """Get latest alerts for real-time dashboard"""
    filters = {}
    if unacknowledged_only:
        filters["acknowledged"] = False
    
    return await get_alerts(limit=limit, **filters)

async def get_alert_by_id(alert_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific alert by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
        row = await cursor.fetchone()
        
        if row and row.get("sensor_values"):
            try:
                if isinstance(row["sensor_values"], str):
                    row["sensor_values"] = json.loads(row["sensor_values"])
            except:
                row["sensor_values"] = {}
        
        return row

async def acknowledge_alert(alert_id: int, acknowledged_by: Optional[str] = None) -> bool:
    """Acknowledge an alert"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Use CURRENT_TIMESTAMP for SQLite compatibility
            if acknowledged_by:
                cursor = await db.execute("""
                    UPDATE alerts 
                    SET acknowledged = 1, 
                        acknowledged_at = CURRENT_TIMESTAMP,
                        acknowledged_by = ?
                    WHERE id = ?
                """, (acknowledged_by, alert_id))
            else:
                cursor = await db.execute("""
                    UPDATE alerts 
                    SET acknowledged = 1, 
                        acknowledged_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (alert_id,))
            
            await db.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error acknowledging alert {alert_id}: {e}")
        return False

async def count_alerts(
    device_id: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None
) -> int:
    """Count alerts with optional filters"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        query = "SELECT COUNT(*) as count FROM alerts WHERE 1=1"
        params = []
        
        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)
        
        if alert_type:
            query += " AND alert_type = ?"
            params.append(alert_type)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        if acknowledged is not None:
            query += " AND acknowledged = ?"
            params.append(1 if acknowledged else 0)
        
        cursor = await db.execute(query, params)
        result = await cursor.fetchone()
        return result["count"] if result else 0

async def get_recent_sensor_readings(
    device_id: str,
    sensor_type: str,
    minutes: int = 10,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get recent sensor readings for trend analysis"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = dict_factory
        
        # Calculate timestamp threshold
        from datetime import datetime, timedelta
        threshold_time = datetime.utcnow() - timedelta(minutes=minutes)
        threshold_timestamp = int(threshold_time.timestamp())
        
        cursor = await db.execute("""
            SELECT * FROM sensor_readings
            WHERE device_id = ? 
            AND sensor_type = ?
            AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (device_id, sensor_type, threshold_timestamp, limit))
        
        rows = await cursor.fetchall()
        
        # Parse JSON data
        for row in rows:
            if row.get("data"):
                try:
                    if isinstance(row["data"], str):
                        row["data"] = json.loads(row["data"])
                except:
                    row["data"] = {}
        
        return rows



