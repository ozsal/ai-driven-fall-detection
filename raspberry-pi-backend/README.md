# Raspberry Pi Backend

FastAPI backend for the Fall Detection System running on Raspberry Pi.

## Prerequisites

- Raspberry Pi 4 (or compatible)
- Python 3.8+
- MongoDB installed and running
- Mosquitto MQTT broker installed

## Installation

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv mongodb mosquitto mosquitto-clients
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Start MongoDB and Mosquitto:
```bash
sudo systemctl start mongod
sudo systemctl start mosquitto
```

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

