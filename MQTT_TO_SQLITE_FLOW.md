# MQTT to SQLite Data Flow - Complete Guide

## Data Flow Overview

```
ESP8266 Sensor → MQTT Broker → MQTT Client → Message Handler → SQLite Database
                                                      ↓
                                            WebSocket → Frontend
```

## Step-by-Step Process

### 1. MQTT Message Reception (`mqtt_client.py`)

**Location:** `mqtt_broker/mqtt_client.py` - `_on_message()` method

**What happens:**
- MQTT client receives message from broker
- Decodes payload from bytes to string
- Tries to parse as JSON
- Converts to dictionary if needed
- Adds topic and timestamp metadata
- Schedules async message handler

**Logs you'll see:**
```
📨 Received MQTT message on topic: sensors/pir/ESP8266_NODE_01
   Payload: 1...
🔄 Scheduling message handler for topic: sensors/pir/ESP8266_NODE_01
```

### 2. Message Handler Processing (`api/main.py`)

**Location:** `api/main.py` - `handle_mqtt_message()` function

**What happens:**
- Extracts device_id from topic or payload
- Extracts sensor_type from topic
- Extracts location from payload
- Processes sensor data (handles primitives like "1" or "25.5")
- Prepares database record
- Calls database insertion

**Logs you'll see:**
```
💾 Attempting to store reading: device_id=ESP8266_NODE_01, sensor_type=pir, topic=sensors/pir/ESP8266_NODE_01
   📝 Inserting: device_id=ESP8266_NODE_01, sensor_type=pir, timestamp=1234567890
   📝 Data JSON length: 45 bytes
```

### 3. Database Storage (`database/sqlite_db.py`)

**Location:** `database/sqlite_db.py` - `insert_sensor_reading()` function

**What happens:**
- Ensures database file exists (creates if needed)
- Opens database connection
- Serializes sensor data to JSON
- Inserts into `sensor_readings` table
- Commits transaction
- Verifies insertion succeeded
- Updates `devices` table
- Closes connection

**Logs you'll see:**
```
   ✅ Inserted reading with ID: 1
   ✅ Verified: Reading 1 exists in database
   ✅ Updated device: ESP8266_NODE_01
✅ SUCCESS: Stored sensor reading #1 from ESP8266_NODE_01 (pir)...
   Device ID: ESP8266_NODE_01, Sensor Type: pir, Location: None
   Data: {'motion_detected': True}
✅ Message handler completed for topic: sensors/pir/ESP8266_NODE_01
```

## Database Schema

### sensor_readings Table
```sql
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    data TEXT NOT NULL,  -- JSON string
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    topic TEXT
)
```

### devices Table
```sql
CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    device_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Troubleshooting

### No Data in Database

**Check 1: MQTT Connection**
```bash
# Look for in backend logs:
✓ MQTT client connected successfully
✓ Subscribed to: sensors/pir/+
```

**Check 2: Messages Being Received**
```bash
# Look for in backend logs:
📨 Received MQTT message on topic: sensors/...
```

**Check 3: Handler Being Called**
```bash
# Look for in backend logs:
🔄 Scheduling message handler for topic: sensors/...
```

**Check 4: Storage Attempt**
```bash
# Look for in backend logs:
💾 Attempting to store reading: device_id=...
```

**Check 5: Storage Success**
```bash
# Look for in backend logs:
✅ Inserted reading with ID: X
✅ Verified: Reading X exists in database
```

### Common Issues

1. **No "📨 Received" messages**
   - MQTT not connected
   - ESP8266 not publishing
   - Wrong topic subscription

2. **"📨 Received" but no "🔄 Scheduling"**
   - Message handler not set
   - Event loop not available

3. **"🔄 Scheduling" but no "💾 Attempting"**
   - Handler not executing
   - Exception in handler (check logs)

4. **"💾 Attempting" but no "✅ Inserted"**
   - Database error (check logs for details)
   - Database file permissions
   - Disk space

5. **"✅ Inserted" but data not in database**
   - Transaction not committed
   - Database connection issue
   - Wrong database file being queried

## Verification

### Check Database
```bash
sqlite3 fall_detection.db "SELECT COUNT(*) FROM sensor_readings;"
sqlite3 fall_detection.db "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 5;"
```

### Check via API
```bash
curl http://10.162.131.191:8000/api/sensor-readings?limit=5
curl http://10.162.131.191:8000/api/debug/database
```

### Check Devices
```bash
sqlite3 fall_detection.db "SELECT * FROM devices;"
curl http://10.162.131.191:8000/api/devices
```

## Recent Fixes Applied

1. **Removed timeout** on message handler to allow database operations to complete
2. **Added verification step** after database insert to confirm data was saved
3. **Improved connection management** for database operations
4. **Added completion callbacks** to log handler success/failure
5. **Enhanced error logging** throughout the flow

## Expected Behavior

When ESP8266 sends data:
1. ✅ MQTT message received
2. ✅ Handler scheduled
3. ✅ Data processed
4. ✅ Database insert attempted
5. ✅ Insert verified
6. ✅ Device updated
7. ✅ Success logged
8. ✅ Data visible in database


