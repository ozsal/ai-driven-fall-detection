# Quick Start Guide

Get the Fall Detection System up and running quickly.

## Prerequisites Checklist

- [ ] Raspberry Pi 4 with Raspberry Pi OS installed
- [ ] ESP8266 NodeMCU boards (2x)
- [ ] Sensors: PIR (2x), HC-SR04 (2x), DHT22 (2x)
- [ ] WiFi network access
- [ ] Computer for programming ESP8266

## 5-Minute Setup

### Step 1: Raspberry Pi (5 minutes)

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv mongodb mosquitto mosquitto-clients

# Clone or copy project files
cd ~
# (Copy project files here)

# Setup backend
cd AI-driven-fall-detection/raspberry-pi-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Update MQTT and database settings

# Start services
sudo systemctl start mosquitto

# Start API
cd api
python main.py
```

### Step 2: ESP8266 (10 minutes)

1. Install Arduino IDE
2. Add ESP8266 board support (see INSTALLATION.md)
3. Install libraries: PubSubClient, DHT sensor library, ArduinoJson
4. Open `esp8266-sensors/pir_ultrasonic_dht22/sensor_node.ino`
5. Update WiFi SSID, password, and MQTT server IP
6. Connect ESP8266 via USB
7. Upload code
8. Check Serial Monitor (115200 baud)

### Step 3: Web Dashboard (5 minutes)

```bash
cd web-dashboard/react-app
npm install

# Create .env
echo "REACT_APP_API_URL=http://localhost:8000" > .env
echo "REACT_APP_WS_URL=ws://localhost:8000/ws" >> .env

npm start
```

Open http://localhost:3000

### Step 4: Mobile App (10 minutes)

```bash
cd mobile-app/flutter-app
flutter pub get

# Configure Firebase (see INSTALLATION.md)
# Add google-services.json and GoogleService-Info.plist

flutter run
```

## Verify Installation

### Test MQTT
```bash
# On Raspberry Pi
mosquitto_sub -h localhost -t "#" -u admin -P your_password
```

You should see sensor data messages.

### Test API
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/statistics
```

### Test Fall Detection
1. Simulate fall scenario:
   - Cover PIR sensor (no motion detected)
   - Place object within 50cm of ultrasonic sensor
   - Wait for extended period (10+ seconds)
2. Check dashboard for fall event
3. Verify email alert (if configured)
4. Check mobile app notification

## Common Issues

**ESP8266 not connecting:**
- Check WiFi credentials
- Verify MQTT broker IP is correct
- Check Serial Monitor for errors

**No data in dashboard:**
- Verify MQTT broker is running
- Check API is running
- Verify WebSocket connection

**Alerts not sending:**
- Check email SMTP settings in .env
- Verify FCM server key for push notifications
- Check alert threshold settings

## Next Steps

1. Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
2. Review [docs/architecture.md](docs/architecture.md) for system overview
3. Check [docs/hardware_setup.md](docs/hardware_setup.md) for wiring
4. Configure production settings (see INSTALLATION.md)

## Getting Help

- Check component README files
- Review documentation in `docs/` directory
- Verify all services are running
- Check logs for error messages

## Production Checklist

- [ ] Change default passwords
- [ ] Configure SSL/TLS
- [ ] Set up systemd services
- [ ] Configure firewall
- [ ] Set up backups
- [ ] Test alert system
- [ ] Monitor system health

