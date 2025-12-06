# SQLite Database Setup Guide

This guide will help you set up the SQLite database for the Fall Detection System.

## Overview

The system uses **SQLite3**, which is a file-based database. This means:
- ✅ No separate database server required
- ✅ No configuration needed
- ✅ Database is stored in a single file (`fall_detection.db`)
- ✅ Automatically initialized on first run

## Prerequisites

1. **Python 3.11 or 3.12** (recommended)
2. **aiosqlite** package (included in `requirements.txt`)

## Quick Setup (Automatic)

The database will be **automatically initialized** when you start the backend API. The `init_database()` function is called during startup.

### Option 1: Automatic Setup (Recommended)

Just start the backend - the database will be created automatically:

```bash
cd raspberry-pi-backend
python api/main.py
```

Or use the start script:

```bash
./start.sh
```

## Manual Setup

If you want to initialize the database manually before starting the API:

### Step 1: Install Dependencies

Make sure you have installed all Python dependencies:

```bash
cd raspberry-pi-backend

# Activate virtual environment (if using one)
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Setup Script

Run the database setup script:

```bash
python setup_database.py
```

**Expected Output:**
```
Setting up SQLite database...
Database initialized at /path/to/raspberry-pi-backend/fall_detection.db
✓ Database setup completed successfully!
Database file location: /path/to/raspberry-pi-backend/fall_detection.db
```

### Step 3: Verify Database Creation

Check that the database file was created:

```bash
# On Linux/Mac
ls -lh fall_detection.db

# On Windows
dir fall_detection.db
```

The database file should be approximately **50-60 KB** after initialization.

## Database Structure

The database contains the following tables:

### 1. `sensor_readings`
Stores all sensor data from ESP8266 nodes and other sensors.
- `id` - Primary key
- `device_id` - Device identifier
- `sensor_type` - Type of sensor (e.g., 'dht22', 'pir', 'ultrasonic')
- `timestamp` - Unix timestamp
- `data` - JSON data from sensors
- `location` - Optional location information
- `received_at` - When the data was received by the backend

### 2. `fall_events`
Stores detected fall events.
- `id` - Primary key
- `user_id` - User/device identifier
- `timestamp` - When the fall was detected
- `severity_score` - ML-calculated severity (0-10)
- `verified` - Whether the fall was verified by room sensors
- `sensor_data` - JSON containing sensor data at time of fall
- `location` - Location where fall occurred
- `acknowledged` - Whether the event was acknowledged
- `acknowledged_at` - When the event was acknowledged

### 3. `devices`
Tracks all connected devices.
- `device_id` - Primary key
- `device_type` - Type of device (e.g., 'esp8266', 'room_sensor')
- `status` - Device status ('active', 'inactive')
- `last_seen` - Last time device sent data
- `location` - Device location
- `metadata` - Additional device information (JSON)

### 4. `users`
User information (for future use).
- `user_id` - Primary key
- `name` - User name
- `email` - Email address
- `phone` - Phone number

### 5. `alert_logs`
Logs of alert notifications sent.
- `id` - Primary key
- `event_id` - Foreign key to `fall_events`
- `channels` - JSON array of notification channels used
- `status` - Alert status ('sent', 'failed')
- `sent_at` - When the alert was sent

## Database Location

The database file is stored at:
```
raspberry-pi-backend/fall_detection.db
```

**Note:** The database file is automatically created in the `raspberry-pi-backend` directory when first initialized.

## Using the Database

### Python API

The database functions are available in `database/sqlite_db.py`:

```python
from database.sqlite_db import (
    init_database,
    insert_sensor_reading,
    insert_fall_event,
    get_sensor_readings,
    get_fall_events,
    get_devices,
    count_fall_events,
    count_sensor_readings,
    count_active_devices
)

# Initialize database (usually done automatically)
await init_database()

# Insert a sensor reading
await insert_sensor_reading({
    "device_id": "ESP8266_001",
    "sensor_type": "dht22",
    "timestamp": 1234567890,
    "data": {"temperature_c": 22.5, "humidity_percent": 45.0},
    "location": "Living Room"
})

# Get recent sensor readings
readings = await get_sensor_readings(device_id="ESP8266_001", limit=10)

# Get fall events
events = await get_fall_events(limit=20)
```

## Viewing Database Contents

### Using SQLite Command Line

```bash
# Open the database
sqlite3 fall_detection.db

# View all tables
.tables

# View sensor readings
SELECT * FROM sensor_readings LIMIT 10;

# View fall events
SELECT * FROM fall_events ORDER BY timestamp DESC LIMIT 10;

# View devices
SELECT * FROM devices;

# Exit
.quit
```

### Using Python

```python
import aiosqlite
import json

async def view_database():
    async with aiosqlite.connect('fall_detection.db') as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM fall_events LIMIT 5") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                print(dict(row))

# Run it
import asyncio
asyncio.run(view_database())
```

## Troubleshooting

### Database file not created

**Problem:** Database file doesn't exist after running setup.

**Solution:**
1. Check file permissions in the `raspberry-pi-backend` directory
2. Ensure Python has write permissions
3. Run the setup script manually: `python setup_database.py`

### Permission Errors

**Problem:** `PermissionError` when trying to create database.

**Solution:**
```bash
# On Linux/Mac, check permissions
ls -la raspberry-pi-backend/

# Fix permissions if needed
chmod 755 raspberry-pi-backend/
```

### Database Locked

**Problem:** `database is locked` error.

**Solution:**
- Make sure only one instance of the backend is running
- Close any SQLite clients that have the database open
- Restart the backend

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'aiosqlite'`

**Solution:**
```bash
pip install aiosqlite==0.19.0
# OR
pip install -r requirements.txt
```

## Backup and Restore

### Backup Database

```bash
# Simple copy
cp fall_detection.db fall_detection.db.backup

# Or use SQLite dump
sqlite3 fall_detection.db ".backup fall_detection.db.backup"
```

### Restore Database

```bash
# Copy backup back
cp fall_detection.db.backup fall_detection.db

# Or restore from dump
sqlite3 fall_detection.db < backup.sql
```

## Database Maintenance

### Vacuum (Optimize)

```sql
VACUUM;
```

### Check Database Integrity

```sql
PRAGMA integrity_check;
```

### Get Database Size

```bash
# On Linux/Mac
du -h fall_detection.db

# On Windows
dir fall_detection.db
```

## Next Steps

After setting up the database:

1. ✅ Start the backend API: `python api/main.py`
2. ✅ Connect your ESP8266 sensors
3. ✅ Verify data is being stored: Check `/api/sensor-readings` endpoint
4. ✅ Monitor fall events: Check `/api/fall-events` endpoint

## Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [aiosqlite Documentation](https://aiosqlite.omnilib.dev/)
- [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)

