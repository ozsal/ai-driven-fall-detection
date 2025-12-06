# MQTT to SQLite Data Retrieval - Complete Setup

## ✅ System is Configured

The system is now fully configured to:
1. **Receive** MQTT messages from ESP8266 sensors
2. **Process** the messages and extract sensor data
3. **Store** the data in SQLite database
4. **Update** device information automatically

## Data Flow

```
ESP8266 → MQTT Broker → Backend MQTT Client → Message Handler → SQLite Database
                                                      ↓
                                            WebSocket → Frontend (Real-time)
```

## How It Works

### 1. MQTT Connection (`mqtt_broker/mqtt_client.py`)

- Connects to MQTT broker (supports with/without authentication)
- Subscribes to sensor topics:
  - `sensors/pir/+` - Motion sensor data
  - `sensors/ultrasonic/+` - Distance sensor data
  - `sensors/dht22/+` - Temperature/humidity data
  - `sensors/combined/+` - Combined sensor readings
- Receives messages and schedules handler

### 2. Message Processing (`api/main.py` - `handle_mqtt_message()`)

- Extracts device_id from topic (e.g., `sensors/pir/ESP8266_NODE_01` → `ESP8266_NODE_01`)
- Extracts sensor_type from topic (e.g., `sensors/pir/...` → `pir`)
- Processes payload:
  - JSON payloads: Parses and extracts data
  - Primitive payloads (like "1" or "25.5"): Converts to structured data
- Prepares database record

### 3. Database Storage (`database/sqlite_db.py` - `insert_sensor_reading()`)

- Ensures database exists (creates if needed)
- Inserts into `sensor_readings` table:
  - device_id
  - sensor_type
  - timestamp
  - data (JSON string)
  - location
  - topic
- Verifies insertion succeeded
- Updates `devices` table with latest device info

## Verification Steps

### Step 1: Check MQTT Connection

When backend starts, you should see:
```
✓ MQTT client connected successfully
  Broker: 10.162.131.191:8883
  Subscribing to topics:
    ✓ Subscribed to: sensors/pir/+
    ✓ Subscribed to: sensors/ultrasonic/+
    ...
```

### Step 2: Check Messages Being Received

When ESP8266 sends data, you should see:
```
📨 Received MQTT message on topic: sensors/pir/ESP8266_NODE_01
   Payload: 1...
🔄 Scheduling message handler for topic: sensors/pir/ESP8266_NODE_01
```

### Step 3: Check Data Storage

You should see:
```
💾 Attempting to store reading: device_id=ESP8266_NODE_01, sensor_type=pir, topic=sensors/pir/ESP8266_NODE_01
   📝 Inserting: device_id=ESP8266_NODE_01, sensor_type=pir, timestamp=1234567890
   📝 Data JSON length: 45 bytes
   ✅ Inserted reading with ID: 1
   ✅ Verified: Reading 1 exists in database
   ✅ Updated device: ESP8266_NODE_01
✅ SUCCESS: Stored sensor reading #1 from ESP8266_NODE_01 (pir)...
✅ Message handler completed for topic: sensors/pir/ESP8266_NODE_01
```

### Step 4: Verify in Database

```bash
# Count readings
sqlite3 fall_detection.db "SELECT COUNT(*) FROM sensor_readings;"

# View recent readings
sqlite3 fall_detection.db "SELECT id, device_id, sensor_type, topic, received_at FROM sensor_readings ORDER BY id DESC LIMIT 10;"

# View devices
sqlite3 fall_detection.db "SELECT * FROM devices;"
```

### Step 5: Verify via API

```bash
# Get sensor readings
curl http://10.162.131.191:8000/api/sensor-readings?limit=5

# Get devices
curl http://10.162.131.191:8000/api/devices

# Debug endpoint
curl http://10.162.131.191:8000/api/debug/database
```

## Database Schema

### sensor_readings Table
Stores all sensor data:
- `id` - Auto-increment primary key
- `device_id` - Device identifier (e.g., "ESP8266_NODE_01")
- `sensor_type` - Type of sensor (e.g., "pir", "ultrasonic", "dht22", "combined")
- `timestamp` - Unix timestamp of reading
- `data` - JSON string with sensor values
- `received_at` - When message was received by backend
- `location` - Device location (if provided)
- `topic` - MQTT topic the message came from

### devices Table
Tracks all devices:
- `device_id` - Device identifier (primary key)
- `device_type` - Type of device/sensor
- `status` - Device status (active/inactive)
- `last_seen` - Last time device sent data
- `location` - Device location

## Troubleshooting

### No Data in Database

1. **Check MQTT connection:**
   - Look for "✓ MQTT client connected successfully" in logs
   - Verify broker is running and accessible

2. **Check messages being received:**
   - Look for "📨 Received MQTT message" in logs
   - Verify ESP8266 is publishing to correct topics

3. **Check handler execution:**
   - Look for "🔄 Scheduling message handler" in logs
   - Look for "💾 Attempting to store reading" in logs

4. **Check database errors:**
   - Look for "❌ DATABASE ERROR" or "❌ CRITICAL ERROR" in logs
   - Check database file permissions
   - Check disk space

### Common Issues

**Issue:** "⚠️ Warning: No message handler set"
- **Fix:** Message handler is set in `lifespan()` function. Ensure backend started properly.

**Issue:** "⚠️ Warning: Event loop not available"
- **Fix:** This shouldn't happen if backend started correctly. Restart backend.

**Issue:** Database insert fails
- **Fix:** Check database file permissions, disk space, and error logs

## Configuration

### MQTT Settings (Environment Variables)

Create `.env` file in `raspberry-pi-backend/`:
```env
MQTT_BROKER_HOST=10.162.131.191
MQTT_BROKER_PORT=8883
MQTT_USERNAME=  # Leave empty for no auth
MQTT_PASSWORD=  # Leave empty for no auth
```

Or set defaults in code (already configured).

### Database Location

Database file: `raspberry-pi-backend/fall_detection.db`

Automatically created on first run if it doesn't exist.

## Summary

✅ **MQTT Client** - Receives messages from broker
✅ **Message Handler** - Processes and extracts data
✅ **Database Storage** - Saves to SQLite with verification
✅ **Device Tracking** - Updates device information
✅ **Error Handling** - Comprehensive logging and error handling
✅ **Verification** - Confirms data was saved

The system is ready to receive and store MQTT data from ESP8266 sensors!

