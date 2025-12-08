# DHT22 MQTT Port Update & Verification Summary

## ✅ Changes Made

### 1. MQTT Port Updated
- **Changed default port from 8883 to 1883** in `mqtt_client.py`
- This matches ESP8266 configuration (port 1883, non-encrypted MQTT)
- **File:** `raspberry-pi-backend/mqtt_broker/mqtt_client.py` (line 25)

### 2. Enhanced MQTT Logging
- Added DHT22-specific logging in MQTT client
- Validates JSON payload and checks for temperature/humidity fields
- **File:** `raspberry-pi-backend/mqtt_broker/mqtt_client.py`

### 3. Enhanced Message Handler Logging
- Added detailed DHT22 data extraction logging
- Shows temperature and humidity values before storage
- **File:** `raspberry-pi-backend/api/main.py`

## 📊 Current Status

### MQTT Connection: ✅ WORKING
- Successfully connected to `10.162.131.191:1883`
- Subscribed to `sensors/dht22/+` topic
- Receiving PIR and Ultrasonic messages

### DHT22 Messages: ❌ NOT RECEIVED
- No DHT22 messages seen during 30-second test
- PIR and Ultrasonic messages are being received
- Database is empty (no sensor readings stored)

## 🔍 Diagnosis

### What's Working:
1. ✅ MQTT connection on port 1883
2. ✅ Topic subscription (`sensors/dht22/+`)
3. ✅ PIR sensor messages received
4. ✅ Ultrasonic sensor messages received

### What's Not Working:
1. ❌ DHT22 messages not being received from ESP8266
2. ❌ No data in database (backend may not be running to process messages)

## 🎯 Next Steps

### Step 1: Verify ESP8266 is Publishing DHT22 Data

Check ESP8266 serial monitor to see if it's publishing DHT22 data:
- Look for: `"Published DHT22: {...}"`
- Should show JSON with `temperature_c` and `humidity_percent`

### Step 2: Restart Backend Server

The backend needs to be restarted to:
- Use the new port 1883
- Process incoming MQTT messages
- Store data in database

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python api/main.py
```

### Step 3: Monitor Backend Logs

Look for these messages when DHT22 data arrives:
```
🌡️ DHT22 MQTT message received on topic: sensors/dht22/ESP8266_NODE_01
   Full payload: {"device_id":"ESP8266_NODE_01","temperature_c":22.5,"humidity_percent":45.0,...}
   ✓ DHT22 data found: temp=22.5°C, humidity=45.0%
🌡️ DHT22 data extracted: temp=22.5°C, humidity=45.0%
💾 Attempting to store reading: device_id=ESP8266_NODE_01, sensor_type=dht22
✅ SUCCESS: Stored sensor reading #X
```

### Step 4: Verify Data in Database

After backend is running and receiving messages:
```bash
# Check via API
curl http://10.162.131.191:8000/api/sensors/dht22?limit=5

# Or run verification script
python raspberry-pi-backend/verify_dht22_storage.py
```

## 🔧 Troubleshooting

### Issue: ESP8266 Not Publishing DHT22

**Check ESP8266 code:**
- Verify DHT22 sensor is connected to GPIO4 (D2)
- Check if DHT22 readings are successful: `if (!isnan(temp) && !isnan(hum))`
- Verify topic: `sensors/dht22/ESP8266_NODE_01`

**Check ESP8266 Serial Monitor:**
- Should see: `"Published DHT22: {...}"` every 2 seconds
- If not, DHT22 sensor may not be working

### Issue: Messages Received But Not Stored

**Check backend logs for:**
- `❌ DATABASE ERROR` - Database issue
- `⚠️ DHT22 payload missing temperature_c or humidity_percent` - Payload format issue
- `❌ Message handler failed` - Processing error

### Issue: Port Mismatch

**Verify port configuration:**
- ESP8266 uses: `1883` (in `sensor_node.ino` line 30)
- Backend now uses: `1883` (default, can override with `.env`)

**If using `.env` file:**
```env
MQTT_BROKER_HOST=10.162.131.191
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
```

## 📝 Expected Data Flow

1. **ESP8266** reads DHT22 sensor every 2 seconds
2. **ESP8266** publishes JSON to `sensors/dht22/ESP8266_NODE_01`:
   ```json
   {
     "device_id": "ESP8266_NODE_01",
     "temperature_c": 22.5,
     "humidity_percent": 45.0,
     "timestamp": 1234567890
   }
   ```
3. **MQTT Broker** receives message on port 1883
4. **Backend MQTT Client** receives message and logs: `🌡️ DHT22 MQTT message received`
5. **Message Handler** extracts `temperature_c` and `humidity_percent`
6. **Database** stores reading with sensor_type='dht22'
7. **API** returns data via `/api/sensors/dht22`

## ✅ Verification Checklist

- [x] Port updated to 1883 in `mqtt_client.py`
- [x] Enhanced logging for DHT22 messages
- [x] MQTT connection test successful
- [ ] ESP8266 publishing DHT22 data (check serial monitor)
- [ ] Backend running and processing messages
- [ ] DHT22 data in database
- [ ] API returning DHT22 data

## 🚀 Quick Test

Run this to test the full flow:
```bash
# 1. Start backend
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python api/main.py

# 2. In another terminal, check for DHT22 data
curl http://10.162.131.191:8000/api/sensors/dht22?limit=5

# 3. Monitor backend logs for DHT22 messages
```


