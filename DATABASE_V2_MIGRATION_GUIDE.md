# Database v2 Migration Guide

## Overview

This guide explains how to extend your existing FastAPI backend, MQTT subscriber, and SQLite database to support the new v2 schema **without breaking existing functionality**.

## What's New in v2

### New Database Tables
- **pir_readings** - Dedicated table for PIR motion sensor readings
- **ultrasonic_readings** - Dedicated table for ultrasonic distance sensor readings
- **dht22_readings** - Dedicated table for DHT22 temperature/humidity readings
- **wifi_readings** - Dedicated table for WiFi signal strength readings

### Enhanced Tables
- **devices** - Added `id` (INTEGER PRIMARY KEY) and `device_name` fields
- **sensors** - Added `sensor_name` and `device_id_fk` (foreign key to devices.id)

### New MQTT Format Support
The system now supports structured JSON format:
```json
{
  "device_id": "ESP8266_NODE_01",
  "location": "Living_Room",
  "timestamp": 123456789,
  "sensors": {
    "pir": { "motion_detected": true },
    "ultrasonic": { "distance_cm": 123.4 },
    "dht22": { "temperature_c": 25.6, "humidity_percent": 60.2 }
  },
  "wifi": { "rssi": -55 }
}
```

### Backward Compatibility
- ✅ All existing MQTT topics still work
- ✅ All existing API endpoints still work
- ✅ Legacy `sensor_readings` table still receives data
- ✅ Existing code continues to function

## Step-by-Step Migration

### Step 1: Backup Your Database

```bash
# On Raspberry Pi
cd ~/ai-driven-fall-detection/raspberry-pi-backend
cp fall_detection.db fall_detection.db.backup
```

### Step 2: Add New Files

Copy the new files to your backend:

1. **`database/database_v2.py`** - Extended database functions
2. **`api/mqtt_handler_v2.py`** - Extended MQTT handler
3. **`api/routes_v2.py`** - New API routes

### Step 3: Update Your Main API File

Add this to `api/main.py` at the top (after imports):

```python
# Import v2 modules
from database.database_v2 import migrate_database_to_v2
from api.mqtt_handler_v2 import handle_mqtt_message_v2
from api.routes_v2 import router as v2_router

# Add v2 routes to app
app.include_router(v2_router, prefix="/api/v2", tags=["v2"])
```

Update the `lifespan` function to run migration:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing Fall Detection System...")
    
    # Initialize database (existing)
    await init_database()
    
    # Run v2 migration (NEW)
    try:
        await migrate_database_to_v2()
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")
        # Continue even if migration has issues
    
    # ... rest of existing startup code ...
```

### Step 4: Update MQTT Handler (Optional)

You have two options:

**Option A: Use v2 handler for all messages (recommended)**
```python
# In api/main.py, replace handle_mqtt_message with:
mqtt_client.set_message_handler(handle_mqtt_message_v2)
```

**Option B: Keep existing handler, add v2 handler for specific topics**
```python
# In api/main.py, modify handle_mqtt_message to check format:
async def handle_mqtt_message(topic: str, payload: dict):
    # Check if it's v2 format
    if isinstance(payload, dict) and "sensors" in payload:
        await handle_mqtt_message_v2(topic, payload, broadcast_to_websockets)
    else:
        # Use existing handler
        # ... existing code ...
