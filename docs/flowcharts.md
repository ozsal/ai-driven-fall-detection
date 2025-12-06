# System Flowcharts

## Main System Flow

```
┌─────────────────┐
│   System Start  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Initialize All Components   │
│ - ESP8266 Nodes             │
│ - Micro:bit Wearable        │
│ - Raspberry Pi Backend      │
│ - Database                  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Connect to WiFi/MQTT        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Start Sensor Reading Loop    │
└────────┬────────────────────┘
         │
         └──────────────────────┐
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Continuous Monitoring │
                    └───────────────────────┘
```

## Fall Detection Flow

```
┌─────────────────────────────────────────┐
│  Micro:bit Accelerometer Reading        │
│  (50Hz sampling rate)                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  TinyML Model Inference                  │
│  - Extract features (acceleration,      │
│    jerk, orientation)                   │
│  - Run inference                         │
└──────────────┬──────────────────────────┘
               │
               ▼
      ┌────────────────┐
      │ Fall Detected? │
      └───┬────────┬───┘
          │        │
         NO       YES
          │        │
          │        ▼
          │  ┌─────────────────────────────┐
          │  │ Publish to MQTT             │
          │  │ Topic: wearable/fall/{id}   │
          │  └──────────────┬──────────────┘
          │                 │
          │                 ▼
          │  ┌─────────────────────────────┐
          │  │ Raspberry Pi Receives Alert │
          │  └──────────────┬──────────────┘
          │                 │
          │                 ▼
          │  ┌─────────────────────────────┐
          │  │ Room Verification Process   │
          │  └──────────────┬──────────────┘
          │                 │
          │                 ▼
          │  ┌─────────────────────────────┐
          │  │ Check PIR Sensor            │
          │  │ - Motion detected?          │
          │  └──────────────┬──────────────┘
          │                 │
          │                 ▼
          │  ┌─────────────────────────────┐
          │  │ Check Ultrasonic Sensor      │
          │  │ - Distance < threshold?      │
          │  └──────────────┬──────────────┘
          │                 │
          │                 ▼
          │  ┌─────────────────────────────┐
          │  │ Check DHT22 Sensor          │
          │  │ - Temp/Humidity change?     │
          │  └──────────────┬──────────────┘
          │                 │
          │                 ▼
          │  ┌─────────────────────────────┐
          │  │ Calculate Severity Score    │
          │  └──────────────┬──────────────┘
          │                 │
          │                 ▼
          │  ┌─────────────────────────────┐
          │  │ Score > Threshold?          │
          │  └───┬──────────────────────┬───┘
          │      │                     │
          │     NO                    YES
          │      │                     │
          │      │                     ▼
          │      │         ┌─────────────────────────┐
          │      │         │ Trigger Alert System    │
          │      │         │ - Push notification     │
          │      │         │ - Email alert           │
          │      │         │ - Dashboard update      │
          │      │         │ - Log to database       │
          │      │         └─────────────────────────┘
          │      │
          │      └─────────────────────┐
          │                            │
          └────────────────────────────┘
               │
               ▼
      ┌──────────────────────┐
      │ Continue Monitoring  │
      └──────────────────────┘
```

## ESP8266 Sensor Node Flow

```
┌─────────────────────┐
│  ESP8266 Boot       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│ Initialize WiFi Connection  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Connect to MQTT Broker      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Initialize Sensors           │
│ - PIR (GPIO14)              │
│ - Ultrasonic (GPIO12/13)    │
│ - DHT22 (GPIO4)             │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Main Loop (Every 2 seconds) │
└──────────┬──────────────────┘
           │
           ├──────────────────────────┐
           │                          │
           ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐
│ Read PIR Sensor     │    │ Read Ultrasonic     │
│ - Motion state      │    │ - Distance (cm)     │
└──────────┬──────────┘    └──────────┬──────────┘
           │                          │
           └──────────┬───────────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ Read DHT22          │
           │ - Temperature (°C)  │
           │ - Humidity (%)      │
           └──────────┬──────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ Create JSON Message │
           │ {                   │
           │   device_id,        │
           │   timestamp,        │
           │   pir_motion,       │
           │   distance,         │
           │   temperature,      │
           │   humidity          │
           │ }                   │
           └──────────┬──────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ Publish to MQTT      │
           │ Topic: sensors/...   │
           └──────────┬──────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │ Wait 2 seconds      │
           └──────────┬──────────┘
                      │
                      └──────────┐
                                  │
                                  ▼
                      ┌─────────────────────┐
                      │ Continue Loop       │
                      └─────────────────────┘
```

## Alert System Flow

```
┌─────────────────────────────┐
│ Fall Event Confirmed        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Calculate Severity Score    │
│ - Low (0-3)                 │
│ - Medium (4-6)              │
│ - High (7-10)               │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Save Event to Database      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Get User Preferences        │
│ - Notification settings     │
│ - Emergency contacts        │
└──────────┬──────────────────┘
           │
           ├──────────────────────┬──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Push Notification│  │ Email Alert      │  │ Dashboard Update │
│ - Mobile app     │  │ - Primary contact│  │ - Real-time alert│
│ - High priority  │  │ - Secondary      │  │ - Event log      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
           │                      │                      │
           └──────────────────────┴──────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Log Alert Status        │
                    │ - Sent timestamp        │
                    │ - Delivery status       │
                    └─────────────────────────┘
```

## Data Processing Flow

```
┌─────────────────────────────┐
│ MQTT Message Received       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Parse JSON Payload          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Validate Data               │
│ - Check ranges              │
│ - Verify device ID          │
│ - Timestamp validation      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Store in MongoDB            │
│ Collection: sensor_readings │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Update Real-time Cache      │
│ (For dashboard)             │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Run Analysis                │
│ - Pattern detection         │
│ - Anomaly detection         │
│ - Trend analysis            │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Trigger Actions if Needed   │
│ - Alerts                    │
│ - Automated responses        │
└─────────────────────────────┘
```

## Database Schema Flow

```
┌─────────────────────────────────────┐
│         MongoDB Collections          │
├─────────────────────────────────────┤
│                                     │
│  sensor_readings                    │
│  {                                  │
│    _id: ObjectId,                   │
│    device_id: string,               │
│    sensor_type: string,             │
│    timestamp: ISODate,              │
│    data: {                          │
│      motion: boolean,               │
│      distance: number,              │
│      temperature: number,           │
│      humidity: number,              │
│      acceleration: {x,y,z}          │
│    }                                │
│  }                                  │
│                                     │
│  fall_events                        │
│  {                                  │
│    _id: ObjectId,                   │
│    user_id: string,                 │
│    timestamp: ISODate,              │
│    severity_score: number,          │
│    verified: boolean,               │
│    sensor_data: {                   │
│      accelerometer: {...},          │
│      room_sensors: {...}            │
│    },                               │
│    alert_status: {                  │
│      push_sent: boolean,            │
│      email_sent: boolean,           │
│      acknowledged: boolean          │
│    }                                │
│  }                                  │
│                                     │
│  users                              │
│  {                                  │
│    _id: ObjectId,                   │
│    name: string,                    │
│    email: string,                   │
│    phone: string,                   │
│    emergency_contacts: [...],       │
│    preferences: {                   │
│      alert_threshold: number,       │
│      notification_enabled: boolean  │
│    }                                │
│  }                                  │
│                                     │
│  devices                            │
│  {                                  │
│    _id: ObjectId,                   │
│    device_id: string,               │
│    device_type: string,             │
│    location: string,                │
│    status: string,                  │
│    last_seen: ISODate               │
│  }                                  │
└─────────────────────────────────────┘
```

