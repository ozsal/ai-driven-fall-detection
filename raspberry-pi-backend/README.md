# Raspberry Pi Backend

FastAPI backend for the Fall Detection System running on Raspberry Pi.

## Prerequisites

- Raspberry Pi 4 (or compatible)
- Python 3.9, 3.10, or 3.11 (Python 3.12+ may have compatibility issues)
- SQLite3 (included with Python)
- Mosquitto MQTT broker installed

**Important**: Python 3.13 is not recommended due to compatibility issues with numpy and other packages. Use Python 3.11 or earlier.

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
# For full installation (includes ML libraries)
pip install -r requirements.txt

# If you encounter issues with numpy/tensorflow, use minimal version:
# pip install -r requirements-minimal.txt
```

**Troubleshooting**: If you get errors installing numpy or tensorflow:
- Use Python 3.9, 3.10, or 3.11 (not 3.12+)
- Try: `pip install --upgrade pip setuptools wheel`
- Install numpy separately: `pip install numpy==1.24.3`
- For Raspberry Pi, consider using pre-built wheels: `pip install --only-binary :all: numpy`

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
- `sensors/pir/+`
- `sensors/ultrasonic/+`
- `sensors/dht22/+`
- `sensors/combined/+`
- `wearable/fall/+`
- `wearable/accelerometer/+`
- `devices/+/status`

## Training ML Model

```bash
cd ml_models
python train_model.py
```

## Production Deployment

For production, use a process manager like systemd or supervisor to keep the service running.

