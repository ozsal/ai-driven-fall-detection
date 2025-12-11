# DHT22 Temperature & Humidity Data Verification Guide

## Overview

This guide helps you verify that DHT22 sensor data from ESP8266 is being received via MQTT and stored in the database.

## Quick Check

### 1. Run the Test Script

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python test_dht22_mqtt.py
```

This script will:
- Check existing DHT22 data in the database
- Connect to MQTT and wait 30 seconds for DHT22 messages
- Verify temperature and humidity data is present
- Check if new data is being stored

### 2. Check MQTT Port Configuration

**Important:** ESP8266 publishes to port **1883** (non-encrypted), but the backend defaults to **8883** (TLS).

Check your `.env` file:
```bash
cat raspberry-pi-backend/.env | grep MQTT_BROKER_PORT
```

If it shows `8883`, but your ESP8266 uses `1883`, update it:
```bash
MQTT_BROKER_PORT=1883
```

### 3. Verify MQTT Subscription

The backend subscribes to: `sensors/dht22/+`

ESP8266 should publish to: `sensors/dht22/ESP8266_NODE_01`

### 4. Check Backend Logs

Look for these messages when DHT22 data is received:

**Good signs:**
```
🌡️ DHT22 MQTT message received on topic: sensors/dht22/ESP8266_NODE_01
   Full payload: {"device_id":"ESP8266_NODE_01","temperature_c":22.5,"humidity_percent":45.0,"timestamp":12345}
   ✓ DHT22 data found: temp=22.5°C, humidity=45.0%
🌡️ DHT22 data extracted: temp=22.5°C, humidity=45.0%
💾 Attempting to store reading: device_id=ESP8266_NODE_01, sensor_type=dht22
✅ SUCCESS: Stored sensor reading #123
   🌡️ DHT22 stored with: temp=22.5°C, humidity=45.0%
```

**Bad signs:**
```
⚠️ DHT22 payload missing temperature_c or humidity_percent
⚠️ DHT22 payload is not valid JSON
❌ Message handler failed for topic sensors/dht22/...
```

### 5. Test MQTT Connection Manually

Subscribe to DHT22 topics to see if messages are being published:

```bash
# If using port 1883 (non-encrypted)
mosquitto_sub -h 10.162.131.191 -p 1883 -t "sensors/dht22/#" -v

# If using port 8883 (TLS) with authentication
mosquitto_sub -h 10.162.131.191 -p 8883 -u ozsal -P "@@Ozsal23##" -t "sensors/dht22/#" -v
```

If you see messages, MQTT is working. If not:
- Check ESP8266 is powered on and connected
- Verify ESP8266 WiFi connection
- Check MQTT broker is running

### 6. Check Database

Query the database directly:

```bash
sqlite3 fall_detection.db "SELECT id, device_id, sensor_type, timestamp, data FROM sensor_readings WHERE sensor_type='dht22' ORDER BY id DESC LIMIT 5;"
```

Or use the API:

```bash
curl http://10.162.131.191:8000/api/sensors/dht22?limit=5
```

### 7. Verify ESP8266 Code

Check that ESP8266 is publishing DHT22 data correctly:

```cpp
// In sensor_node.ino, verify this code exists:
StaticJsonDocument<256> dht22_doc;
dht22_doc["device_id"] = device_id;
dht22_doc["temperature_c"] = temperature;
dht22_doc["humidity_percent"] = humidity;
dht22_doc["timestamp"] = millis();
char dht22_buffer[256];
serializeJson(dht22_doc, dht22_buffer);
client.publish(topic_dht22.c_str(), dht22_buffer);
```

## Common Issues

### Issue 1: Port Mismatch
**Symptom:** No MQTT messages received
**Solution:** Ensure backend and ESP8266 use the same MQTT port (1883 or 8883)

### Issue 2: Missing Fields
**Symptom:** Messages received but no temperature/humidity in database
**Solution:** Check ESP8266 is publishing `temperature_c` and `humidity_percent` (not `temperature` and `humidity`)

### Issue 3: JSON Parsing Error
**Symptom:** "DHT22 payload is not valid JSON" in logs
**Solution:** Verify ESP8266 is serializing JSON correctly before publishing

### Issue 4: Database Not Storing
**Symptom:** Messages received but database empty
**Solution:** Check database permissions and path. Look for "DATABASE ERROR" in logs.

## Expected Data Format

**MQTT Topic:** `sensors/dht22/ESP8266_NODE_01`

**Payload (JSON):**
```json
{
  "device_id": "ESP8266_NODE_01",
  "temperature_c": 22.5,
  "humidity_percent": 45.0,
  "timestamp": 1234567890
}
```

**Database Storage:**
```json
{
  "id": 123,
  "device_id": "ESP8266_NODE_01",
  "sensor_type": "dht22",
  "timestamp": 1234567890,
  "data": {
    "temperature_c": 22.5,
    "humidity_percent": 45.0
  },
  "topic": "sensors/dht22/ESP8266_NODE_01"
}
```

## Next Steps

1. Run `test_dht22_mqtt.py` to diagnose the issue
2. Check MQTT port configuration matches ESP8266
3. Verify ESP8266 is publishing to correct topic
4. Check backend logs for DHT22-specific messages
5. Query database to confirm data is stored

