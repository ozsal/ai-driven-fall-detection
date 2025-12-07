# Separate Sensor APIs and Frontend Integration

## Overview

Each sensor now has its **own dedicated API endpoint** and sends **separate WebSocket messages** to the frontend for easy filtering and display.

## API Endpoints

### 1. PIR Motion Sensor

**Endpoint:** `GET /api/sensors/pir`

**Query Parameters:**
- `device_id` (optional) - Filter by device ID
- `limit` (optional, default: 100) - Number of readings to return

**Example:**
```bash
# Get all PIR sensor readings
curl http://10.162.131.191:8000/api/sensors/pir

# Get PIR readings from specific device
curl http://10.162.131.191:8000/api/sensors/pir?device_id=ESP8266_NODE_01

# Get latest 10 PIR readings
curl http://10.162.131.191:8000/api/sensors/pir?limit=10
```

**Response:**
```json
[
  {
    "id": 1,
    "device_id": "ESP8266_NODE_01",
    "sensor_type": "pir",
    "timestamp": 1234567890,
    "data": {"motion_detected": true},
    "topic": "sensors/pir/ESP8266_NODE_01",
    "location": null,
    "received_at": "2024-12-06 18:30:00"
  }
]
```

### 2. Ultrasonic Distance Sensor

**Endpoint:** `GET /api/sensors/ultrasonic`

**Query Parameters:**
- `device_id` (optional) - Filter by device ID
- `limit` (optional, default: 100) - Number of readings to return

**Example:**
```bash
# Get all Ultrasonic sensor readings
curl http://10.162.131.191:8000/api/sensors/ultrasonic

# Get Ultrasonic readings from specific device
curl http://10.162.131.191:8000/api/sensors/ultrasonic?device_id=ESP8266_NODE_01

# Get latest 10 Ultrasonic readings
curl http://10.162.131.191:8000/api/sensors/ultrasonic?limit=10
```

**Response:**
```json
[
  {
    "id": 2,
    "device_id": "ESP8266_NODE_01",
    "sensor_type": "ultrasonic",
    "timestamp": 1234567891,
    "data": {"distance_cm": 25.5},
    "topic": "sensors/ultrasonic/ESP8266_NODE_01",
    "location": null,
    "received_at": "2024-12-06 18:30:01"
  }
]
```

### 3. DHT22 Temperature/Humidity Sensor

**Endpoint:** `GET /api/sensors/dht22`

**Query Parameters:**
- `device_id` (optional) - Filter by device ID
- `limit` (optional, default: 100) - Number of readings to return

**Example:**
```bash
# Get all DHT22 sensor readings
curl http://10.162.131.191:8000/api/sensors/dht22

# Get DHT22 readings from specific device
curl http://10.162.131.191:8000/api/sensors/dht22?device_id=ESP8266_NODE_01

# Get latest 10 DHT22 readings
curl http://10.162.131.191:8000/api/sensors/dht22?limit=10
```

**Response:**
```json
[
  {
    "id": 3,
    "device_id": "ESP8266_NODE_01",
    "sensor_type": "dht22",
    "timestamp": 1234567892,
    "data": {
      "temperature_c": 22.5,
      "humidity_percent": 45.0
    },
    "topic": "sensors/dht22/ESP8266_NODE_01",
    "location": null,
    "received_at": "2024-12-06 18:30:02"
  }
]
```

### 4. All Sensors (Generic Endpoint)

**Endpoint:** `GET /api/sensor-readings`

Still available for getting all sensors or filtering by sensor_type:
```bash
# Get all sensor readings
curl http://10.162.131.191:8000/api/sensor-readings

# Filter by sensor type
curl http://10.162.131.191:8000/api/sensor-readings?sensor_type=pir
```

## WebSocket Messages

### Separate Message Types

Each sensor sends a **dedicated message type** for easy frontend filtering:

#### PIR Sensor Messages
```json
{
  "type": "sensor_pir",
  "sensor_type": "pir",
  "device_id": "ESP8266_NODE_01",
  "timestamp": 1234567890,
  "data": {"motion_detected": true},
  "topic": "sensors/pir/ESP8266_NODE_01",
  "location": null
}
```

#### Ultrasonic Sensor Messages
```json
{
  "type": "sensor_ultrasonic",
  "sensor_type": "ultrasonic",
  "device_id": "ESP8266_NODE_01",
  "timestamp": 1234567891,
  "data": {"distance_cm": 25.5},
  "topic": "sensors/ultrasonic/ESP8266_NODE_01",
  "location": null
}
```

