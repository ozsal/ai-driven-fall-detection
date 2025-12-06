# How to Check SQLite Database

## Method 1: Using sqlite3 Command Line (Recommended)

### On Raspberry Pi:

1. **Navigate to the backend directory:**
   ```bash
   cd ~/ai-driven-fall-detection/raspberry-pi-backend
   ```

2. **Open the database:**
   ```bash
   sqlite3 fall_detection.db
   ```

3. **Useful SQLite commands:**

   ```sql
   -- Show all tables
   .tables
   
   -- Show table structure
   .schema sensor_readings
   .schema devices
   .schema fall_events
   
   -- Count total sensor readings
   SELECT COUNT(*) FROM sensor_readings;
   
   -- View recent sensor readings (last 10)
   SELECT id, device_id, sensor_type, timestamp, topic, received_at 
   FROM sensor_readings 
   ORDER BY id DESC 
   LIMIT 10;
   
   -- View sensor reading with data
   SELECT id, device_id, sensor_type, data, timestamp, topic 
   FROM sensor_readings 
   ORDER BY id DESC 
   LIMIT 5;
   
   -- Count readings by sensor type
   SELECT sensor_type, COUNT(*) as count 
   FROM sensor_readings 
   GROUP BY sensor_type;
   
   -- Count readings by device
   SELECT device_id, COUNT(*) as count 
   FROM sensor_readings 
   GROUP BY device_id;
   
   -- View all devices
   SELECT * FROM devices;
   
   -- View recent devices (last seen)
   SELECT device_id, device_type, status, last_seen, location 
   FROM devices 
   ORDER BY last_seen DESC;
   
   -- View fall events
   SELECT * FROM fall_events ORDER BY timestamp DESC LIMIT 10;
   
   -- Exit SQLite
   .quit
   ```

4. **One-liner queries (without opening SQLite):**
   ```bash
   # Count total readings
   sqlite3 fall_detection.db "SELECT COUNT(*) FROM sensor_readings;"
   
   # View last 5 readings
   sqlite3 fall_detection.db "SELECT id, device_id, sensor_type, topic, received_at FROM sensor_readings ORDER BY id DESC LIMIT 5;"
   
   # View all devices
   sqlite3 fall_detection.db "SELECT * FROM devices;"
   
   # Count by sensor type
   sqlite3 fall_detection.db "SELECT sensor_type, COUNT(*) FROM sensor_readings GROUP BY sensor_type;"
   ```

## Method 2: Using the Diagnostic Script

Run the diagnostic script we created:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python diagnose_sensor_data.py
```

This will show:
- Total sensor readings count
- Recent readings (last 10)
- All devices
- Expected MQTT topics

## Method 3: Using the Debug API Endpoint

Check via the API:

```bash
curl http://10.162.131.191:8000/api/debug/database
```

Or format it nicely:
```bash
curl http://10.162.131.191:8000/api/debug/database | python3 -m json.tool
```

## Method 4: Using a GUI Tool (Optional)

If you have a GUI on your Raspberry Pi or want to use a remote tool:

1. **Install DB Browser for SQLite:**
   ```bash
   sudo apt-get update
   sudo apt-get install sqlitebrowser
   sqlitebrowser fall_detection.db
   ```

2. **Or use VS Code extension:**
   - Install "SQLite Viewer" extension
   - Open the database file

## Quick Diagnostic Queries

### Check if data is being stored:
```bash
sqlite3 fall_detection.db "SELECT COUNT(*) as total, MAX(id) as latest_id, MAX(received_at) as last_received FROM sensor_readings;"
```

### Check what devices are sending data:
```bash
sqlite3 fall_detection.db "SELECT device_id, sensor_type, COUNT(*) as count, MAX(received_at) as last_seen FROM sensor_readings GROUP BY device_id, sensor_type ORDER BY last_seen DESC;"
```

### Check recent activity (last hour):
```bash
sqlite3 fall_detection.db "SELECT device_id, sensor_type, COUNT(*) as count FROM sensor_readings WHERE received_at > datetime('now', '-1 hour') GROUP BY device_id, sensor_type;"
```

### View full reading details:
```bash
sqlite3 fall_detection.db -header -column "SELECT id, device_id, sensor_type, data, topic, received_at FROM sensor_readings ORDER BY id DESC LIMIT 5;"
```

## Database File Location

The database file is located at:
```
~/ai-driven-fall-detection/raspberry-pi-backend/fall_detection.db
```

Or full path:
```
/home/uel/ai-driven-fall-detection/raspberry-pi-backend/fall_detection.db
```

## Troubleshooting

### If database doesn't exist:
```bash
# Check if file exists
ls -la ~/ai-driven-fall-detection/raspberry-pi-backend/fall_detection.db

# If it doesn't exist, the backend will create it on startup
# Or manually initialize:
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python setup_database.py
```

### If you get "database is locked":
- The backend might be using it
- Stop the backend, check the database, then restart

### If you want to backup the database:
```bash
cp fall_detection.db fall_detection.db.backup
```

### If you want to clear all data (careful!):
```bash
sqlite3 fall_detection.db "DELETE FROM sensor_readings; DELETE FROM devices; DELETE FROM fall_events;"
```

## Example Session

```bash
# Open database
cd ~/ai-driven-fall-detection/raspberry-pi-backend
sqlite3 fall_detection.db

# In SQLite:
sqlite> .tables
sensor_readings  devices  fall_events  users  alert_logs

sqlite> SELECT COUNT(*) FROM sensor_readings;
100

sqlite> SELECT device_id, sensor_type, COUNT(*) 
   ...> FROM sensor_readings 
   ...> GROUP BY device_id, sensor_type;
ESP8266_NODE_01|pir|25
ESP8266_NODE_01|ultrasonic|25
ESP8266_NODE_01|dht22|25
ESP8266_NODE_01|combined|25

sqlite> SELECT * FROM devices;
ESP8266_NODE_01|pir|active|2024-12-06 18:30:00|Living_Room

sqlite> .quit
```

