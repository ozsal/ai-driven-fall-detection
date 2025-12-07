# Quick Database Check Queries

## Check if there's any data:

```sql
-- Count total readings
SELECT COUNT(*) FROM sensor_readings;

-- Count by sensor type
SELECT sensor_type, COUNT(*) as count 
FROM sensor_readings 
GROUP BY sensor_type;

-- Count by device
SELECT device_id, COUNT(*) as count 
FROM sensor_readings 
GROUP BY device_id;

-- View recent readings (last 10)
SELECT id, device_id, sensor_type, topic, received_at 
FROM sensor_readings 
ORDER BY id DESC 
LIMIT 10;

-- View full details of recent readings
SELECT id, device_id, sensor_type, data, topic, timestamp, received_at 
FROM sensor_readings 
ORDER BY id DESC 
LIMIT 5;

-- Check devices table
SELECT * FROM devices;

-- Check if table exists and structure
.schema sensor_readings
.tables
```

## If COUNT(*) returns 0:

The data is not being stored. Check backend logs for:
- `📨 Received MQTT message` - Messages are being received
- `🔄 Scheduling message handler` - Handler is being called
- `💾 Attempting to store reading` - Storage attempt is happening
- `✅ Inserted reading with ID: X` - Success
- `❌ DATABASE ERROR` - Failure (check error message)

## Quick one-liner to check:

```bash
sqlite3 fall_detection.db "SELECT COUNT(*) FROM sensor_readings;"
```


