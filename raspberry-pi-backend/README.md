# Raspberry Pi Backend

FastAPI backend for the Fall Detection System running on Raspberry Pi.

## Prerequisites

- Raspberry Pi 4 (or compatible)
- Python 3.11 or 3.12 (recommended)
- SQLite3 (included with Python)
- Mosquitto MQTT broker installed

**Recommended**: Python 3.12 with NumPy 1.26.4 (optimal balance of features and stability)
**Alternative**: Python 3.11 (most stable for Raspberry Pi)
**Not Recommended**: Python 3.13 (compatibility issues with some packages)

## Installation

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv mosquitto mosquitto-clients
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
# Upgrade pip, setuptools, and wheel first
pip install --upgrade pip setuptools wheel

# For Python 3.12 (recommended):
pip install -r requirements-python312.txt
# OR use main requirements.txt (optimized for 3.12)
pip install -r requirements.txt

# For Python 3.11:
pip install -r requirements-python311.txt

# If you encounter issues, use minimal version (no ML libraries):
# pip install -r requirements-minimal.txt
```

**Package Versions for Python 3.12:**
- NumPy: 1.26.4 (stable, well-tested)
- scikit-learn: 1.3.2
- pandas: 2.1.4

See `PYTHON312_SETUP.md` for detailed Python 3.12 setup instructions.

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Start Mosquitto:
```bash
sudo systemctl start mosquitto
```

Note: SQLite is file-based and doesn't require a separate service.

## Running

```bash
cd api
python main.py
```

Or use the start script:
```bash
chmod +x start.sh
./start.sh
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/devices` - List all devices
- `GET /api/sensor-readings` - Get sensor readings
- `GET /api/fall-events` - Get fall events
- `GET /api/fall-events/{event_id}` - Get specific event
- `POST /api/fall-events/{event_id}/acknowledge` - Acknowledge event
- `GET /api/statistics` - Get system statistics
- `WS /ws` - WebSocket for real-time updates

## MQTT Topics

The backend subscribes to:
- `sensors/pir/+` - PIR motion sensor data
- `sensors/ultrasonic/+` - Ultrasonic distance sensor data
- `sensors/dht22/+` - DHT22 temperature/humidity data
- `sensors/combined/+` - Combined sensor readings from ESP8266 nodes
- `devices/+/status` - Device status updates

## Training ML Model

```bash
cd ml_models
python train_model.py
```

## Production Deployment

For production, use a process manager like systemd or supervisor to keep the service running.