#### DHT22 Sensor Messages
```json
{
  "type": "sensor_dht22",
  "sensor_type": "dht22",
  "device_id": "ESP8266_NODE_01",
  "timestamp": 1234567892,
  "data": {
    "temperature_c": 22.5,
    "humidity_percent": 45.0
  },
  "topic": "sensors/dht22/ESP8266_NODE_01",
  "location": null
}
```

### Generic Message Type (Backward Compatibility)

Also sends generic `sensor_data` type for backward compatibility:
```json
{
  "type": "sensor_data",
  "sensor_type": "pir",
  "device_id": "ESP8266_NODE_01",
  "timestamp": 1234567890,
  "data": {"motion_detected": true},
  "topic": "sensors/pir/ESP8266_NODE_01",
  "location": null
}
```

## Frontend Integration

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://10.162.131.191:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  // Filter by message type for each sensor
  switch(message.type) {
    case 'sensor_pir':
      handlePIRData(message);
      break;
    case 'sensor_ultrasonic':
      handleUltrasonicData(message);
      break;
    case 'sensor_dht22':
      handleDHT22Data(message);
      break;
    case 'sensor_data':
      // Generic handler (backward compatibility)
      handleGenericSensorData(message);
      break;
  }
};
```

### Separate API Calls

```javascript
// Fetch PIR sensor data
async function fetchPIRData(deviceId = null) {
  const url = deviceId 
    ? `http://10.162.131.191:8000/api/sensors/pir?device_id=${deviceId}`
    : 'http://10.162.131.191:8000/api/sensors/pir';
  const response = await fetch(url);
  return await response.json();
}

// Fetch Ultrasonic sensor data
async function fetchUltrasonicData(deviceId = null) {
  const url = deviceId 
    ? `http://10.162.131.191:8000/api/sensors/ultrasonic?device_id=${deviceId}`
    : 'http://10.162.131.191:8000/api/sensors/ultrasonic';
  const response = await fetch(url);
  return await response.json();
}

// Fetch DHT22 sensor data
async function fetchDHT22Data(deviceId = null) {
  const url = deviceId 
    ? `http://10.162.131.191:8000/api/sensors/dht22?device_id=${deviceId}`
    : 'http://10.162.131.191:8000/api/sensors/dht22';
  const response = await fetch(url);
  return await response.json();
}
```

### React Component Example

```jsx
import { useState, useEffect } from 'react';

function SensorDashboard() {
  const [pirData, setPirData] = useState([]);
  const [ultrasonicData, setUltrasonicData] = useState([]);
  const [dht22Data, setDht22Data] = useState([]);

  // Fetch initial data
  useEffect(() => {
    fetchPIRData().then(setPirData);
    fetchUltrasonicData().then(setUltrasonicData);
    fetchDHT22Data().then(setDht22Data);
  }, []);

  // WebSocket for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://10.162.131.191:8000/ws');
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch(message.type) {
        case 'sensor_pir':
          setPirData(prev => [message, ...prev].slice(0, 100));
          break;
        case 'sensor_ultrasonic':
          setUltrasonicData(prev => [message, ...prev].slice(0, 100));
          break;
        case 'sensor_dht22':
          setDht22Data(prev => [message, ...prev].slice(0, 100));
          break;
      }
    };
    
    return () => ws.close();
  }, []);

  return (
    <div>
      <PIRSensorCard data={pirData} />
      <UltrasonicSensorCard data={ultrasonicData} />
      <DHT22SensorCard data={dht22Data} />
    </div>
  );
}
```

## API Summary

| Sensor | Endpoint | WebSocket Type | Data Format |
|--------|----------|----------------|-------------|
| PIR | `/api/sensors/pir` | `sensor_pir` | `{"motion_detected": true/false}` |
| Ultrasonic | `/api/sensors/ultrasonic` | `sensor_ultrasonic` | `{"distance_cm": 25.5}` |
| DHT22 | `/api/sensors/dht22` | `sensor_dht22` | `{"temperature_c": 22.5, "humidity_percent": 45.0}` |

## Benefits

✅ **Separate Endpoints** - Each sensor has its own dedicated API
✅ **Easy Filtering** - Frontend can subscribe to specific sensor types
✅ **Better Organization** - Clear separation of concerns
✅ **Real-time Updates** - Each sensor sends separate WebSocket messages
✅ **Backward Compatible** - Generic endpoints still work

## Testing

### Test PIR API
```bash
curl http://10.162.131.191:8000/api/sensors/pir?limit=5
```

### Test Ultrasonic API
```bash
curl http://10.162.131.191:8000/api/sensors/ultrasonic?limit=5
```

### Test DHT22 API
```bash
curl http://10.162.131.191:8000/api/sensors/dht22?limit=5
```

### Test WebSocket
```javascript
const ws = new WebSocket('ws://10.162.131.191:8000/ws');
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log('Received:', msg.type, msg);
};
```


