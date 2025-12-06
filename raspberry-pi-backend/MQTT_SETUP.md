# MQTT Broker Setup Guide

## Quick Fix for "Connection Refused" Error

If you're getting `ConnectionRefusedError: [Errno 111] Connection refused`, the MQTT broker is not running or not accessible.

## Option 1: Start Local Mosquitto Broker (Recommended for Development)

### Install Mosquitto

```bash
# On Ubuntu/Debian/Raspberry Pi OS
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients -y

# On macOS
brew install mosquitto

# On Windows
# Download from: https://mosquitto.org/download/
```

### Start Mosquitto

```bash
# Start as a service (Linux/Raspberry Pi)
sudo systemctl start mosquitto
sudo systemctl enable mosquitto  # Enable on boot

# Or run in foreground for testing
mosquitto -v

# Or run in background
mosquitto -d
```

### Verify Mosquitto is Running

```bash
# Check if mosquitto is running
sudo systemctl status mosquitto

# Or check process
ps aux | grep mosquitto

# Test connection
mosquitto_pub -h localhost -t test/topic -m "Hello"
mosquitto_sub -h localhost -t test/topic
```

## Option 2: Use Remote MQTT Broker

If you're using a remote MQTT broker (like the one configured at `10.162.131.191:8883`):

1. **Check if the broker is accessible:**
   ```bash
   # Test connection
   ping 10.162.131.191
   
   # Test MQTT port (if using unencrypted MQTT on port 1883)
   telnet 10.162.131.191 1883
   
   # For encrypted MQTT (port 8883), you may need certificates
   ```

2. **Verify credentials in `.env` file:**
   ```bash
   cd raspberry-pi-backend
   cat .env | grep MQTT
   ```

3. **Update `.env` file if needed:**
   ```env
   MQTT_BROKER_HOST=10.162.131.191
   MQTT_BROKER_PORT=8883
   MQTT_USERNAME=ozsal
   MQTT_PASSWORD=@@Ozsal23##
   ```

## Option 3: Configure for Local Development

If you want to use a local broker for development:

1. **Create/Update `.env` file:**
   ```bash
   cd raspberry-pi-backend
   nano .env
   ```

2. **Add/Update these lines:**
   ```env
   MQTT_BROKER_HOST=localhost
   MQTT_BROKER_PORT=1883
   MQTT_USERNAME=
   MQTT_PASSWORD=
   ```

   **Note:** Local Mosquitto typically doesn't require authentication by default.

3. **Restart the backend:**
   ```bash
   python api/main.py
   ```

## Current Configuration

Based on your code, the system is configured to connect to:
- **Host:** `10.162.131.191`
- **Port:** `8883` (MQTT over TLS/SSL)
- **Username:** `ozsal`
- **Password:** `@@Ozsal23##`

## Troubleshooting

### Error: Connection Refused

**Causes:**
1. MQTT broker is not running
2. Wrong host/port in configuration
3. Firewall blocking the connection
4. Network connectivity issues

**Solutions:**
1. Start the MQTT broker (see Option 1 above)
2. Check `.env` file for correct host/port
3. Check firewall rules:
   ```bash
   # On Raspberry Pi
   sudo ufw status
   sudo ufw allow 1883/tcp  # For unencrypted MQTT
   sudo ufw allow 8883/tcp  # For encrypted MQTT
   ```
4. Test network connectivity:
   ```bash
   ping <MQTT_BROKER_HOST>
   telnet <MQTT_BROKER_HOST> <MQTT_BROKER_PORT>
   ```

### Error: Authentication Failed

**Causes:**
1. Wrong username/password
2. Broker doesn't have authentication configured

**Solutions:**
1. Verify credentials in `.env` file
2. Check broker configuration for authentication requirements
3. For local development, remove username/password if not needed

### API Starts Without MQTT

**Good News:** The API will now start even if MQTT is unavailable! You'll see a warning message:
```
⚠️  MQTT connection error: [Errno 111] Connection refused
⚠️  MQTT broker at 10.162.131.191:8883 is not available
⚠️  API will continue without MQTT. Sensor data will not be received until MQTT is available.
```

**What this means:**
- ✅ API endpoints will work
- ✅ Database operations will work
- ✅ WebSocket connections will work
- ❌ Sensor data from MQTT will not be received
- ❌ Fall detection from MQTT sensors will not work

**To fix:** Start the MQTT broker and restart the API.

## Testing MQTT Connection

### Test with mosquitto_pub (publish)

```bash
# Publish a test message
mosquitto_pub -h localhost -p 1883 -t "sensors/test" -m '{"temperature": 25.5, "humidity": 60}'

# With authentication
mosquitto_pub -h 10.162.131.191 -p 8883 -u ozsal -P "@@Ozsal23##" -t "sensors/test" -m '{"test": "data"}'
```

### Test with mosquitto_sub (subscribe)

```bash
# Subscribe to all sensor topics
mosquitto_sub -h localhost -p 1883 -t "sensors/#" -v

# With authentication
mosquitto_sub -h 10.162.131.191 -p 8883 -u ozsal -P "@@Ozsal23##" -t "sensors/#" -v
```

## MQTT Topics Used by the System

The backend subscribes to these topics:
- `sensors/pir/+` - PIR motion sensor data
- `sensors/ultrasonic/+` - Ultrasonic distance sensor data
- `sensors/dht22/+` - DHT22 temperature/humidity data
- `sensors/combined/+` - Combined sensor readings from ESP8266
- `wearable/fall/+` - Wearable fall detection (if using)
- `wearable/accelerometer/+` - Accelerometer data (if using)
- `devices/+/status` - Device status updates

## Next Steps

1. ✅ Start MQTT broker (see Option 1)
2. ✅ Verify connection with test commands
3. ✅ Restart the backend API
4. ✅ Check logs for "MQTT client connected successfully"
5. ✅ Test with sensor data publishing

## Additional Resources

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [MQTT Protocol Specification](https://mqtt.org/)
- [Paho MQTT Python Client](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php)

