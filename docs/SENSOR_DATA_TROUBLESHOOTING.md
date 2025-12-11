# Sensor Data Troubleshooting Guide

## Quick Diagnostic Steps

### 1. Run the Diagnostic Script

On your Raspberry Pi, run:
```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python diagnose_sensor_data.py
```

This will show:
- How many sensor readings are in the database
- Recent sensor readings
- Devices that have been seen
- Expected MQTT topics

### 2. Check Backend Logs

Look for these messages in your backend logs:

**Good signs:**
- `✓ MQTT client connected successfully`
- `✓ Subscribed to: sensors/dht22/+`
- `📨 Received MQTT message on topic: sensors/...`
- `✓ Stored sensor reading #X from ...`

**Bad signs:**
- `⚠️ MQTT initialization failed`
- `✗ MQTT connection failed`
- No "Received MQTT message" messages

### 3. Check MQTT Connection

**Test if MQTT broker is accessible:**
```bash
# On Raspberry Pi
mosquitto_sub -h 10.162.131.191 -p 8883 -u ozsal -P '@@Ozsal23##' -t 'sensors/#' -v
```

If you see messages, MQTT is working. If not, check:
- MQTT broker is running
- Network connectivity
- Credentials are correct

### 4. Check Sensor Topics

Your sensors should publish to these topics:
- `sensors/dht22/ESP8266_XXX` - Temperature/Humidity
- `sensors/pir/ESP8266_XXX` - Motion sensor
- `sensors/ultrasonic/ESP8266_XXX` - Distance sensor
- `sensors/combined/ESP8266_XXX` - Combined readings

**Verify sensor code is publishing to correct topics!**

### 5. Check API Endpoint

Test if data is in the database:
```bash
curl http://10.162.131.191:8000/api/sensor-readings?limit=5
```

If this returns an empty array `[]`, no data has been stored yet.

### 6. Common Issues and Solutions

#### Issue: MQTT Not Connected
**Symptoms:**
- Backend logs show `⚠️ MQTT initialization failed`
- No "MQTT client connected" message

**Solutions:**
1. Check MQTT broker is running:
   ```bash
   sudo systemctl status mosquitto
   ```
2. Check broker configuration
3. Verify network connectivity
4. Check credentials in `.env` file

#### Issue: No Messages Received
**Symptoms:**
- MQTT connected but no "Received MQTT message" logs
- Diagnostic script shows 0 readings

**Solutions:**
1. Verify sensors are powered on and connected to WiFi
2. Check sensor code is publishing to correct topics
3. Test with MQTT client:
   ```bash
   mosquitto_sub -h 10.162.131.191 -p 8883 -u ozsal -P '@@Ozsal23##' -t 'sensors/#' -v
   ```
4. Check sensor serial monitor for errors

#### Issue: Messages Received But Not Stored
**Symptoms:**
- See "Received MQTT message" but no "Stored sensor reading"
- Error messages in logs

**Solutions:**
1. Check database file permissions
2. Check database file exists: `ls -la fall_detection.db`
3. Look for error messages in backend logs
4. Check disk space: `df -h`

#### Issue: Data in Database But Not in Frontend
**Symptoms:**
- Diagnostic script shows readings
- API returns data
- Frontend shows nothing

**Solutions:**
1. Check frontend is connected to correct API URL
2. Check browser console for errors
3. Check WebSocket connection
4. Verify CORS settings

### 7. Manual MQTT Test

Publish a test message to verify the system:
```bash
mosquitto_pub -h 10.162.131.191 -p 8883 -u ozsal -P '@@Ozsal23##' \
  -t 'sensors/dht22/TEST_DEVICE' \
  -m '{"device_id":"TEST_DEVICE","temperature_c":25.5,"humidity_percent":50.0}'
```

Then check:
1. Backend logs for "Received MQTT message"
2. Backend logs for "Stored sensor reading"
3. API: `curl http://10.162.131.191:8000/api/sensor-readings?limit=1`

### 8. Check Sensor Code

Verify your ESP8266 sensor code:
- ✅ WiFi credentials are correct
- ✅ MQTT broker IP/port are correct
- ✅ MQTT credentials match backend
- ✅ Publishing to correct topics (e.g., `sensors/dht22/ESP8266_001`)
- ✅ Publishing in JSON format
- ✅ Serial monitor shows successful publishes

### 9. Network Issues

Check network connectivity:
```bash
# From Raspberry Pi
ping 10.162.131.191  # MQTT broker IP
ping <sensor_ip>      # Sensor device IP

# Check if MQTT port is open
telnet 10.162.131.191 8883
```

### 10. Database Issues

Check database:
```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
sqlite3 fall_detection.db

# In SQLite:
.tables
SELECT COUNT(*) FROM sensor_readings;
SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 5;
SELECT * FROM devices;
.quit
```

## Expected Behavior

When everything is working:
1. Backend starts and connects to MQTT
2. Sensors publish data every few seconds
3. Backend logs show "Received MQTT message" for each message
4. Backend logs show "Stored sensor reading #X"
5. API endpoint returns data
6. Frontend displays data in real-time

## Still Not Working?

1. **Check all logs** - Backend, MQTT broker, sensors
2. **Run diagnostic script** - `python diagnose_sensor_data.py`
3. **Test MQTT manually** - Use mosquitto_pub/sub
4. **Check network** - Ping, telnet, firewall
5. **Verify credentials** - MQTT username/password
6. **Check topics** - Make sure sensors use correct topic format



