# Sensor Status Tracking Guide

## Overview

Each sensor (PIR, Ultrasonic, DHT22) is now tracked **separately** in the database with its own **active status**. This allows you to monitor the health and activity of each individual sensor.

## Database Schema

### sensors Table

New table created to track each sensor separately:

```sql
CREATE TABLE sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    sensor_type TEXT NOT NULL,  -- 'pir', 'ultrasonic', 'dht22'
    status TEXT DEFAULT 'active',  -- 'active' or 'inactive'
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    total_readings INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(device_id, sensor_type)
)
```

**Key Features:**
- Each sensor is uniquely identified by `(device_id, sensor_type)`
- Status is automatically updated when data is received
- Tracks total number of readings per sensor
- Records last time sensor sent data

## Active Status Logic

A sensor is considered **active** if:
- Data was received in the **last 5 minutes**

A sensor is considered **inactive** if:
- No data received in the last 5 minutes

Status is automatically calculated when querying sensors.

## API Endpoints

### Get All Sensors

**Endpoint:** `GET /api/sensors`

**Query Parameters:**
- `sensor_type` (optional) - Filter by sensor type: `pir`, `ultrasonic`, `dht22`
- `device_id` (optional) - Filter by device ID

**Example:**
```bash
# Get all sensors
curl http://10.162.131.191:8000/api/sensors

# Get all PIR sensors
curl http://10.162.131.191:8000/api/sensors?sensor_type=pir

# Get all sensors from a device
curl http://10.162.131.191:8000/api/sensors?device_id=ESP8266_NODE_01
```

**Response:**
```json
[
  {
    "id": 1,
    "device_id": "ESP8266_NODE_01",
    "sensor_type": "pir",
    "status": "active",
    "last_seen": "2024-12-06 18:30:00",
    "location": null,
    "total_readings": 150,
    "created_at": "2024-12-06 10:00:00"
  },
  {
    "id": 2,
    "device_id": "ESP8266_NODE_01",
    "sensor_type": "ultrasonic",
    "status": "active",
    "last_seen": "2024-12-06 18:30:01",
    "location": null,
    "total_readings": 150,
    "created_at": "2024-12-06 10:00:00"
  },
  {
    "id": 3,
    "device_id": "ESP8266_NODE_01",
    "sensor_type": "dht22",
    "status": "active",
    "last_seen": "2024-12-06 18:30:02",
    "location": null,
    "total_readings": 150,
    "created_at": "2024-12-06 10:00:00"
  }
]
```

### Get PIR Sensors Status

**Endpoint:** `GET /api/sensors/pir/status`

**Example:**
```bash
curl http://10.162.131.191:8000/api/sensors/pir/status
```

### Get Ultrasonic Sensors Status

**Endpoint:** `GET /api/sensors/ultrasonic/status`

**Example:**
```bash
curl http://10.162.131.191:8000/api/sensors/ultrasonic/status
```

### Get DHT22 Sensors Status

**Endpoint:** `GET /api/sensors/dht22/status`

**Example:**
```bash
curl http://10.162.131.191:8000/api/sensors/dht22/status
```

### Update Sensor Status Manually

**Endpoint:** `PUT /api/sensors/{device_id}/{sensor_type}/status`

**Body:**
```json
{
  "status": "active"  // or "inactive"
}
```

**Example:**
```bash
curl -X PUT http://10.162.131.191:8000/api/sensors/ESP8266_NODE_01/pir/status \
  -H "Content-Type: application/json" \
  -d '{"status": "inactive"}'
```

## Automatic Status Updates

When a sensor reading is received:

1. **Sensor reading** is inserted into `sensor_readings` table
2. **Sensor record** is created/updated in `sensors` table:
   - `status` set to `'active'`
   - `last_seen` updated to current timestamp
   - `total_readings` incremented
   - `location` updated if provided

## Database Queries

### View All Sensors

```sql
SELECT * FROM sensors ORDER BY last_seen DESC;
```

### View Active Sensors Only

```sql
SELECT * FROM sensors 
WHERE last_seen >= datetime('now', '-5 minutes')
ORDER BY sensor_type, device_id;
```

### View Inactive Sensors

```sql
SELECT * FROM sensors 
WHERE last_seen < datetime('now', '-5 minutes')
ORDER BY sensor_type, device_id;
```

### Count Sensors by Type

```sql
SELECT sensor_type, COUNT(*) as count,
       SUM(CASE WHEN last_seen >= datetime('now', '-5 minutes') THEN 1 ELSE 0 END) as active_count
FROM sensors
GROUP BY sensor_type;
```

### Get Sensor Statistics

```sql
SELECT 
    device_id,
    sensor_type,
    status,
    total_readings,
    last_seen,
    CASE 
        WHEN last_seen >= datetime('now', '-5 minutes') THEN 'active'
        ELSE 'inactive'
    END as calculated_status
FROM sensors
ORDER BY device_id, sensor_type;
```

## Frontend Integration

### Display Sensor Status

```javascript
// Fetch sensor status
async function fetchSensorStatus() {
  const response = await fetch('http://10.162.131.191:8000/api/sensors');
  const sensors = await response.json();
  
  // Group by sensor type
  const pirSensors = sensors.filter(s => s.sensor_type === 'pir');
  const ultrasonicSensors = sensors.filter(s => s.sensor_type === 'ultrasonic');
  const dht22Sensors = sensors.filter(s => s.sensor_type === 'dht22');
  
  return { pirSensors, ultrasonicSensors, dht22Sensors };
}

// Display status
function SensorStatusCard({ sensor }) {
  const statusColor = sensor.status === 'active' ? 'green' : 'red';
  return (
    <div>
      <h3>{sensor.device_id} - {sensor.sensor_type}</h3>
      <p>Status: <span style={{color: statusColor}}>{sensor.status}</span></p>
      <p>Last Seen: {sensor.last_seen}</p>
      <p>Total Readings: {sensor.total_readings}</p>
    </div>
  );
}
```

### Real-time Status Updates

When new sensor data arrives via WebSocket, the frontend can:
1. Update the sensor's `last_seen` timestamp
2. Set status to `active`
3. Increment `total_readings` counter
4. Update the UI accordingly

## Migration

For existing databases, the `sensors` table will be automatically created when:
- Backend starts and calls `init_database()`
- First sensor reading is inserted

Existing sensor readings will not automatically create sensor records, but new readings will.

## Summary

✅ **Separate Tracking** - Each sensor tracked independently
✅ **Active Status** - Automatically calculated based on recent data
✅ **Total Readings** - Count of readings per sensor
✅ **API Endpoints** - Easy access to sensor status
✅ **Real-time Updates** - Status updated when data received
✅ **Manual Override** - Can manually set sensor status

Each sensor (PIR, Ultrasonic, DHT22) now has its own active status in the database!



