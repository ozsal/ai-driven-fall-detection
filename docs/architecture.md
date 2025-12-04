# System Architecture

## Overview

The AI-Driven Fall Detection System uses a distributed IoT architecture with multiple sensor nodes, a central processing unit, and user interfaces.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                     │
├─────────────────────────────┬───────────────────────────────────┤
│   Web Dashboard (React)     │   Mobile App (Flutter)            │
│   - Real-time monitoring     │   - Push notifications            │
│   - Historical data          │   - Alert management              │
│   - Device management        │   - Emergency contacts            │
└──────────────┬──────────────┴──────────────┬────────────────────┘
               │                              │
               └──────────────┬───────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    APPLICATION LAYER                             │
├──────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Raspberry Pi)                                 │
│  - REST API endpoints                                           │
│  - MQTT message handling                                        │
│  - AI/ML inference engine                                       │
│  - Alert management                                             │
│  - Data aggregation                                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      DATA LAYER                                  │
├──────────────────────────────────────────────────────────────────┤
│  SQLite Database                                                │
│  - Sensor readings                                              │
│  - Fall events                                                  │
│  - User profiles                                                │
│  - Device configurations                                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    COMMUNICATION LAYER                           │
├──────────────────────────────────────────────────────────────────┤
│  MQTT Broker (Mosquitto)                                        │
│  Topics:                                                        │
│  - sensors/pir/{device_id}                                      │
│  - sensors/ultrasonic/{device_id}                               │
│  - sensors/dht22/{device_id}                                    │
│  - sensors/combined/{device_id}                                 │
│  - devices/{device_id}/status                                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      SENSOR LAYER                                │
├──────────────────────┬──────────────────┐
│  ESP8266 Node 1      │  ESP8266 Node 2  │
│  - PIR Sensor        │  - PIR Sensor    │
│  - Ultrasonic        │  - Ultrasonic    │
│  - DHT22             │  - DHT22         │
└──────────────────────┴──────────────────┘
```

## Component Details

### 1. ESP8266 Sensor Nodes
- **Function**: Monitor room environment
- **Sensors**: PIR (motion), HC-SR04 (distance), DHT22 (temp/humidity)
- **Communication**: WiFi + MQTT
- **Update Rate**: 1-2 seconds

### 2. Raspberry Pi Backend
- **Function**: Central processing unit
- **Services**: 
  - MQTT Broker (Mosquitto)
  - FastAPI REST API
  - AI/ML Inference Engine
  - Alert Manager
- **Processing**: Multi-sensor fusion, fall severity scoring

### 3. Database (SQLite)
- **Tables**:
  - `sensor_readings`: Time-series sensor data
  - `fall_events`: Detected fall incidents
  - `users`: User profiles and preferences
  - `devices`: Device configurations
  - `alert_logs`: Alert delivery logs

### 4. Web Dashboard
- **Technology**: React + Chart.js
- **Features**: Real-time graphs, device management, alert history

### 5. Mobile App
- **Technology**: Flutter
- **Features**: Push notifications, emergency contacts, quick alerts

## Data Flow

1. **Sensor Data Collection**
   - ESP8266 nodes read sensors every 1-2 seconds
   - PIR motion, ultrasonic distance, and DHT22 temperature/humidity data
   - Data published to MQTT topics

2. **Data Processing**
   - Raspberry Pi subscribes to all MQTT topics
   - Data stored in SQLite database file
   - Real-time analysis for fall detection

3. **Fall Detection Algorithm**
   - **Step 1**: Analyze room sensor patterns:
     - PIR: No motion detected for extended period (person on ground)
     - Ultrasonic: Distance < threshold (person near ground)
     - DHT22: Sudden temp/humidity change (door opening, movement, etc.)
   - **Step 2**: Calculate fall severity score based on sensor fusion
   - **Step 3**: Verify with multiple sensor readings
   - **Step 4**: Trigger alerts if fall detected

4. **Alert System**
   - Push notification to mobile app
   - Email to registered contacts
   - Dashboard notification
   - Log event in database

## Fall Severity Scoring Model

The system uses a multi-factor scoring model:

```
Severity Score = (Room Verification Score × 0.5) + 
                 (Duration Score × 0.3) + 
                 (Environmental Score × 0.2)

Where:
- Room Verification Score: PIR inactivity + ultrasonic distance (0-10)
- Duration Score: Time since last movement detected (0-10)
- Environmental Score: Temperature/humidity changes indicating activity (0-10)
```

## Security Considerations

- MQTT authentication (username/password)
- TLS/SSL for MQTT communication
- API authentication (JWT tokens)
- Database access control
- Encrypted sensor data transmission

