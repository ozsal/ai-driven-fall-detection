# New Database Schema - Devices and Sensor Readings

## Overview

The database has been restructured to have:
1. **devices** table - Stores device names (PIR, Ultrasonic, Temperature & Humidity) with status
2. **sensor_readings** table - Stores readings with device ID, data, status, and user information

## Devices Table

### Schema
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name TEXT NOT NULL UNIQUE,  -- "PIR", "Ultrasonic", "Temperature & Humidity"
    device_type TEXT NOT NULL,          -- "motion_sensor", "distance_sensor", "environmental_sensor"
    status TEXT DEFAULT 'offline',      -- "online" or "offline"
    last_seen TIMESTAMP,                 -- Last time device sent data
    location TEXT,                       -- Device location
    description TEXT,                    -- Device description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Default Devices

The following devices are automatically created:
1. **PIR** - Motion Sensor
2. **Ultrasonic** - Distance Sensor (HC-SR04)
3. **Temperature & Humidity** - DHT22 Sensor

### Status Logic

- **online**: Data received in last 5 minutes
- **offline**: No data received in last 5 minutes

## Sensor Readings Table

### Schema
```sql
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,         -- Foreign key to devices.id
    device_name TEXT NOT NULL,          -- "PIR", "Ultrasonic", "Temperature & Humidity"
    sensor_type TEXT NOT NULL,          -- "pir", "ultrasonic", "dht22"
    reading_data TEXT NOT NULL,         -- JSON string with sensor data
    status TEXT DEFAULT 'active',        -- Reading status
    user_id TEXT,                       -- User who created/owns this reading
    user_role TEXT,                     -- User role (admin, viewer, editor)
    user_permissions TEXT,              -- JSON array of permissions
    timestamp INTEGER NOT NULL,         -- When reading was taken
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,                      -- Reading location
    topic TEXT,                         -- MQTT topic
    FOREIGN KEY (device_id) REFERENCES devices(id)
)
```

### Fields Explained

- **device_id**: References the device in the devices table
- **device_name**: Human-readable device name
- **sensor_type**: Type of sensor (pir, ultrasonic, dht22)
- **reading_data**: JSON string containing actual sensor values
- **status**: Status of the reading (active, inactive)
- **user_id**: ID of user associated with reading
- **user_role**: Role of user (admin, editor, viewer)
- **user_permissions**: JSON array of permissions (["read"], ["read", "write"], etc.)

## Example Data

### Devices Table
```sql
id | device_name           | device_type          | status  | last_seen
1  | PIR                   | motion_sensor        | online  | 2024-12-06 18:30:00
2  | Ultrasonic            | distance_sensor      | online  | 2024-12-06 18:30:01
3  | Temperature & Humidity| environmental_sensor | online  | 2024-12-06 18:30:02
```

### Sensor Readings Table
```sql
id | device_id | device_name | sensor_type | reading_data                    | status | user_id | user_role
1  | 1         | PIR          | pir         | {"motion_detected": true}      | active | user1   | viewer
2  | 2         | Ultrasonic   | ultrasonic  | {"distance_cm": 25.5}          | active | user1   | viewer
3  | 3         | Temperature & Humidity | dht22 | {"temperature_c": 22.5, "humidity_percent": 45.0} | active | user1 | viewer
```

## API Endpoints

### Get All Devices
```bash
GET /api/devices
```

Returns:
```json
[
  {
    "id": 1,
    "device_name": "PIR",
    "device_type": "motion_sensor",
    "status": "online",
    "last_seen": "2024-12-06 18:30:00",
    "description": "PIR Motion Sensor"
  }
]
```

### Get Sensor Readings
```bash
GET /api/sensor-readings?device_name=PIR
GET /api/sensor-readings?device_id=1
GET /api/sensor-readings?sensor_type=pir
```

Returns:
```json
[
  {
    "id": 1,
    "device_id": 1,
    "device_name": "PIR",
    "sensor_type": "pir",
    "reading_data": {"motion_detected": true},
    "status": "active",
    "user_id": "user1",
    "user_role": "viewer",
    "user_permissions": ["read"],
    "timestamp": 1234567890,
    "received_at": "2024-12-06 18:30:00"
  }
]
```

## User Roles and Permissions

### Default Roles
- **admin**: Full access (read, write, delete)
- **editor**: Can read and write
- **viewer**: Can only read

### Permissions
- **read**: Can view sensor readings
- **write**: Can create/update sensor readings
- **delete**: Can delete sensor readings

### Setting User Information

When inserting sensor readings, you can specify:
```python
{
    "user_id": "user123",
    "user_role": "editor",
    "user_permissions": ["read", "write"]
}
```

## Database Queries

### Get All Devices with Status
```sql
SELECT * FROM devices ORDER BY device_name;
```

### Get Online Devices
```sql
SELECT * FROM devices 
WHERE status = 'online' 
ORDER BY device_name;
```

### Get Readings by Device
```sql
SELECT * FROM sensor_readings 
WHERE device_name = 'PIR' 
ORDER BY id DESC;
```

### Get Readings with User Info
```sql
SELECT 
    sr.*,
    d.device_name,
    d.status as device_status
FROM sensor_readings sr
JOIN devices d ON sr.device_id = d.id
WHERE sr.user_id = 'user1'
ORDER BY sr.id DESC;
```

## Migration Notes

- Existing `sensor_readings` table will be migrated
- Device names are automatically mapped:
  - `pir` → "PIR"
  - `ultrasonic` → "Ultrasonic"
  - `dht22` → "Temperature & Humidity"
- Old `device_id` (string) is kept in sensors table for backward compatibility
- New `device_id` (integer) references devices table

## Summary

✅ **Devices Table** - Stores device names (PIR, Ultrasonic, Temperature & Humidity) with online/offline status
✅ **Sensor Readings Table** - Stores readings with device ID, data, status, and user information
✅ **User Support** - Tracks user_id, role, and permissions for each reading
✅ **Status Tracking** - Devices show online/offline based on recent data
✅ **Backward Compatible** - Old code still works with sensors table

