# Debugging: No Sensor Readings in API

## Quick Diagnostic Steps

### 1. Check the Debug Endpoint

After pulling the latest code and restarting, check the debug endpoint:

```bash
curl http://10.162.131.191:8000/api/debug/database
```

This will show:
- Database file path and existence
- Total readings count
- Total devices count
- MQTT connection status
- Sample readings (last 5)
- All devices

### 2. Check Backend Logs

Look for these messages in your backend logs:

**When MQTT message is received:**
```
📨 Received MQTT message on topic: sensors/pir/ESP8266_NODE_01
   Payload: 1...
```

**When data is stored:**
```
✓ Stored sensor reading #X from ESP8266_NODE_01 (pir) on topic 'sensors/pir/ESP8266_NODE_01'
  Device ID: ESP8266_NODE_01, Sensor Type: pir, Location: None
  Data: {'motion_detected': True}
```

**When API is called:**
```
📊 API: Fetching sensor readings - device_id=None, sensor_type=None, limit=100
📊 API: Returning X sensor readings
```

### 3. Common Issues

#### Issue: MQTT Messages Received But Not Stored

**Symptoms:**
- See "📨 Received MQTT message" but no "✓ Stored sensor reading"
- Debug endpoint shows `total_readings: 0`

**Check:**
1. Look for error messages after "Received MQTT message"
2. Check database file permissions
3. Check disk space: `df -h`

#### Issue: Data Stored But Not Returned

**Symptoms:**
- See "✓ Stored sensor reading" messages
- Debug endpoint shows `total_readings: X` but API returns 0

**Check:**
1. Check backend logs for "📊 API: Returning X sensor readings"
2. Verify database query is working
3. Check if there's a filter issue (device_id or sensor_type)

#### Issue: Database Path Issue

**Symptoms:**
- Debug endpoint shows `database_exists: false`
- Different database path than expected

**Fix:**
1. Check the database path in debug endpoint
2. Verify the database file exists at that location
3. Check if multiple database files exist

### 4. Manual Database Check

On Raspberry Pi, check the database directly:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
sqlite3 fall_detection.db

# In SQLite:
SELECT COUNT(*) FROM sensor_readings;
SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 5;
SELECT * FROM devices;
.quit
```

### 5. Test MQTT Message Flow

1. **Check if messages are being received:**
   - Look for "📨 Received MQTT message" in logs

2. **Check if messages are being stored:**
   - Look for "✓ Stored sensor reading" in logs
   - Check debug endpoint: `curl http://10.162.131.191:8000/api/debug/database`

3. **Check if API returns data:**
   - Check backend logs for "📊 API: Returning X sensor readings"
   - Test API: `curl http://10.162.131.191:8000/api/sensor-readings?limit=5`

### 6. Expected Flow

When everything works:
1. ESP8266 publishes → MQTT broker
2. Backend receives → "📨 Received MQTT message"
3. Backend processes → Extracts device_id, sensor_type, data
4. Backend stores → "✓ Stored sensor reading #X"
5. API query → "📊 API: Fetching sensor readings"
6. API returns → "📊 API: Returning X sensor readings"
7. Frontend displays → Data appears in dashboard

### 7. Next Steps After Pulling Latest Code

1. **Pull and restart:**
   ```bash
   cd ~/ai-driven-fall-detection
   git pull
   cd raspberry-pi-backend
   python api/main.py
   ```

2. **Check debug endpoint:**
   ```bash
   curl http://10.162.131.191:8000/api/debug/database | python -m json.tool
   ```

3. **Watch backend logs** for:
   - MQTT message reception
   - Data storage
   - API calls

4. **If still no data:**
   - Check MQTT broker is running
   - Check sensors are publishing
   - Check backend logs for errors
   - Run diagnostic script: `python diagnose_sensor_data.py`