```

### Step 5: Restart Backend

```bash
# Stop existing backend
# Then restart
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python api/main.py
```

## New API Endpoints

### Get All Devices with Sensors
```bash
GET /api/v2/devices
```

Response:
```json
{
  "devices": [
    {
      "id": 1,
      "device_id": "ESP8266_NODE_01",
      "device_name": "ESP8266_NODE_01",
      "location": "Living_Room",
      "status": "online",
      "sensors": [
        {
          "id": 1,
          "sensor_type": "pir",
          "sensor_name": "PIR Motion Sensor",
          "latest_reading": {
            "motion_detected": 1,
            "timestamp": 123456789
          }
        }
      ]
    }
  ],
  "count": 1
}
```

### Get Specific Device
```bash
GET /api/v2/devices/{device_id}
```

### Get Latest Reading for Sensor
```bash
GET /api/v2/sensor/{sensor_id}/latest-reading
```

### Get Sensor-Specific Readings
```bash
GET /api/v2/readings/pir?sensor_id=1&limit=100
GET /api/v2/readings/ultrasonic?sensor_id=2&limit=100
GET /api/v2/readings/dht22?sensor_id=3&limit=100
GET /api/v2/readings/wifi?sensor_id=4&limit=100
```

## MQTT Message Format

### New v2 Format (Recommended)
```json
{
  "device_id": "ESP8266_NODE_01",
  "device_name": "Living Room Sensor",
  "location": "Living_Room",
  "timestamp": 123456789,
  "sensors": {
    "pir": { "motion_detected": true },
    "ultrasonic": { "distance_cm": 123.4 },
    "dht22": { "temperature_c": 25.6, "humidity_percent": 60.2 }
  },
  "wifi": { "rssi": -55 }
}
```

**MQTT Topic:** `sensors/v2/ESP8266_NODE_01` (or any topic you prefer)

### Legacy Format (Still Supported)
```
Topic: sensors/pir/ESP8266_NODE_01
Payload: 1
```

## WebSocket Messages

### v2 Format Message
```json
{
  "type": "sensor_data_v2",
  "device_id": "ESP8266_NODE_01",
  "device_name": "Living Room Sensor",
  "location": "Living_Room",
  "timestamp": 123456789,
  "readings": [
    {
      "sensor_type": "pir",
      "reading_id": 1,
      "data": { "motion_detected": true }
    }
  ]
}
```

### Legacy Format (Still Sent)
```json
{
  "type": "sensor_pir",
  "sensor_type": "pir",
  "device_id": "ESP8266_NODE_01",
  "timestamp": 123456789,
  "data": { "motion_detected": true }
}
```

## Database Schema

### devices Table (Updated)
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- NEW
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT,                       -- NEW
    device_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### sensors Table (Updated)
```sql
CREATE TABLE sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    sensor_name TEXT,                      -- NEW
    device_id_fk INTEGER,                  -- NEW (foreign key to devices.id)
    status TEXT DEFAULT 'active',
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    total_readings INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_id, sensor_type)
)
```

### New Reading Tables
```sql
-- PIR readings
CREATE TABLE pir_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    motion_detected INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- Ultrasonic readings
CREATE TABLE ultrasonic_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    distance_cm REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- DHT22 readings
CREATE TABLE dht22_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    temperature_c REAL NOT NULL,
    humidity_percent REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- WiFi readings
CREATE TABLE wifi_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    rssi INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);
```

## Verification

### Check Migration Success
```bash
sqlite3 fall_detection.db ".tables"
```

You should see:
- `devices` (updated)
- `sensors` (updated)
- `sensor_readings` (existing, still works)
- `pir_readings` (new)
- `ultrasonic_readings` (new)
- `dht22_readings` (new)
- `wifi_readings` (new)

### Test New API Endpoints
```bash
curl http://localhost:8000/api/v2/devices
curl http://localhost:8000/api/v2/devices/ESP8266_NODE_01
curl http://localhost:8000/api/v2/readings/pir
```

### Test MQTT v2 Format
Publish a test message:
```bash
mosquitto_pub -h localhost -t "sensors/v2/test" -m '{
  "device_id": "TEST_DEVICE",
  "location": "Test_Room",
  "timestamp": 123456789,
  "sensors": {
    "pir": { "motion_detected": true },
    "ultrasonic": { "distance_cm": 50.0 },
    "dht22": { "temperature_c": 22.5, "humidity_percent": 45.0 }
  },
  "wifi": { "rssi": -60 }
}'
```

## Troubleshooting

### Migration Errors
If migration fails, check:
1. Database file permissions
2. SQLite version (should be 3.8+)
3. Check logs for specific error messages

### API Not Working
1. Ensure v2 routes are included: `app.include_router(v2_router, prefix="/api/v2")`
2. Check FastAPI logs for errors
3. Verify database migration completed

### MQTT Not Processing v2 Format
1. Ensure `handle_mqtt_message_v2` is being called
2. Check MQTT topic subscriptions
3. Verify JSON format is correct

## Rollback

If you need to rollback:
1. Restore database backup: `cp fall_detection.db.backup fall_detection.db`
2. Remove v2 imports from `api/main.py`
3. Restart backend

## Summary

✅ **Backward Compatible** - All existing code continues to work
✅ **New Features** - Dedicated tables for each sensor type
✅ **Structured Data** - Better organization and querying
✅ **Easy Migration** - Automatic migration on startup
✅ **Dual Support** - Both old and new MQTT formats work

The system now supports both the legacy format and the new v2 format simultaneously!

