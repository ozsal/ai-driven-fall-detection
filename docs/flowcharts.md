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
│  ESP8266 Sensor Data Collection        │
│  - PIR Motion Sensor                    │
│  - Ultrasonic Distance Sensor          │
│  - DHT22 Temperature/Humidity           │
│  (Every 2 seconds)                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Raspberry Pi Receives MQTT Data        │
│  - Store in SQLite database            │
│  - Analyze sensor patterns              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Fall Detection Analysis                │
│  - Check PIR: No motion detected?       │
│  - Check Ultrasonic: Distance < 50cm?  │
│  - Check DHT22: Environmental changes? │
│  - Analyze duration of inactivity       │
└──────────────┬──────────────────────────┘
               │
               ▼
      ┌─────────────────────────────┐
      │ Calculate Severity Score    │
      │ - Room Verification (50%)   │
      │ - Duration (30%)             │
      │ - Environmental (20%)       │
      └──────────────┬──────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Score >= 6.0?         │
          └───┬──────────────┬───┘
              │              │
             NO            YES
              │              │
              │              ▼
              │  ┌─────────────────────────────┐
              │  │ Verify with Multiple        │
              │  │ Sensor Readings             │
              │  │ - At least 2 factors match │
              │  └──────────────┬──────────────┘
              │                 │
              │                 ▼
              │  ┌─────────────────────────────┐
              │  │ Fall Detected & Verified    │
              │  └──────────────┬──────────────┘
              │                 │
              │                 ▼
              │  ┌─────────────────────────────┐
              │  │ Trigger Alert System        │
              │  │ - Push notification         │
              │  │ - Email alert                │
              │  │ - Dashboard update           │
              │  │ - Log to database            │
              │  └─────────────────────────────┘
              │
              └─────────────────────┐
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
│ Store in SQLite Database    │
│ Table: sensor_readings      │
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
│ Run Fall Detection Analysis │
│ - PIR inactivity check      │
│ - Ultrasonic distance check │
│ - Duration analysis         │
│ - Environmental changes     │
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
│         SQLite Database              │
├─────────────────────────────────────┤
│                                     │
│  sensor_readings                    │
│  {                                  │
│    id: INTEGER PRIMARY KEY,          │
│    device_id: TEXT,                  │
│    location: TEXT,                   │
│    sensor_type: TEXT,               │
│    timestamp: INTEGER,              │
│    received_at: TEXT (ISO),          │
│    data: TEXT (JSON),               │
│    topic: TEXT                      │
│  }                                  │
│                                     │
│  fall_events                        │
│  {                                  │
│    id: INTEGER PRIMARY KEY,          │
│    event_id: TEXT UNIQUE,           │
│    user_id: TEXT,                   │
│    timestamp: TEXT (ISO),            │
│    severity_score: REAL,            │
│    verified: INTEGER (0/1),         │
│    location: TEXT,                   │
│    sensor_data: TEXT (JSON),        │
│    acknowledged: INTEGER (0/1),      │
│    acknowledged_at: TEXT (ISO)      │
│  }                                  │
│                                     │
│  devices                            │
│  {                                  │
│    id: INTEGER PRIMARY KEY,          │
│    device_id: TEXT UNIQUE,          │
│    device_type: TEXT,               │
│    location: TEXT,                  │
│    status: TEXT,                    │
│    last_seen: TEXT (ISO)            │
│  }                                  │
│                                     │
│  users                              │
│  {                                  │
│    id: INTEGER PRIMARY KEY,          │
│    user_id: TEXT UNIQUE,            │
│    name: TEXT,                      │
│    email: TEXT UNIQUE,              │
│    phone: TEXT,                     │
│    preferences: TEXT (JSON),        │
│    created_at: TEXT (ISO)           │
│  }                                  │
│                                     │
│  alert_logs                         │
│  {                                  │
│    id: INTEGER PRIMARY KEY,          │
│    event_id: TEXT,                  │
│    channels: TEXT (JSON),           │
│    sent_at: TEXT (ISO),             │
│    status: TEXT                     │
│  }                                  │
└─────────────────────────────────────┘
```
