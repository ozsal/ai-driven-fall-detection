# MQTT TLS/SSL Setup Instructions

## Summary

I've restored TLS/SSL support in the MQTT client code. Here's what needs to be done to complete the setup:

## ✅ What's Already Done

1. ✅ **MQTT Client Code**: TLS/SSL support restored in `mqtt_broker/mqtt_client.py`
2. ✅ **Configuration Files**: `mosquitto_tls.conf` template is ready
3. ✅ **Certificate Scripts**: Generation scripts are available (bash and PowerShell)
4. ✅ **Environment Setup**: Helper script created to update .env file

## 🔧 What Needs to Be Done on Raspberry Pi

### Step 1: Generate Certificates

SSH into your Raspberry Pi and run:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend/mqtt_broker
chmod +x generate_certificates.sh
./generate_certificates.sh
```

When prompted, enter your broker IP (e.g., `10.162.131.191`)

This will create:
- `certs/ca.crt` - Certificate Authority certificate
- `certs/ca.key` - CA private key (KEEP SECRET!)
- `certs/server.crt` - Server certificate
- `certs/server.key` - Server private key (KEEP SECRET!)
- `certs/client.crt` - Client certificate (for mutual TLS, optional)
- `certs/client.key` - Client private key (KEEP SECRET!)

### Step 2: Copy Certificates to Mosquitto

```bash
# Create Mosquitto certificates directory
sudo mkdir -p /etc/mosquitto/certs

# Copy certificates
sudo cp certs/ca.crt /etc/mosquitto/certs/
sudo cp certs/server.crt /etc/mosquitto/certs/
sudo cp certs/server.key /etc/mosquitto/certs/

# Set proper permissions
sudo chmod 644 /etc/mosquitto/certs/*.crt
sudo chmod 600 /etc/mosquitto/certs/*.key
sudo chown mosquitto:mosquitto /etc/mosquitto/certs/*
```

### Step 3: Configure Mosquitto

```bash
# Copy TLS configuration
sudo cp mqtt_broker/mosquitto_tls.conf /etc/mosquitto/conf.d/mqtt_tls.conf

# Verify configuration
sudo nano /etc/mosquitto/conf.d/mqtt_tls.conf
```

The config should have:
- Listener on port 8883 (TLS)
- Certificate paths pointing to `/etc/mosquitto/certs/`
- TLS version 1.2
- `require_certificate false` (server-only TLS, recommended)

### Step 4: Restart Mosquitto

```bash
sudo systemctl restart mosquitto
sudo systemctl status mosquitto
```

Check for any errors in the output.

### Step 5: Verify TLS is Working

```bash
# Test TLS connection (subscribe in one terminal)
mosquitto_sub -h localhost -p 8883 -t "test/topic" \
  --cafile /etc/mosquitto/certs/ca.crt

# Test TLS connection (publish in another terminal)
mosquitto_pub -h localhost -p 8883 -t "test/topic" -m "Hello TLS" \
  --cafile /etc/mosquitto/certs/ca.crt
```

If both commands work without errors, TLS is configured correctly!

### Step 6: Copy CA Certificate to Windows Machine

Copy `certs/ca.crt` from Raspberry Pi to your Windows machine:

```bash
# On Raspberry Pi
scp ~/ai-driven-fall-detection/raspberry-pi-backend/mqtt_broker/certs/ca.crt user@windows-machine:/path/to/raspberry-pi-backend/mqtt_broker/certs/
```

Or manually copy the file to: `H:\AI driven fall detection\raspberry-pi-backend\mqtt_broker\certs\ca.crt`

## 🔧 Configure Python Backend

### Update .env File

On your Windows machine, edit `raspberry-pi-backend/.env` and add/update:

```env
# MQTT Broker Configuration
MQTT_BROKER_HOST=10.162.131.191
MQTT_BROKER_PORT=8883  # TLS port

# Enable TLS
MQTT_USE_TLS=true

# Certificate path (relative to project root)
MQTT_CA_CERT=mqtt_broker/certs/ca.crt

# For mutual TLS (optional):
# MQTT_CLIENT_CERT=mqtt_broker/certs/client.crt
# MQTT_CLIENT_KEY=mqtt_broker/certs/client.key

# MQTT Authentication (if configured)
MQTT_USERNAME=
MQTT_PASSWORD=

# Insecure mode (NOT RECOMMENDED - only for testing)
MQTT_TLS_INSECURE=false
```

Or run the helper script:
```powershell
cd raspberry-pi-backend
.\setup_tls.ps1
```

### Test Connection

```bash
cd raspberry-pi-backend
python check_mqtt_connection.py
```

You should see:
```
✓ MQTT client connected successfully
  Broker: 10.162.131.191:8883
  Configuring TLS/SSL connection...
  ✓ TLS/SSL configured
    CA Certificate: mqtt_broker/certs/ca.crt
```

## 🔍 Troubleshooting

### Certificate Verification Failed

**Error**: `ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Solutions:**
1. Verify `ca.crt` is in the correct location
2. Check certificate hasn't expired
3. Ensure broker hostname matches certificate CN (should be 10.162.131.191)
4. For testing only, set `MQTT_TLS_INSECURE=true` (NOT for production!)

### Connection Refused on Port 8883

**Error**: `Connection refused` or `Connection timeout`

**Solutions:**
1. Check Mosquitto is listening on 8883:
   ```bash
   sudo netstat -tlnp | grep 8883
   ```
2. Check firewall allows port 8883
3. Verify Mosquitto config is correct
4. Check logs: `sudo journalctl -u mosquitto -f`

### Mosquitto Won't Start

Check Mosquitto logs:
```bash
sudo journalctl -u mosquitto -n 50
```

Common issues:
- Certificate file permissions (should be readable by mosquitto user)
- Certificate file paths incorrect
- Certificate expired or invalid

## 📋 Quick Checklist

- [ ] Generate certificates on Raspberry Pi
- [ ] Copy certificates to `/etc/mosquitto/certs/`
- [ ] Set proper file permissions
- [ ] Configure Mosquitto with TLS settings
- [ ] Restart Mosquitto service
- [ ] Test TLS connection with mosquitto_sub/pub
- [ ] Copy `ca.crt` to Windows machine
- [ ] Update `.env` file with TLS settings
- [ ] Test Python backend connection
- [ ] Verify encrypted communication works

## 🔒 Security Notes

1. **Never commit private keys** (`.key` files) to git
2. Keep `ca.key` and `server.key` secure on Raspberry Pi only
3. Only distribute `ca.crt` to clients that need to verify the server
4. Use strong passwords if enabling MQTT authentication
5. Consider mutual TLS (mTLS) for additional security

## 📚 Additional Resources

- Full documentation: `docs/MQTT_TLS_SETUP.md`
- Mosquitto TLS docs: https://mosquitto.org/man/mosquitto-conf-5.html
- Certificate generation: `mqtt_broker/generate_certificates.sh`

