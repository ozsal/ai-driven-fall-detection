# MQTT TLS/SSL Setup Guide

## Overview

This guide explains how to set up TLS/SSL encryption for MQTT communication between sensor nodes (ESP8266) and the backend system. TLS/SSL provides:

- **Encryption**: All MQTT messages are encrypted in transit
- **Authentication**: Server certificate verification prevents man-in-the-middle attacks
- **Integrity**: Ensures messages are not tampered with during transmission

## Prerequisites

- OpenSSL installed on your system
- Mosquitto MQTT broker installed and running
- Python `paho-mqtt` library (already in requirements.txt)
- ESP8266 with sufficient flash memory for TLS (optional, for client-side TLS)

## Step 1: Generate SSL Certificates

### Option A: Using Bash Script (Linux/macOS)

```bash
cd raspberry-pi-backend/mqtt_broker
chmod +x generate_certificates.sh
./generate_certificates.sh
```

### Option B: Using PowerShell Script (Windows)

```powershell
cd raspberry-pi-backend\mqtt_broker
.\generate_certificates.ps1
```

The script will:
1. Create a Certificate Authority (CA)
2. Generate a server certificate for the MQTT broker
3. Generate a client certificate (for mutual TLS, optional)
4. Store all certificates in the `certs/` directory

**Important**: Keep all `.key` files secure and never commit them to version control!

## Step 2: Configure Mosquitto Broker

### Copy Certificates

```bash
# Create Mosquitto certificates directory
sudo mkdir -p /etc/mosquitto/certs

# Copy certificates
sudo cp raspberry-pi-backend/mqtt_broker/certs/ca.crt /etc/mosquitto/certs/
sudo cp raspberry-pi-backend/mqtt_broker/certs/server.crt /etc/mosquitto/certs/
sudo cp raspberry-pi-backend/mqtt_broker/certs/server.key /etc/mosquitto/certs/

# Set proper permissions
sudo chmod 644 /etc/mosquitto/certs/*.crt
sudo chmod 600 /etc/mosquitto/certs/*.key
sudo chown mosquitto:mosquitto /etc/mosquitto/certs/*
```

### Configure Mosquitto

```bash
# Copy TLS configuration
sudo cp raspberry-pi-backend/mqtt_broker/mosquitto_tls.conf /etc/mosquitto/conf.d/mqtt_tls.conf

# Or edit the main config file
sudo nano /etc/mosquitto/mosquitto.conf
```

Add the TLS configuration:

```ini
# Listen on port 8883 for TLS connections
listener 8883
protocol mqtt

# TLS/SSL Configuration
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key

# TLS Version
tls_version tlsv1.2

# Require client certificates (optional - set to true for mutual TLS)
require_certificate false

# Authentication (optional, can use with TLS)
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl
```

### Restart Mosquitto

```bash
sudo systemctl restart mosquitto
sudo systemctl status mosquitto
```

### Verify TLS is Working

```bash
# Test TLS connection (should connect successfully)
mosquitto_sub -h localhost -p 8883 -t "test/topic" \
  --cafile /etc/mosquitto/certs/ca.crt \
  -u your_username -P your_password

# In another terminal, publish a test message
mosquitto_pub -h localhost -p 8883 -t "test/topic" -m "Hello TLS" \
  --cafile /etc/mosquitto/certs/ca.crt \
  -u your_username -P your_password
```

## Step 3: Configure Python Backend

### Update Environment Variables

Edit `.env` file in `raspberry-pi-backend/`:

```env
# MQTT Broker Configuration
MQTT_BROKER_HOST=10.162.131.191
MQTT_BROKER_PORT=8883  # TLS port

# Enable TLS
MQTT_USE_TLS=true

# Certificate paths (relative to project root or absolute)
MQTT_CA_CERT=mqtt_broker/certs/ca.crt

# For mutual TLS (optional):
# MQTT_CLIENT_CERT=mqtt_broker/certs/client.crt
# MQTT_CLIENT_KEY=mqtt_broker/certs/client.key

# MQTT Authentication (optional, can use with TLS)
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password

# Insecure mode (NOT RECOMMENDED - only for testing)
# MQTT_TLS_INSECURE=false
```

### Test Connection

```bash
cd raspberry-pi-backend
python -c "
from mqtt_broker.mqtt_client import MQTTClient
import asyncio

async def test():
    client = MQTTClient()
    await client.connect()
    if client.is_connected():
        print('✓ TLS connection successful!')
        client.print_stats()
    await client.disconnect()

asyncio.run(test())
"
```

## Step 4: Configure ESP8266 (Optional)

**Note**: TLS/SSL on ESP8266 requires significant flash memory (~50KB+). Only enable if you have sufficient space.

### Update Arduino Code

1. Open `esp8266-sensors/pir_ultrasonic_dht22/sensor_node.ino`

2. Enable TLS:

```cpp
#define USE_TLS true  // Enable TLS/SSL

// Add your CA certificate
const char* ca_cert = \
  "-----BEGIN CERTIFICATE-----\n" \
  "YOUR_CA_CERTIFICATE_CONTENT_HERE\n" \
  "-----END CERTIFICATE-----\n";
```

3. Update MQTT port:

```cpp
const int mqtt_port = 8883;  // TLS port
```

4. Upload the updated code to ESP8266

### Memory Considerations

- **Without TLS**: ~250KB flash used
- **With TLS**: ~300KB+ flash used (depends on certificate size)
- ESP8266 typically has 4MB flash, so TLS is usually feasible

## Configuration Options

### Server-Only TLS (Recommended)

- Client verifies server certificate
- No client certificates needed
- Simpler setup
- Still provides encryption and server authentication

**Configuration:**
- `require_certificate false` in Mosquitto
- `MQTT_CA_CERT` set in `.env`
- No client certificates needed

### Mutual TLS (mTLS)

- Both client and server verify each other's certificates
- Stronger security
- Requires client certificates

**Configuration:**
- `require_certificate true` in Mosquitto
- `MQTT_CA_CERT`, `MQTT_CLIENT_CERT`, `MQTT_CLIENT_KEY` set in `.env`
- Client certificates generated and distributed

## Verification and Testing

### Check TLS Status via API

```bash
curl http://localhost:8000/api/mqtt/stats
```

Response includes TLS status:

```json
{
  "tls_enabled": true,
  "tls_mutual": false,
  "qos_level": 1,
  "reliability_percentage": 99.8,
  ...
}
```

### Monitor MQTT Connections

```bash
# Check Mosquitto logs
sudo tail -f /var/log/mosquitto/mosquitto.log

# Test TLS connection
mosquitto_sub -h your_broker_ip -p 8883 \
  --cafile certs/ca.crt \
  -t "sensors/#" -v
```

## Troubleshooting

### Certificate Verification Failed

**Error**: `ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Solutions:**
1. Ensure CA certificate path is correct
2. Verify certificate hasn't expired
3. Check broker hostname matches certificate CN
4. For testing, use `MQTT_TLS_INSECURE=true` (NOT for production!)

### Connection Refused on Port 8883

**Error**: `Connection refused` or `Connection timeout`

**Solutions:**
1. Verify Mosquitto is listening on port 8883:
   ```bash
   sudo netstat -tlnp | grep 8883
   ```
2. Check firewall rules allow port 8883
3. Verify Mosquitto configuration is correct
4. Check Mosquitto logs: `sudo journalctl -u mosquitto`

### ESP8266 TLS Issues

**Problem**: ESP8266 can't connect with TLS

**Solutions:**
1. Check flash memory usage (TLS requires more space)
2. Verify CA certificate is correctly formatted
3. Ensure certificate fits in program memory
4. Consider using certificate fingerprint instead of full certificate

### Certificate Expiration

Certificates expire after the validity period (default: 365 days).

**To renew:**
1. Generate new certificates using the scripts
2. Update broker configuration
3. Restart Mosquitto
4. Update client configurations

## Security Best Practices

1. **Keep Private Keys Secure**
   - Never commit `.key` files to version control
   - Use proper file permissions (600)
   - Store keys in secure locations

2. **Certificate Validity**
   - Use shorter validity periods for production (90-180 days)
   - Set up certificate renewal process
   - Monitor certificate expiration dates

3. **TLS Version**
   - Use TLS 1.2 or higher
   - Disable older TLS versions if not needed

4. **Certificate Authority**
   - Use a trusted CA for production
   - Self-signed certificates are fine for development/testing
   - Consider Let's Encrypt for production

5. **Firewall Rules**
   - Only allow port 8883 from trusted networks
   - Block port 1883 if TLS-only access is required

6. **Monitoring**
   - Monitor TLS handshake failures
   - Log certificate verification errors
   - Track TLS connection statistics

## Performance Impact

TLS/SSL adds minimal overhead:
- **CPU**: ~5-10% increase for encryption/decryption
- **Latency**: ~10-50ms additional connection time
- **Bandwidth**: Minimal increase (~1-2% for overhead)

For most IoT applications, this is negligible and the security benefits far outweigh the minimal performance cost.

## Migration from Non-TLS to TLS

### Backend Migration

1. Generate certificates
2. Configure Mosquitto for TLS (port 8883)
3. Keep port 1883 active during migration
4. Update `.env` file with TLS settings
5. Test TLS connection
6. Switch clients to TLS one by one
7. Once all clients migrated, disable port 1883

### Zero-Downtime Migration

- Run both ports (1883 and 8883) simultaneously
- Migrate clients gradually
- Monitor for issues
- Disable non-TLS port only after all clients migrated

## Additional Resources

- [Mosquitto TLS Documentation](https://mosquitto.org/man/mosquitto-conf-5.html)
- [OpenSSL Certificate Guide](https://www.openssl.org/docs/)
- [ESP8266 TLS Support](https://github.com/esp8266/Arduino/tree/master/libraries/ESP8266WiFi/src)
- [Paho MQTT Python TLS](https://www.eclipse.org/paho/clients/python/docs/)

## Summary

TLS/SSL encryption for MQTT provides:
- ✅ Encrypted message transmission
- ✅ Server authentication
- ✅ Message integrity
- ✅ Protection against man-in-the-middle attacks
- ✅ Optional mutual authentication (mTLS)

The implementation is straightforward and provides significant security improvements with minimal performance impact.

