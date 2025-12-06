# Separate Sensor Data Handling Guide

## Overview

The system is configured to receive, store, and display data from **3 separate sensors**:
1. **PIR Motion Sensor** - Detects motion
2. **DHT22 Temperature/Humidity Sensor** - Measures temperature and humidity
3. **Ultrasonic Distance Sensor** - Measures distance

Each sensor's data is:
- ✅ Published to **separate MQTT topics**
- ✅ Stored **separately in the database** by sensor type
- ✅ Sent to the **frontend separately** via WebSocket
- ✅ Can be **queried separately** via API

## MQTT Topics

ESP8266 publishes to these topics:

| Sensor | Topic Format | Example | Payload Format |
|--------|-------------|---------|----------------|
| PIR | `sensors/pir/{device_id}` | `sensors/pir/ESP8266_NODE_01` | `"1"` or `"0"` (motion detected) |
| Ultrasonic | `sensors/ultrasonic/{device_id}` | `sensors/ultrasonic/ESP8266_NODE_01` | `"25.5"` (distance in cm) |
| DHT22 | `sensors/dht22/{device_id}` | `sensors/dht22/ESP8266_NODE_01` | JSON: `{"temperature_c": 22.5, "humidity_percent": 45.0}` |
| Combined | `sensors/combined/{device_id}` | `sensors/combined/ESP8266_NODE_01` | JSON: All sensors together |

## Database Storage

### sensor_readings Table

Each sensor reading is stored as a **separate row** with:
- `sensor_type` - Identifies which sensor: `"pir"`, `"ultrasonic"`, `"dht22"`, or `"combined"`
- `device_id` - Device identifier (e.g., `"ESP8266_NODE_01"`)
- `data` - JSON string with sensor-specific values

### Example Database Records

**PIR Sensor Reading:**
```json
{
  "id": 1,
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "pir",
  "timestamp": 1234567890,
  "data": {"motion_detected": true},
  "topic": "sensors/pir/ESP8266_NODE_01"
}
```

**Ultrasonic Sensor Reading:**
```json
{
  "id": 2,
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "ultrasonic",
  "timestamp": 1234567891,
  "data": {"distance_cm": 25.5},
  "topic": "sensors/ultrasonic/ESP8266_NODE_01"
}
```

**DHT22 Sensor Reading:**
```json
{
  "id": 3,
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "dht22",
  "timestamp": 1234567892,
  "data": {"temperature_c": 22.5, "humidity_percent": 45.0},
  "topic": "sensors/dht22/ESP8266_NODE_01"
}
```

## API Endpoints

### Get All Sensor Readings
```bash
GET /api/sensor-readings?limit=100
```
Returns all sensor types mixed together.

### Get Specific Sensor Type
```bash
# Get only PIR sensor readings
GET /api/sensor-readings?sensor_type=pir&limit=50

# Get only Ultrasonic sensor readings
GET /api/sensor-readings?sensor_type=ultrasonic&limit=50

# Get only DHT22 sensor readings
GET /api/sensor-readings?sensor_type=dht22&limit=50
```

### Get Readings from Specific Device
```bash
GET /api/sensor-readings?device_id=ESP8266_NODE_01&limit=100
```

### Get Specific Sensor from Specific Device
```bash
GET /api/sensor-readings?device_id=ESP8266_NODE_01&sensor_type=pir&limit=50
```

## Frontend Data Flow

### WebSocket Messages

When a sensor reading is received, the backend broadcasts via WebSocket:

```json
{
  "type": "sensor_data",
  "topic": "sensors/pir/ESP8266_NODE_01",
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "pir",
  "timestamp": 1234567890,
  "data": {"motion_detected": true},
  "location": null
}
```

The frontend can filter by `sensor_type` to display each sensor separately.

### Frontend Display

The frontend should:
1. **Receive WebSocket messages** for all sensors
2. **Filter by sensor_type** to separate:
   - PIR motion data
   - Ultrasonic distance data
   - DHT22 temperature/humidity data
3. **Display each sensor** in its own component/card
4. **Update in real-time** as new data arrives

## Data Processing Flow

### 1. ESP8266 Publishing

