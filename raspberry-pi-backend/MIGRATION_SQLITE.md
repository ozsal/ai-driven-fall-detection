# Migration from MongoDB to SQLite3

This document describes the migration from MongoDB to SQLite3 for the Fall Detection System.

## Changes Made

### 1. Database Module
- **Removed**: `database/mongodb.py`
- **Added**: `database/sqlite_db.py`
- Uses `aiosqlite` for async SQLite operations

### 2. Dependencies
- **Removed**: `pymongo==4.6.0`
- **Added**: `aiosqlite==0.19.0`
- SQLite3 is built into Python, no system installation needed

### 3. Configuration
- **Removed**: `MONGODB_URI`, `MONGODB_DB_NAME`
- **Added**: `DB_DIR`, `DB_NAME`
- Database file location: `{DB_DIR}/{DB_NAME}` (default: `./fall_detection.db`)

### 4. API Changes
All database operations now use SQLite functions:
- `insert_sensor_reading()` - Insert sensor data
- `insert_fall_event()` - Insert fall event (returns event_id)
- `get_sensor_readings()` - Query sensor readings
- `get_fall_events()` - Query fall events
- `get_fall_event()` - Get single event by event_id
- `acknowledge_fall_event()` - Acknowledge event
- `get_devices()` - Get device list
- `get_recent_room_sensor_data()` - Get recent sensor data
- `count_fall_events()` - Count events
- `count_sensor_readings()` - Count readings
- `count_active_devices()` - Count active devices
- `insert_alert_log()` - Log alert status

### 5. Database Schema

#### sensor_readings
- id (INTEGER PRIMARY KEY)
- device_id (TEXT)
- location (TEXT)
- sensor_type (TEXT)
- timestamp (INTEGER)
- received_at (TEXT ISO format)
- data (TEXT JSON)
- topic (TEXT)

#### fall_events
- id (INTEGER PRIMARY KEY)
- event_id (TEXT UNIQUE) - UUID string
- user_id (TEXT)
- timestamp (TEXT ISO format)
- severity_score (REAL)
- verified (INTEGER 0/1)
- location (TEXT)
- sensor_data (TEXT JSON)
- acknowledged (INTEGER 0/1)
- acknowledged_at (TEXT ISO format)

#### devices
- id (INTEGER PRIMARY KEY)
- device_id (TEXT UNIQUE)
- device_type (TEXT)
- location (TEXT)
- status (TEXT)
- last_seen (TEXT ISO format)

#### users
- id (INTEGER PRIMARY KEY)
- user_id (TEXT UNIQUE)
- name (TEXT)
- email (TEXT UNIQUE)
- phone (TEXT)
- preferences (TEXT JSON)
- created_at (TEXT ISO format)

#### alert_logs
- id (INTEGER PRIMARY KEY)
- event_id (TEXT)
- channels (TEXT JSON)
- sent_at (TEXT ISO format)
- status (TEXT)

## Benefits

1. **Simpler Deployment**: No separate database service needed
2. **File-based**: Easy backup (just copy the .db file)
3. **Lightweight**: No additional system dependencies
4. **Portable**: Database file can be moved easily
5. **Zero Configuration**: Works out of the box

## Migration Steps

If you have existing MongoDB data:

1. Export data from MongoDB:
```bash
mongoexport --db fall_detection_db --collection sensor_readings --out sensor_readings.json
mongoexport --db fall_detection_db --collection fall_events --out fall_events.json
# etc.
```

2. Convert JSON to SQLite format (write a migration script)

3. Import into SQLite using the new functions

## Notes

- Event IDs are now UUID strings instead of ObjectId
- Timestamps stored as ISO format strings
- JSON data stored as TEXT and parsed on read
- Boolean values stored as INTEGER (0/1)

## Testing

After migration, verify:
- Sensor readings are stored correctly
- Fall events can be created and retrieved
- Statistics endpoint works
- Device management works
- Alert logging works

