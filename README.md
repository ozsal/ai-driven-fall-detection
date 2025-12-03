# AI-Driven Fall Detection System

A comprehensive IoT + AI-based fall detection system using Raspberry Pi, ESP8266 sensors, and Micro:bit wearable device.

## 🏗️ System Architecture

The system consists of:
- **ESP8266 Sensor Nodes**: PIR motion sensor, Ultrasonic sensor, DHT22 (temperature/humidity)
- **Micro:bit Wearable**: Accelerometer-based fall detection with TinyML
- **Raspberry Pi Backend**: MQTT broker, FastAPI server, AI inference engine
- **Database**: MongoDB for data storage
- **Frontend**: React web dashboard and Flutter mobile app
- **Alert System**: Push notifications and email alerts

## 📁 Project Structure

```
AI-driven-fall-detection/
├── esp8266-sensors/
│   ├── pir_ultrasonic_dht22/
│   └── mqtt_client/
├── microbit-wearable/
│   └── fall_detection/
├── raspberry-pi-backend/
│   ├── api/
│   ├── mqtt_broker/
│   ├── ml_models/
│   └── database/
├── web-dashboard/
│   └── react-app/
├── mobile-app/
│   └── flutter-app/
├── docs/
│   ├── architecture.md
│   ├── hardware_setup.md
│   └── flowcharts.md
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi 4 (or compatible)
- ESP8266 development boards (NodeMCU or similar)
- Micro:bit v2
- Sensors: PIR, HC-SR04 Ultrasonic, DHT22
- Python 3.8+
- Node.js 16+
- Flutter SDK

### Installation

1. **Raspberry Pi Setup**
   ```bash
   cd raspberry-pi-backend
   pip install -r requirements.txt
   ```

2. **ESP8266 Setup**
   - Install Arduino IDE
   - Install ESP8266 board support
   - Upload sensor node code

3. **Micro:bit Setup**
   - Use MakeCode or MicroPython
   - Flash wearable code

4. **Web Dashboard**
   ```bash
   cd web-dashboard/react-app
   npm install
   npm start
   ```

5. **Mobile App**
   ```bash
   cd mobile-app/flutter-app
   flutter pub get
   flutter run
   ```

## 🔧 Hardware Connections

See `docs/hardware_setup.md` for detailed pin mappings and connection diagrams.

## 📊 Features

- Multi-sensor fall detection
- Real-time monitoring dashboard
- Mobile app notifications
- Email alerts
- Fall severity scoring
- Historical data analysis
- Room-level verification

## 📖 Documentation

- [System Architecture](docs/architecture.md)
- [Hardware Setup](docs/hardware_setup.md)
- [Flowcharts](docs/flowcharts.md)

## 🤝 Contributing

This is a production-ready system. Follow the code structure and add features as needed.

## 📝 License

MIT License

