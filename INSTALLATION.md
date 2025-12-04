# Installation Guide

Complete installation guide for the AI-Driven Fall Detection System.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Raspberry Pi Setup](#raspberry-pi-setup)
3. [ESP8266 Setup](#esp8266-setup)
4. [Database Setup](#database-setup)
5. [Web Dashboard Setup](#web-dashboard-setup)
6. [Web Dashboard Setup](#web-dashboard-setup)
7. [Mobile App Setup](#mobile-app-setup)
8. [Configuration](#configuration)
9. [Testing](#testing)

## System Requirements

### Hardware
- Raspberry Pi 4 (4GB RAM recommended)
- ESP8266 NodeMCU v1.0 (2x for multiple rooms)
- PIR Motion Sensor (HC-SR501) - 2x
- Ultrasonic Distance Sensor (HC-SR04) - 2x
- DHT22 Temperature/Humidity Sensor - 2x
- Resistors: 10kΩ, 1kΩ
- Jumper wires, breadboards
- 5V power supplies

### Software
- Raspberry Pi OS (latest)
- Python 3.9, 3.10, or 3.11 (Python 3.12+ not recommended)
- Node.js 16+
- Flutter SDK 3.0+
- Arduino IDE
- SQLite3 (included with Python)
- Mosquitto MQTT Broker

**Important**: Python 3.13 has compatibility issues with numpy and other packages. Use Python 3.11 or earlier.

## Raspberry Pi Setup

### 1. Install Operating System
```bash
# Flash Raspberry Pi OS to SD card using Raspberry Pi Imager
# Enable SSH and WiFi during setup
```

### 2. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. Install Dependencies
```bash
# Install Python and pip (use Python 3.11 or earlier)
sudo apt-get install python3.11 python3.11-pip python3.11-venv -y

# Or use system default (usually Python 3.9 on Raspberry Pi OS)
# sudo apt-get install python3 python3-pip python3-venv -y

# Verify Python version
python3 --version  # Should be 3.9, 3.10, or 3.11

# SQLite3 is included with Python - no separate installation needed

# Install Mosquitto MQTT Broker
sudo apt-get install mosquitto mosquitto-clients -y
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Install Node.js (for web dashboard)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 4. Setup Backend
```bash
cd raspberry-pi-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip, setuptools, and wheel first
pip install --upgrade pip setuptools wheel

# Install Python dependencies
# If you encounter numpy/tensorflow errors, see INSTALL_TROUBLESHOOTING.md
pip install -r requirements.txt

# Alternative: Use minimal requirements (without heavy ML libraries)
# pip install -r requirements-minimal.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Train ML model (optional)
cd ml_models
python train_model.py
cd ..
```

### 5. Start Backend
```bash
cd api
python main.py
```

Or use systemd service (see below).

## ESP8266 Setup

### 1. Install Arduino IDE
- Download from https://www.arduino.cc/en/software
- Install on your computer

### 2. Add ESP8266 Board Support
1. Open Arduino IDE
2. File → Preferences → Additional Board Manager URLs
3. Add: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
4. Tools → Board → Boards Manager
5. Search "ESP8266" → Install

### 3. Install Libraries
Sketch → Include Library → Manage Libraries → Install:
- PubSubClient (by Nick O'Leary)
- DHT sensor library (by Adafruit)
- ArduinoJson (by Benoit Blanchon)

### 4. Configure and Upload
1. Open `esp8266-sensors/pir_ultrasonic_dht22/sensor_node.ino`
2. Update WiFi credentials and MQTT server IP
3. Connect ESP8266 via USB
4. Select board: Tools → Board → NodeMCU 1.0 (ESP-12E Module)
5. Select port: Tools → Port
6. Upload: Sketch → Upload

### 5. Test
- Open Serial Monitor (115200 baud)
- Verify WiFi connection
- Check MQTT messages on broker

## Database Setup

### SQLite Configuration
```bash
# SQLite is file-based and doesn't require a separate service
# The database file will be created automatically on first run

# Database file location (default):
# ./fall_detection.db

# You can configure the database path in .env:
# DB_DIR=.
# DB_NAME=fall_detection.db
```

### Verify Database
```bash
# Check if database file exists (after first run)
ls -lh fall_detection.db

# View database structure (optional - requires sqlite3 CLI)
sqlite3 fall_detection.db ".tables"
```

## Web Dashboard Setup

### 1. Install Dependencies
```bash
cd web-dashboard/react-app
npm install
```

### 2. Configure
Create `.env` file:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 3. Run Development Server
```bash
npm start
```

Dashboard opens at http://localhost:3000

### 4. Build for Production
```bash
npm run build
# Serve with: npx serve -s build
```

## Mobile App Setup

### 1. Install Flutter
```bash
# Follow Flutter installation guide for your OS
# https://docs.flutter.dev/get-started/install
```

### 2. Setup Firebase
1. Create Firebase project at https://console.firebase.google.com
2. Add Android/iOS apps
3. Download configuration files:
   - `google-services.json` → `android/app/`
   - `GoogleService-Info.plist` → `ios/Runner/`

### 3. Install Dependencies
```bash
cd mobile-app/flutter-app
flutter pub get
```

### 4. Run
```bash
# Android
flutter run

# iOS (macOS only)
flutter run -d ios
```

## Configuration

### MQTT Broker (Mosquitto)
Edit `/etc/mosquitto/mosquitto.conf`:
```
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Create password file:
```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd admin
# Enter password
```

### Environment Variables
Update `.env` files in:
- `raspberry-pi-backend/.env`
- `web-dashboard/react-app/.env`

Key settings:
- SQLite database path (DB_DIR, DB_NAME)
- MQTT broker credentials
- Email SMTP settings
- FCM push notification keys
- API URLs

## Testing

### 1. Test MQTT Communication
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "#" -u admin -P your_password

# Publish test message
mosquitto_pub -h localhost -t "test/topic" -m "Hello" -u admin -P your_password
```

### 2. Test API
```bash
# Health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/api/statistics
```

### 3. Test Sensors
- ESP8266: Check serial monitor for readings
- Test fall detection by simulating inactivity (cover PIR sensor, place object near ultrasonic)
- Verify data appears in dashboard

### 4. Test Alerts
- Trigger fall detection
- Verify email sent
- Verify push notification received
- Check dashboard for event

## Troubleshooting

### ESP8266 Not Connecting
- Check WiFi credentials
- Verify MQTT broker IP address
- Check serial monitor for errors

### SQLite Database Issues
- Verify database file permissions
- Check database path in `.env`
- Ensure directory exists for database file
- Check disk space availability

### MQTT Messages Not Received
- Check broker is running: `sudo systemctl status mosquitto`
- Verify credentials
- Check firewall rules

### Dashboard Not Loading
- Verify API is running
- Check CORS settings
- Verify WebSocket connection

## Production Deployment

### Systemd Service (Raspberry Pi)
Create `/etc/systemd/system/fall-detection.service`:
```ini
[Unit]
Description=Fall Detection System API
After=network.target mosquitto.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/AI-driven-fall-detection/raspberry-pi-backend/api
Environment="PATH=/home/pi/AI-driven-fall-detection/raspberry-pi-backend/venv/bin"
ExecStart=/home/pi/AI-driven-fall-detection/raspberry-pi-backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fall-detection
sudo systemctl start fall-detection
sudo systemctl status fall-detection
```

## Support

For issues or questions, check:
- Documentation in `docs/` directory
- README files in each component
- GitHub issues (if applicable)