```cpp
// PIR Sensor
client.publish("sensors/pir/ESP8266_NODE_01", "1");  // Motion detected

// Ultrasonic Sensor
client.publish("sensors/ultrasonic/ESP8266_NODE_01", "25.5");  // 25.5 cm

// DHT22 Sensor
client.publish("sensors/dht22/ESP8266_NODE_01", 
  "{\"temperature_c\":22.5,\"humidity_percent\":45.0}");
```

### 2. Backend Processing

For each message:
1. **Extract sensor_type** from topic (`sensors/pir/...` → `pir`)
2. **Extract device_id** from topic (`.../ESP8266_NODE_01` → `ESP8266_NODE_01`)
3. **Process payload** based on sensor type:
   - PIR: `"1"` → `{"motion_detected": true}`
   - Ultrasonic: `"25.5"` → `{"distance_cm": 25.5}`
   - DHT22: JSON → Parse and use as-is
4. **Store in database** with `sensor_type` field
5. **Broadcast via WebSocket** with `sensor_type` included

### 3. Database Storage

Each sensor reading is stored as a separate row:
```sql
INSERT INTO sensor_readings 
  (device_id, sensor_type, timestamp, data, topic)
VALUES 
  ('ESP8266_NODE_01', 'pir', 1234567890, '{"motion_detected":true}', 'sensors/pir/ESP8266_NODE_01');
```

### 4. Frontend Display

Frontend receives WebSocket messages and can:
- Filter by `sensor_type` to show each sensor separately
- Group by `device_id` to show all sensors from one device
- Display real-time updates for each sensor type

## Query Examples

### Get Latest Reading from Each Sensor Type

```sql
-- Latest PIR reading
SELECT * FROM sensor_readings 
WHERE sensor_type = 'pir' 
ORDER BY id DESC LIMIT 1;

-- Latest Ultrasonic reading
SELECT * FROM sensor_readings 
WHERE sensor_type = 'ultrasonic' 
ORDER BY id DESC LIMIT 1;

-- Latest DHT22 reading
SELECT * FROM sensor_readings 
WHERE sensor_type = 'dht22' 
ORDER BY id DESC LIMIT 1;
```

### Count Readings by Sensor Type

```sql
SELECT sensor_type, COUNT(*) as count 
FROM sensor_readings 
GROUP BY sensor_type;
```

### Get All Sensors from One Device

```sql
SELECT sensor_type, data, timestamp 
FROM sensor_readings 
WHERE device_id = 'ESP8266_NODE_01' 
ORDER BY timestamp DESC;
```

## Verification

### Check MQTT Subscriptions

Backend logs should show:
```
✓ Subscribed to: sensors/pir/+
✓ Subscribed to: sensors/ultrasonic/+
✓ Subscribed to: sensors/dht22/+
✓ Subscribed to: sensors/combined/+
```

### Check Data Storage

```bash
# Count by sensor type
sqlite3 fall_detection.db "
  SELECT sensor_type, COUNT(*) as count 
  FROM sensor_readings 
  GROUP BY sensor_type;
"

# View recent readings by type
sqlite3 fall_detection.db "
  SELECT sensor_type, device_id, data, received_at 
  FROM sensor_readings 
  ORDER BY id DESC 
  LIMIT 10;
"
```

### Check API

```bash
# Get all readings
curl http://10.162.131.191:8000/api/sensor-readings?limit=10

# Get only PIR readings
curl http://10.162.131.191:8000/api/sensor-readings?sensor_type=pir&limit=5

# Get only Ultrasonic readings
curl http://10.162.131.191:8000/api/sensor-readings?sensor_type=ultrasonic&limit=5

# Get only DHT22 readings
curl http://10.162.131.191:8000/api/sensor-readings?sensor_type=dht22&limit=5
```

## Summary

✅ **Separate MQTT Topics** - Each sensor publishes to its own topic
✅ **Separate Database Storage** - Each sensor reading stored with `sensor_type` field
✅ **Separate API Queries** - Can filter by `sensor_type` parameter
✅ **Separate WebSocket Messages** - Each message includes `sensor_type` for filtering
✅ **Real-time Updates** - Frontend receives separate updates for each sensor

The system is fully configured to handle all 3 sensors separately!

