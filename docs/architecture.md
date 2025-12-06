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
│  MongoDB Database                                               │
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
│  - wearable/accelerometer/{device_id}                           │
│  - alerts/fall/{device_id}                                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      SENSOR LAYER                                │
├──────────────────────┬──────────────────┬───────────────────────┤
│  ESP8266 Node 1      │  ESP8266 Node 2  │  Micro:bit Wearable   │
│  - PIR Sensor        │  - PIR Sensor    │  - Accelerometer      │
│  - Ultrasonic        │  - Ultrasonic    │  - TinyML Model       │
│  - DHT22             │  - DHT22         │  - BLE Communication  │
└──────────────────────┴──────────────────┴───────────────────────┘
```

## Component Details

### 1. ESP8266 Sensor Nodes
- **Function**: Monitor room environment
- **Sensors**: PIR (motion), HC-SR04 (distance), DHT22 (temp/humidity)
- **Communication**: WiFi + MQTT
- **Update Rate**: 1-2 seconds

### 2. Micro:bit Wearable
- **Function**: Personal fall detection
- **Sensors**: 3-axis accelerometer
- **Processing**: On-device TinyML inference
- **Communication**: BLE to gateway or direct WiFi

### 3. Raspberry Pi Backend
- **Function**: Central processing unit
- **Services**: 
  - MQTT Broker (Mosquitto)
  - FastAPI REST API
  - AI/ML Inference Engine
  - Alert Manager
- **Processing**: Multi-sensor fusion, fall severity scoring

### 4. Database (MongoDB)
- **Collections**:
  - `sensor_readings`: Time-series sensor data
  - `fall_events`: Detected fall incidents
  - `users`: User profiles and preferences
  - `devices`: Device configurations

### 5. Web Dashboard
- **Technology**: React + Chart.js
- **Features**: Real-time graphs, device management, alert history

### 6. Mobile App
- **Technology**: Flutter
- **Features**: Push notifications, emergency contacts, quick alerts

## Data Flow

1. **Sensor Data Collection**
   - ESP8266 nodes read sensors every 1-2 seconds
   - Micro:bit samples accelerometer at 50Hz
   - Data published to MQTT topics

2. **Data Processing**
   - Raspberry Pi subscribes to all MQTT topics
   - Data stored in MongoDB
   - Real-time analysis for fall detection

3. **Fall Detection Algorithm**
   - **Step 1**: Micro:bit accelerometer detects potential fall
   - **Step 2**: Verify with room sensors:
     - PIR: No motion detected (person on ground)
     - Ultrasonic: Distance < threshold (person near ground)
     - DHT22: Sudden temp/humidity change (door opening, etc.)
   - **Step 3**: Calculate fall severity score
   - **Step 4**: Trigger alerts if confirmed

4. **Alert System**
   - Push notification to mobile app
   - Email to registered contacts
   - Dashboard notification
   - Log event in database

## Fall Severity Scoring Model

The system uses a multi-factor scoring model:

```
Severity Score = (Accelerometer Score × 0.4) + 
                 (Room Verification Score × 0.3) + 
                 (Duration Score × 0.2) + 
                 (Environmental Score × 0.1)

Where:
- Accelerometer Score: Based on impact magnitude and pattern
- Room Verification Score: PIR inactivity + ultrasonic distance
- Duration Score: Time since last movement
- Environmental Score: Temperature/humidity changes
```

## Security Considerations

- MQTT authentication (username/password)
- TLS/SSL for MQTT communication
- API authentication (JWT tokens)
- Database access control
- Encrypted sensor data transmission

