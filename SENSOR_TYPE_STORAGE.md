# Sensor Type Storage in Database

## Overview

All sensor types (PIR, Ultrasonic, DHT22) are now properly stored in the database with correct `sensor_type` values, separate from the device type.

## Database Structure

### sensor_readings Table

Stores each sensor reading with its specific sensor type:

```sql
sensor_readings:
- device_id: "ESP8266_NODE_01"  -- Device identifier
- sensor_type: "pir" | "ultrasonic" | "dht22" | "combined"  -- Sensor type
- data: JSON with sensor-specific values
- timestamp: When reading was taken
- topic: MQTT topic the data came from
```

### sensors Table

Tracks each sensor separately:

```sql
sensors:
- device_id: "ESP8266_NODE_01"
- sensor_type: "pir" | "ultrasonic" | "dht22"  -- Specific sensor type
- status: "active" | "inactive"
- total_readings: Count of readings
- last_seen: Last time sensor sent data
```

### devices Table

Tracks devices (not sensors):

```sql
devices:
- device_id: "ESP8266_NODE_01"
- device_type: "esp8266"  -- Device model/type (NOT sensor type)
- status: "active" | "inactive"
- last_seen: Last time device sent any data
```

## Sensor Type Normalization

The system automatically normalizes sensor type names:

| Input | Normalized |
|-------|-----------|
| `pir`, `motion`, `motion_sensor` | `pir` |
| `ultrasonic`, `sr04`, `hc-sr04`, `distance` | `ultrasonic` |
| `dht22`, `dht`, `temperature`, `humidity` | `dht22` |
| `combined` | `combined` |

## How Sensor Types Are Extracted

1. **From MQTT Topic** (Primary method):
   - Topic: `sensors/pir/ESP8266_NODE_01` → `sensor_type = "pir"`
   - Topic: `sensors/ultrasonic/ESP8266_NODE_01` → `sensor_type = "ultrasonic"`
   - Topic: `sensors/dht22/ESP8266_NODE_01` → `sensor_type = "dht22"`

2. **From Payload** (Fallback):
   - If payload contains `sensor_type` or `sensorType` field, use that
   - Otherwise, extract from topic

3. **Normalization**:
   - All sensor types are normalized to standard names
   - Ensures consistency across the database

## Example Data Storage

### PIR Sensor Reading
```json
{
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "pir",
  "data": {"motion_detected": true},
  "topic": "sensors/pir/ESP8266_NODE_01"
}
```

### Ultrasonic Sensor Reading
```json
{
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "ultrasonic",
  "data": {"distance_cm": 25.5},
  "topic": "sensors/ultrasonic/ESP8266_NODE_01"
}
```

### DHT22 Sensor Reading
```json
{
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "dht22",
  "data": {
    "temperature_c": 22.5,
    "humidity_percent": 45.0
  },
  "topic": "sensors/dht22/ESP8266_NODE_01"
}
```

## Querying by Sensor Type

### Get All PIR Readings
```sql
SELECT * FROM sensor_readings WHERE sensor_type = 'pir';
```

### Get All Ultrasonic Readings
```sql
SELECT * FROM sensor_readings WHERE sensor_type = 'ultrasonic';
```

### Get All DHT22 Readings
```sql
SELECT * FROM sensor_readings WHERE sensor_type = 'dht22';
```

### Count by Sensor Type
```sql
SELECT sensor_type, COUNT(*) as count 
FROM sensor_readings 
GROUP BY sensor_type;
```

## API Endpoints

All endpoints properly filter by sensor_type:

- `/api/sensors/pir` - Returns only PIR sensor readings
- `/api/sensors/ultrasonic` - Returns only Ultrasonic sensor readings
- `/api/sensors/dht22` - Returns only DHT22 sensor readings
- `/api/sensor-readings?sensor_type=pir` - Filter by sensor type

## Verification

### Check Database
```bash
# View all sensor types in database
sqlite3 fall_detection.db "
  SELECT DISTINCT sensor_type, COUNT(*) as count 
  FROM sensor_readings 
  GROUP BY sensor_type;
"

# View sensors table
sqlite3 fall_detection.db "SELECT * FROM sensors;"
```

### Expected Results

You should see:
- `sensor_type = "pir"` for PIR motion sensor
- `sensor_type = "ultrasonic"` for ultrasonic distance sensor
- `sensor_type = "dht22"` for DHT22 temperature/humidity sensor

**NOT** `sensor_type = "esp8266"` - that's the device type, not sensor type!

## Summary

✅ **Sensor Types Stored Correctly** - PIR, Ultrasonic, DHT22 stored as separate sensor types
✅ **Device Type Separate** - Device type (esp8266) stored separately from sensor type
✅ **Automatic Normalization** - Sensor type names normalized for consistency
✅ **Topic-Based Extraction** - Sensor type extracted from MQTT topic
✅ **Separate Tracking** - Each sensor tracked separately in sensors table

All sensor types are now properly stored in the database!



