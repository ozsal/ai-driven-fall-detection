# Project Summary

## AI-Driven Fall Detection System

A comprehensive IoT + AI-based fall detection system with multi-sensor fusion, real-time monitoring, and alert capabilities.

## Project Structure

```
AI-driven-fall-detection/
├── README.md                          # Main project README
├── INSTALLATION.md                     # Complete installation guide
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore rules
│
├── docs/                              # Documentation
│   ├── architecture.md                # System architecture
│   ├── hardware_setup.md              # Hardware connections
│   └── flowcharts.md                  # System flowcharts
│
├── esp8266-sensors/                   # ESP8266 sensor nodes
│   ├── pir_ultrasonic_dht22/
│   │   ├── sensor_node.ino           # Main sensor code
│   │   └── config.h.example          # Configuration template
│   └── mqtt_client/
│       └── README.md                 # MQTT setup guide
│
├── raspberry-pi-backend/              # Raspberry Pi backend
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment variables template
│   ├── start.sh                       # Startup script
│   ├── README.md                      # Backend documentation
│   │
│   ├── api/                           # FastAPI application
│   │   ├── main.py                    # Main API server
│   │   └── __init__.py
│   │
│   ├── database/                      # Database layer
│   │   ├── sqlite_db.py              # SQLite database connection
│   │   └── __init__.py
│   │
│   ├── mqtt_broker/                   # MQTT client
│   │   ├── mqtt_client.py             # MQTT handler
│   │   └── __init__.py
│   │
│   ├── ml_models/                     # AI/ML models
│   │   ├── fall_detector.py           # Fall detection algorithm
│   │   ├── train_model.py             # Model training script
│   │   └── __init__.py
│   │
│   └── alerts/                        # Alert system
│       ├── alert_manager.py           # Alert manager
│       └── __init__.py
│
├── web-dashboard/                     # React web dashboard
│   └── react-app/
│       ├── package.json                # Node dependencies
│       ├── README.md                   # Dashboard guide
│       ├── public/
│       │   └── index.html
│       └── src/
│           ├── App.js                 # Main app component
│           ├── index.js                # Entry point
│           ├── config.js               # Configuration
│           ├── context/
│           │   └── WebSocketContext.js # WebSocket provider
│           └── components/
│               ├── Dashboard.js       # Dashboard view
│               ├── FallEvents.js      # Events list
│               ├── Devices.js          # Device management
│               ├── Settings.js        # Settings page
│               └── Navbar.js          # Navigation
│
└── mobile-app/                        # Flutter mobile app
    └── flutter-app/
        ├── pubspec.yaml                # Flutter dependencies
        ├── README.md                   # App guide
        └── lib/
            ├── main.dart              # App entry point
            ├── screens/
            │   ├── home_screen.dart   # Dashboard screen
            │   ├── events_screen.dart # Events screen
            │   └── settings_screen.dart # Settings screen
            ├── providers/
            │   └── fall_events_provider.dart # State management
            └── services/
                ├── api_service.dart   # API client
                └── notification_service.dart # Push notifications
```

## Key Features

### 1. Multi-Sensor Fall Detection
- **Room Sensors (ESP8266)**: PIR motion, ultrasonic distance, temperature/humidity
- **Multi-Sensor Fusion**: Combines PIR, ultrasonic, and environmental sensors for accurate detection
- **Pattern Analysis**: Detects fall patterns based on motion inactivity and proximity to ground

### 2. AI/ML Fall Detection
- **Severity Scoring**: 0-10 scale based on multiple factors
- **Multi-Sensor Verification**: Cross-validates fall detection using multiple room sensors
- **Pattern Recognition**: Detects fall patterns vs. normal activities

### 3. Real-Time Monitoring
- **Web Dashboard**: React-based interface with live updates
- **Mobile App**: Flutter app with push notifications
- **WebSocket**: Real-time data streaming

### 4. Alert System
- **Email Alerts**: SMTP-based email notifications
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **Dashboard Alerts**: Real-time visual alerts
- **Multi-Channel**: Simultaneous alerts across all channels

### 5. Data Management
- **SQLite Database**: File-based time-series sensor data storage
- **Event Logging**: Complete fall event history
- **Device Management**: Track and monitor all devices

## Technology Stack

### Hardware
- **Raspberry Pi 4**: Central processing unit
- **ESP8266 NodeMCU**: Sensor nodes (2x recommended for multiple rooms)
- **Sensors**: PIR (HC-SR501), HC-SR04 Ultrasonic, DHT22

### Software
- **Backend**: Python 3.8+, FastAPI, SQLite3, Mosquitto MQTT
- **Web Dashboard**: React, Chart.js, Material-UI
- **Mobile App**: Flutter, Firebase
- **ML/AI**: scikit-learn, TensorFlow (optional)

### Communication
- **MQTT**: Sensor data transmission
- **WebSocket**: Real-time dashboard updates
- **REST API**: HTTP endpoints
- **WiFi**: Network connectivity

## System Flow

1. **Data Collection**
   - ESP8266 nodes read sensors every 2 seconds
   - PIR motion, ultrasonic distance, DHT22 temperature/humidity
   - Data published to MQTT topics

2. **Data Processing**
   - Raspberry Pi receives MQTT messages
   - Data stored in SQLite database
   - Real-time analysis for fall patterns

3. **Fall Detection**
   - Analyze room sensor patterns (PIR inactivity, ultrasonic proximity)
   - Detect extended periods of no motion
   - Verify with multiple sensor readings
   - AI model calculates severity score
   - Multi-sensor fusion confirms fall

4. **Alert Generation**
   - Severity score above threshold triggers alerts
   - Email sent to emergency contacts
   - Push notification to mobile app
   - Dashboard shows real-time alert

5. **Event Logging**
   - Fall event saved to database
   - Historical data available for analysis
   - User can acknowledge events

## Installation

See [INSTALLATION.md](INSTALLATION.md) for complete setup instructions.

Quick start:
1. Setup Raspberry Pi with SQLite and Mosquitto
2. Upload ESP8266 sensor code to all nodes
3. Configure environment variables
5. Start backend API
6. Launch web dashboard
7. Install mobile app

## Configuration

Key configuration files:
- `raspberry-pi-backend/.env` - Backend settings
- `esp8266-sensors/.../sensor_node.ino` - WiFi and MQTT settings
- `web-dashboard/react-app/.env` - API URLs
- `mobile-app/flutter-app/lib/services/api_service.dart` - API endpoint

## Testing

1. **Hardware Test**: Verify all sensors reading correctly
2. **MQTT Test**: Check messages on broker
3. **API Test**: Use curl or Postman
4. **Dashboard Test**: Verify real-time updates
5. **Alert Test**: Trigger fall and verify notifications

## Production Deployment

- Use systemd for service management
- Configure firewall rules
- Enable SSL/TLS for MQTT
- Set up reverse proxy for API
- Configure backup for SQLite database file
- Monitor system health

## Security Considerations

- MQTT authentication (username/password)
- TLS/SSL for encrypted communication
- API authentication (JWT tokens)
- Database access control
- Secure credential storage

## Future Enhancements

- Machine learning model training with real data
- Additional sensor types
- Cloud deployment option
- Multi-user support
- Advanced analytics
- Integration with emergency services

## License

MIT License - See [LICENSE](LICENSE) file

## Support

For detailed documentation, see:
- [System Architecture](docs/architecture.md)
- [Hardware Setup](docs/hardware_setup.md)
- [Flowcharts](docs/flowcharts.md)
- Component-specific README files

