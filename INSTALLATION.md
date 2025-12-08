# Complete Installation Guide
## AI-Driven Fall Detection System

This comprehensive guide covers the complete installation and setup of all system components.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Hardware Setup](#hardware-setup)
3. [Raspberry Pi Backend Setup](#raspberry-pi-backend-setup)
4. [ESP8266 Sensor Node Setup](#esp8266-sensor-node-setup)
5. [MQTT Broker Configuration](#mqtt-broker-configuration)
6. [Database Setup](#database-setup)
7. [Authentication & Security Setup](#authentication--security-setup)
8. [ML Models Training (Optional)](#ml-models-training-optional)
9. [Web Dashboard Setup](#web-dashboard-setup)
10. [Systemd Service Setup (Production)](#systemd-service-setup-production)
11. [Testing & Verification](#testing--verification)
12. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Hardware Components

- **Raspberry Pi 4** (4GB RAM recommended)
  - MicroSD card (32GB+)
  - USB-C power supply (5V, 3A)
  - Ethernet cable or WiFi adapter

- **ESP8266 NodeMCU v1.0** (2x recommended for multiple rooms)
  - USB cable for programming
  - 5V power supply (optional, can use USB)

- **Sensors** (per ESP8266 node):
  - PIR Motion Sensor (HC-SR501) - 1x
  - Ultrasonic Distance Sensor (HC-SR04) - 1x
  - DHT22 Temperature/Humidity Sensor - 1x
  - Active Buzzer (for actuator) - 1x

- **Additional Components**:
  - 10kΩ resistor (for DHT22 pull-up)
  - 1kΩ and 2kΩ resistors (for HC-SR04 voltage divider, optional)
  - Breadboard
  - Jumper wires
  - USB cables

### Software Requirements

- **Raspberry Pi OS** (latest, based on Debian)
- **Python 3.11 or 3.12** (Python 3.13 has compatibility issues)
- **Node.js 16+** (for web dashboard)
- **Arduino IDE 1.8+** (for ESP8266 programming)
- **SQLite3** (included with Python)
- **Mosquitto MQTT Broker**

---

## Hardware Setup

### ESP8266 Sensor Node Circuit

#### Pin Connections

```
ESP8266 NodeMCU Pinout:
┌─────────────────────────────────────┐
│  VIN ──────────────── 5V Power      │
│  GND ──────────────── Ground         │
│                                     │
│  D5 (GPIO14) ──────── PIR OUT       │
│  D6 (GPIO12) ──────── Ultrasonic TRIG│
│  D7 (GPIO13) ──────── Ultrasonic ECHO│
│  D2 (GPIO4)  ──────── DHT22 DATA    │
│  D4 (GPIO2)  ──────── Built-in LED  │
│  D1 (GPIO5)  ──────── Buzzer (+)    │
│                                     │
│  3.3V ─────────────── DHT22 VCC     │
│  GND  ─────────────── Common Ground │
└─────────────────────────────────────┘
```

#### Detailed Connections

**PIR Motion Sensor (HC-SR501)**:
- VCC → 5V (NodeMCU)
- GND → GND (NodeMCU)
- OUT → GPIO14 (D5)

**Ultrasonic Sensor (HC-SR04)**:
- VCC → 5V (NodeMCU)
- GND → GND (NodeMCU)
- TRIG → GPIO12 (D6)
- ECHO → GPIO13 (D7)
- **Note**: Echo pin is 5V, ESP8266 GPIO is 3.3V tolerant. Use voltage divider if needed.

**DHT22 Sensor**:
- VCC → 3.3V (NodeMCU)
- GND → GND (NodeMCU)
- DATA → GPIO4 (D2)
- **Pull-up Resistor**: 10kΩ between DATA and 3.3V

**Buzzer (Actuator)**:
- Positive (+) → GPIO5 (D1)
- Negative (-) → GND

### Physical Assembly

1. Place ESP8266 NodeMCU on breadboard
2. Connect all sensors following the pin mapping above
3. Ensure proper power connections (3.3V for DHT22, 5V for PIR and Ultrasonic)
4. Connect pull-up resistor for DHT22
5. Double-check all connections before powering on

**Photograph**: Complete ESP8266 sensor node assembly

---

## Raspberry Pi Backend Setup

### Step 1: Install Operating System

1. Download Raspberry Pi Imager from https://www.raspberrypi.org/software/
2. Flash Raspberry Pi OS to microSD card
3. Enable SSH and configure WiFi during setup (or use Ethernet)
4. Boot Raspberry Pi and connect via SSH

### Step 2: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 3: Install System Dependencies

```bash
# Install Python 3.11 (or use system default if 3.9+)
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Or use system default
sudo apt install python3 python3-pip python3-venv -y

# Verify Python version
python3 --version  # Should be 3.9, 3.10, or 3.11

# Install Mosquitto MQTT Broker
sudo apt install mosquitto mosquitto-clients -y

# Install Node.js (for web dashboard)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
node --version
npm --version
```

### Step 4: Clone/Download Project

```bash
cd ~
git clone <repository-url> ai-driven-fall-detection
# OR download and extract project files
cd ai-driven-fall-detection
```

### Step 5: Setup Python Virtual Environment

```bash
cd raspberry-pi-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate    # On Windows

# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
```

### Step 6: Install Python Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# If you encounter numpy/tensorflow errors, use minimal requirements:
# pip install -r requirements-minimal.txt
```

**Expected packages installed**:
- fastapi, uvicorn
- paho-mqtt
- aiosqlite
- scikit-learn, numpy, pandas
- python-jose, passlib, bcrypt
- websockets
- And more...

### Step 7: Configure Environment Variables

```bash
# Create .env file (if not exists)
cd raspberry-pi-backend
cp .env.example .env  # If example exists
# OR create new .env file

# Edit .env file
nano .env
```

**Required .env variables**:
```env
# Database
DB_DIR=.
DB_NAME=fall_detection.db

# MQTT Broker
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=esp8266_user
MQTT_PASSWORD=your_password_here

# JWT Secret (generate using generate_jwt_secret.py)
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 8: Generate JWT Secret Key

```bash
cd raspberry-pi-backend
python generate_jwt_secret.py

# Copy the generated secret to .env file
```

---

## ESP8266 Sensor Node Setup

### Step 1: Install Arduino IDE

1. Download Arduino IDE from https://www.arduino.cc/en/software
2. Install on your computer (Windows/Mac/Linux)

### Step 2: Add ESP8266 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. In "Additional Board Manager URLs", add:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
4. Go to **Tools → Board → Boards Manager**
5. Search for "ESP8266" and install "esp8266 by ESP8266 Community"
6. Wait for installation to complete

### Step 3: Install Required Libraries

Go to **Sketch → Include Library → Manage Libraries** and install:

- **PubSubClient** (by Nick O'Leary) - Version 2.8.0
- **DHT sensor library** (by Adafruit) - Version 1.4.4
- **ArduinoJson** (by Benoit Blanchon) - Version 6.x

### Step 4: Configure WiFi and MQTT Settings

1. Open `esp8266-sensors/pir_ultrasonic_dht22/sensor_node.ino`
2. Create `config.h` file (or use `config.h.example`):
   ```cpp
   #ifndef CONFIG_H
   #define CONFIG_H
   
   // WiFi Configuration
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   
   // MQTT Configuration
   const char* mqtt_server = "192.168.1.100";  // Raspberry Pi IP
   const int mqtt_port = 1883;
   const char* mqtt_user = "esp8266_user";
   const char* mqtt_password = "your_password_here";
   const char* mqtt_client_id = "ESP8266_NODE_01";
   
   // Device Configuration
   const char* device_id = "ESP8266_NODE_01";
   const char* location = "Living_Room";
   
   #endif
   ```

### Step 5: Upload Code to ESP8266

1. Connect ESP8266 to computer via USB
2. In Arduino IDE:
   - Select board: **Tools → Board → NodeMCU 1.0 (ESP-12E Module)**
   - Select port: **Tools → Port → [Your COM port]**
   - Select upload speed: **Tools → Upload Speed → 115200**
3. Click **Upload** button (or **Sketch → Upload**)
4. Wait for upload to complete

### Step 6: Verify Upload

1. Open **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. You should see:
   ```
   === ESP8266 Multi-Sensor Node Starting ===
   Device ID: ESP8266_NODE_01
   Location: Living_Room
   Connecting to WiFi...
   WiFi connected
   MQTT connected
   ```

---

## MQTT Broker Configuration

### Step 1: Start Mosquitto Service

```bash
# Start Mosquitto
sudo systemctl start mosquitto
sudo systemctl enable mosquitto  # Enable on boot

# Verify it's running
sudo systemctl status mosquitto
```

### Step 2: Configure Authentication

```bash
# Create password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd esp8266_user
# Enter password when prompted

# Add backend user (if needed)
sudo mosquitto_passwd /etc/mosquitto/passwd backend_user
```

### Step 3: Configure Access Control

```bash
# Edit ACL file
sudo nano /etc/mosquitto/acl
```

Add the following:
```
user esp8266_user
topic readwrite sensors/+/+
topic read alerts/fall/+

user backend_user
topic readwrite #
```

### Step 4: Configure Mosquitto

```bash
# Edit main config file
sudo nano /etc/mosquitto/mosquitto.conf
```

Add/modify:
```
listener 1883
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl
```

### Step 5: Restart Mosquitto

```bash
sudo systemctl restart mosquitto
sudo systemctl status mosquitto
```

### Step 6: Test MQTT Connection

```bash
# Subscribe to all topics (in one terminal)
mosquitto_sub -h localhost -t "#" -u esp8266_user -P your_password

# Publish test message (in another terminal)
mosquitto_pub -h localhost -t "test/topic" -m "Hello" -u esp8266_user -P your_password
```

---

## Database Setup

### Automatic Setup (Recommended)

The database is **automatically initialized** when you start the backend:

```bash
cd raspberry-pi-backend
source venv/bin/activate
python api/main.py
```

The database file `fall_detection.db` will be created automatically.

### Manual Setup (Optional)

If you want to initialize the database manually:

```bash
cd raspberry-pi-backend
source venv/bin/activate
python setup_database.py
```

### Verify Database

```bash
# Check database file exists
ls -lh fall_detection.db

# View database structure (requires sqlite3 CLI)
sqlite3 fall_detection.db ".tables"

# Expected tables:
# - sensor_readings
# - alerts
# - fall_events
# - devices
# - sensors
# - users
```

---

## Authentication & Security Setup

### Step 1: Generate JWT Secret

```bash
cd raspberry-pi-backend
python generate_jwt_secret.py
```

Copy the generated secret to `.env` file:
```env
JWT_SECRET_KEY=<generated_secret>
```

### Step 2: Create Admin User

The system uses SQLite for user storage. Create an admin user:

```bash
cd raspberry-pi-backend
source venv/bin/activate
python -c "
from auth.database import create_user, hash_password
import asyncio

async def setup():
    await create_user(
        username='admin',
        email='admin@example.com',
        password=hash_password('admin123'),
        role='admin'
    )
    print('Admin user created')

asyncio.run(setup())
"
```

### Step 3: Verify Authentication

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should return JWT token
```

---

## ML Models Training (Optional)

### Step 1: Train Models

```bash
cd raspberry-pi-backend/ml_models
source ../venv/bin/activate
python train_alert_models.py
```

This will create:
- `models/temperature_anomaly.pkl`
- `models/fire_risk_model.pkl`
- `models/motion_anomaly.pkl`
- Feature scalers for each model
- Metadata files

### Step 2: Verify Models

```bash
ls -lh models/
# Should see .pkl files and .metadata.json files
```

The AlertEngine will automatically load these models on startup.

---

## Web Dashboard Setup

### Step 1: Install Dependencies

```bash
cd web-dashboard/react-app
npm install
```

### Step 2: Configure Environment

Create `.env` file:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### Step 3: Start Development Server

```bash
npm start
```

Dashboard will open at http://localhost:3000

### Step 4: Build for Production

```bash
npm run build

# Serve with:
npx serve -s build
# OR deploy to web server
```

---

## Systemd Service Setup (Production)

### Automatic Setup

```bash
cd raspberry-pi-backend
chmod +x setup_systemd_service.sh
sudo ./setup_systemd_service.sh
```

### Manual Setup

1. Copy service file:
```bash
sudo cp raspberry-pi-backend/fall-detection.service /etc/systemd/system/
```

2. Edit service file (update paths):
```bash
sudo nano /etc/systemd/system/fall-detection.service
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fall-detection
sudo systemctl start fall-detection
sudo systemctl status fall-detection
```

### Service Management

```bash
sudo systemctl start fall-detection    # Start
sudo systemctl stop fall-detection     # Stop
sudo systemctl restart fall-detection  # Restart
sudo systemctl status fall-detection   # Status
sudo journalctl -u fall-detection -f  # View logs
```

---

## Testing & Verification

### Test 1: MQTT Communication

```bash
# Subscribe to sensor topics
mosquitto_sub -h localhost -t "sensors/#" -u esp8266_user -P your_password

# You should see sensor data from ESP8266 nodes
```

### Test 2: Backend API

```bash
# Health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/api/statistics

# Get sensor readings (requires authentication)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/sensors/readings
```

### Test 3: Database Storage

```bash
# Check database file
ls -lh fall_detection.db

# Query sensor readings
sqlite3 fall_detection.db "SELECT COUNT(*) FROM sensor_readings;"
```

### Test 4: Alert Generation

1. Trigger alert condition (e.g., high temperature)
2. Check database:
```bash
sqlite3 fall_detection.db "SELECT * FROM alerts ORDER BY id DESC LIMIT 5;"
```
3. Check dashboard for alerts

### Test 5: Actuator Control

1. Trigger fall detection
2. Verify MQTT command sent to actuator topic
3. Verify buzzer activates

---

## Troubleshooting

### ESP8266 Not Connecting to WiFi

- Check WiFi credentials in `config.h`
- Verify signal strength
- Check serial monitor for error messages
- Ensure 2.4GHz WiFi (ESP8266 doesn't support 5GHz)

### ESP8266 Not Connecting to MQTT

- Verify MQTT broker IP address
- Check MQTT credentials
- Verify broker is running: `sudo systemctl status mosquitto`
- Check firewall rules (port 1883)

### DHT22 Sensor Reading Failures

- Check wiring (DATA pin, pull-up resistor)
- Verify power supply (3.3V)
- Add 2-second delay after initialization
- Check sensor is not damaged

### Backend Not Starting

- Check Python version: `python3 --version`
- Verify virtual environment is activated
- Check all dependencies installed: `pip list`
- Check `.env` file exists and is configured
- View error logs: `python api/main.py` (run in foreground)

### Database Issues

- Verify database file permissions
- Check disk space: `df -h`
- Verify database path in `.env`
- Check SQLite version: `sqlite3 --version`

### MQTT Messages Not Received

- Verify broker is running: `sudo systemctl status mosquitto`
- Check ACL permissions
- Verify credentials match
- Test with mosquitto_sub/mosquitto_pub

### Dashboard Not Loading

- Verify backend API is running
- Check CORS settings in backend
- Verify WebSocket connection
- Check browser console for errors
- Verify API URL in `.env`

### Authentication Issues

- Verify JWT_SECRET_KEY in `.env`
- Check user exists in database
- Verify password hashing
- Check token expiration time

---

## Quick Start Checklist

- [ ] Hardware assembled (ESP8266 + sensors)
- [ ] Raspberry Pi OS installed and updated
- [ ] Python virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] JWT secret generated
- [ ] MQTT broker configured and running
- [ ] Database initialized
- [ ] ESP8266 code uploaded
- [ ] ESP8266 connected to WiFi and MQTT
- [ ] Backend server started
- [ ] Web dashboard running
- [ ] Sensor data appearing in database
- [ ] Alerts generating correctly
- [ ] Systemd service configured (production)

---

## Support

For additional help:
- Check component-specific README files
- Review documentation in `docs/` directory
- Check GitHub issues (if applicable)
- Review error logs: `sudo journalctl -u fall-detection -f`

---

**Installation Complete!** Your AI-Driven Fall Detection System should now be fully operational.
