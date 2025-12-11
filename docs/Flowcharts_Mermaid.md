# Mermaid Flowcharts for AI-Driven Fall Detection System

This document contains all Mermaid flowchart code for the coursework report. You can use these in Markdown files, documentation tools, or online Mermaid editors.

---

## 1. System-Level Data Flow Diagram

This diagram shows the complete data flow from sensors to user interfaces.

```mermaid
flowchart TD
    subgraph ESP8266["ESP8266 SENSOR NODES"]
        PIR["PIR Sensor"]
        ULTRASONIC["Ultrasonic Sensor"]
        DHT22["DHT22 Sensor"]
        ESP8266_NODE["ESP8266 NodeMCU<br/>(Sensor Data Processing)"]
        
        PIR --> ESP8266_NODE
        ULTRASONIC --> ESP8266_NODE
        DHT22 --> ESP8266_NODE
    end
    
    ESP8266_NODE -->|WiFi + MQTT<br/>(Encrypted)| MQTT_BROKER["MQTT BROKER (Mosquitto)<br/>Raspberry Pi (Port 1883)<br/><br/>Topics:<br/>- sensors/pir/{device_id}<br/>- sensors/ultrasonic/{device_id}<br/>- sensors/dht22/{device_id}"]
    
    MQTT_BROKER -->|MQTT Subscribe| BACKEND["FASTAPI BACKEND<br/>(Raspberry Pi)"]
    
    subgraph BACKEND_COMPONENTS["Backend Components"]
        MQTT_HANDLER["MQTT Message Handler<br/>- Parse sensor data<br/>- Validate payload"]
        ALERT_ENGINE["Alert Engine<br/>- Rule-based evaluation<br/>- ML model inference<br/>- Fall detection algorithm"]
        DATABASE["Database Layer (SQLite)<br/>- sensor_readings table<br/>- alerts table<br/>- fall_events table"]
        WEBSOCKET["WebSocket Server<br/>- Real-time alert broadcasting<br/>- Live sensor data updates"]
        
        MQTT_HANDLER --> ALERT_ENGINE
        ALERT_ENGINE --> DATABASE
        DATABASE --> WEBSOCKET
    end
    
    BACKEND --> MQTT_HANDLER
    
    WEBSOCKET -->|HTTP/WebSocket<br/>(JWT Authenticated)| USER_INTERFACES["USER INTERFACES"]
    
    subgraph USER_INTERFACES_COMPONENTS["User Interface Components"]
        WEB_DASHBOARD["Web Dashboard (React)<br/>- Real-time visualization<br/>- Alert management"]
        MOBILE_APP["Mobile App (Flutter)<br/>- Notifications<br/>- Alerts<br/>- Monitoring"]
    end
    
    USER_INTERFACES --> WEB_DASHBOARD
    USER_INTERFACES --> MOBILE_APP
    
    style ESP8266 fill:#e1f5ff
    style MQTT_BROKER fill:#fff4e1
    style BACKEND fill:#e8f5e9
    style USER_INTERFACES fill:#f3e5f5
```

---

## 2. Alert Generation Flow Diagram

This diagram shows the process of generating alerts from sensor readings.

```mermaid
flowchart TD
    START([Sensor Reading]) --> STORE_DB["Store in Database"]
    
    STORE_DB --> ALERT_ENGINE["Alert Engine"]
    
    subgraph ALERT_ENGINE_COMPONENTS["Alert Engine Components"]
        ML_PREDICTOR["ML Predictor<br/>- Temp anomaly<br/>- Fire risk<br/>- Motion anomaly"]
        RULE_BASED["Rule-Based Checks<br/>- Thresholds<br/>- Trends<br/>- Patterns"]
        
        ML_PREDICTOR --> COMBINE
        RULE_BASED --> COMBINE
        COMBINE["Combine Alerts"]
    end
    
    ALERT_ENGINE --> ML_PREDICTOR
    ALERT_ENGINE --> RULE_BASED
    
    COMBINE --> GENERATE_ALERTS["Generate Alerts"]
    
    GENERATE_ALERTS --> STORE_ALERT["Store Alert in Database"]
    
    STORE_ALERT --> BROADCAST["Broadcast via WebSocket"]
    
    ACTIVATE_BUZZER --> END([End])
    
    style START fill:#c8e6c9
    style ALERT_ENGINE fill:#fff9c4
    style ML_PREDICTOR fill:#e1bee7
    style RULE_BASED fill:#ffccbc
    style GENERATE_ALERTS fill:#ffcdd2
    style END fill:#c8e6c9
```

---

## 3. Central Unit (Raspberry Pi) Flowchart

This diagram shows the main processing loop of the central unit.

```mermaid
flowchart TD
    START([START]) --> INIT["Initialize<br/>- Database<br/>- MQTT Client<br/>- FastAPI<br/>- ML Models"]
    
    INIT --> CONNECT_MQTT["Connect to<br/>MQTT Broker"]
    
    CONNECT_MQTT --> SUBSCRIBE["Subscribe to<br/>Sensor Topics"]
    
    SUBSCRIBE --> PARALLEL{Message Type}
    
    PARALLEL -->|MQTT Message| MQTT_RECEIVED["MQTT Message<br/>Received"]
    PARALLEL -->|HTTP Request| HTTP_RECEIVED["HTTP Request<br/>Received"]
    
    MQTT_RECEIVED --> PARSE_MQTT["Parse & Validate<br/>Sensor Data"]
    HTTP_RECEIVED --> AUTH["Authenticate<br/>JWT Token"]
    
    PARSE_MQTT --> STORE_DB["Store in<br/>Database"]
    AUTH --> STORE_DB
    
    STORE_DB --> EVALUATE["Evaluate Alerts<br/>- ML Models<br/>- Rule-Based"]
    
    EVALUATE --> FALL_CHECK{Fall Detected?}
    
    FALL_CHECK -->|YES| GENERATE_ALERT["Generate Alert"]
    FALL_CHECK -->|NO| CONTINUE["Continue Monitoring"]
    
    GENERATE_ALERT --> BROADCAST_ALERT["Broadcast Alert<br/>- WebSocket<br/>- Database<br/>- Actuator Cmd"]
    CONTINUE --> BROADCAST_ALERT
    
    BROADCAST_ALERT --> SEND_MQTT["Send MQTT Cmd<br/>to Actuator"]
    
    SEND_MQTT --> LOOP([LOOP])
    LOOP --> PARALLEL
    
    style START fill:#c8e6c9
    style INIT fill:#e1f5ff
    style CONNECT_MQTT fill:#fff4e1
    style PARALLEL fill:#fff9c4
    style FALL_CHECK fill:#ffcdd2
    style GENERATE_ALERT fill:#f8bbd0
    style LOOP fill:#c8e6c9
```

---

## 4. Sensor Data Processing Flow

This diagram shows how sensor data is processed from reading to storage.

```mermaid
flowchart LR
    subgraph SENSORS["Sensors"]
        PIR_SENSOR["PIR Sensor<br/>Motion Detection"]
        ULTRASONIC_SENSOR["Ultrasonic Sensor<br/>Distance Measurement"]
        DHT22_SENSOR["DHT22 Sensor<br/>Temperature & Humidity"]
    end
    
    subgraph ESP8266_PROCESSING["ESP8266 Processing"]
        READ["Read Sensors<br/>Every 2 seconds"]
        VALIDATE["Validate Data<br/>Range Checks"]
        FORMAT["Format JSON<br/>Payload"]
    end
    
    subgraph MQTT_TRANSMISSION["MQTT Transmission"]
        PUBLISH["Publish to MQTT<br/>QoS Level 1"]
        TOPICS["Topics:<br/>sensors/pir/{id}<br/>sensors/ultrasonic/{id}<br/>sensors/dht22/{id}"]
    end
    
    subgraph BACKEND_PROCESSING["Backend Processing"]
        RECEIVE["Receive MQTT<br/>Message"]
        PARSE["Parse & Extract<br/>Device ID & Data"]
        STORE["Store in<br/>SQLite Database"]
    end
    
    PIR_SENSOR --> READ
    ULTRASONIC_SENSOR --> READ
    DHT22_SENSOR --> READ
    
    READ --> VALIDATE
    VALIDATE --> FORMAT
    FORMAT --> PUBLISH
    PUBLISH --> TOPICS
    TOPICS --> RECEIVE
    RECEIVE --> PARSE
    PARSE --> STORE
    
    style SENSORS fill:#e1f5ff
    style ESP8266_PROCESSING fill:#fff4e1
    style MQTT_TRANSMISSION fill:#e8f5e9
    style BACKEND_PROCESSING fill:#f3e5f5
```

---

## 5. Fall Detection Algorithm Flow

This diagram shows the multi-sensor fall detection algorithm.

```mermaid
flowchart TD
    START([Sensor Data Received]) --> COLLECT["Collect Multi-Sensor Data<br/>- PIR: Motion state<br/>- Ultrasonic: Distance<br/>- DHT22: Environment"]
    
    COLLECT --> CALCULATE_SCORES["Calculate Scores"]
    
    subgraph SCORES["Score Calculation"]
        ROOM_SCORE["Room Verification Score<br/>(Weight: 0.5)<br/>- PIR inactive<br/>- Ultrasonic < 50cm"]
        DURATION_SCORE["Duration Score<br/>(Weight: 0.3)<br/>- Inactivity time > 10s"]
        ENV_SCORE["Environmental Score<br/>(Weight: 0.2)<br/>- Temperature changes<br/>- Humidity changes"]
    end
    
    CALCULATE_SCORES --> ROOM_SCORE
    CALCULATE_SCORES --> DURATION_SCORE
    CALCULATE_SCORES --> ENV_SCORE
    
    ROOM_SCORE --> COMBINE_SCORES["Combine Scores<br/>Severity = Room×0.5 + Duration×0.3 + Env×0.2"]
    DURATION_SCORE --> COMBINE_SCORES
    ENV_SCORE --> COMBINE_SCORES
    
    COMBINE_SCORES --> THRESHOLD_CHECK{Severity >= 6.0?}
    
    THRESHOLD_CHECK -->|YES| FALL_DETECTED["Fall Detected"]
    THRESHOLD_CHECK -->|NO| NO_FALL["No Fall<br/>Continue Monitoring"]
    
    ACTIVATE --> STORE_EVENT["Store Fall Event<br/>in Database"]
    
    STORE_EVENT --> ALERT["Generate Alert<br/>& Broadcast"]
    
    ALERT --> END([End])
    NO_FALL --> END
    
    style START fill:#c8e6c9
    style SCORES fill:#fff9c4
    style THRESHOLD_CHECK fill:#ffcdd2
    style FALL_DETECTED fill:#f8bbd0
    style ACTIVATE fill:#ffccbc
    style END fill:#c8e6c9
```

---

## 6. Authentication & Authorization Flow

This diagram shows the authentication and authorization process for API access.

```mermaid
flowchart TD
    CLIENT([Client Request]) --> HAS_TOKEN{Has JWT Token?}
    
    HAS_TOKEN -->|NO| LOGIN["POST /auth/login<br/>Username + Password"]
    HAS_TOKEN -->|YES| VERIFY_TOKEN["Verify Token<br/>- Check signature<br/>- Check expiration"]
    
    LOGIN --> VALIDATE_CRED["Validate Credentials<br/>- Check username<br/>- Verify password hash"]
    
    VALIDATE_CRED -->|Invalid| REJECT1["401 Unauthorized"]
    VALIDATE_CRED -->|Valid| GENERATE_TOKEN["Generate JWT Token<br/>- User ID<br/>- Role<br/>- Expiration"]
    
    GENERATE_TOKEN --> RETURN_TOKEN["Return Token<br/>to Client"]
    
    VERIFY_TOKEN -->|Invalid/Expired| REJECT2["401 Unauthorized"]
    VERIFY_TOKEN -->|Valid| EXTRACT_ROLE["Extract User Role<br/>from Token"]
    
    EXTRACT_ROLE --> CHECK_PERMISSION{Required Permission}
    
    CHECK_PERMISSION -->|Admin| ADMIN_ACCESS["Admin Access<br/>- Full CRUD<br/>- User Management"]
    CHECK_PERMISSION -->|Sensor Manager| MANAGER_ACCESS["Sensor Manager Access<br/>- View & Edit Sensors<br/>- Manage Devices"]
    CHECK_PERMISSION -->|Viewer| VIEWER_ACCESS["Viewer Access<br/>- Read Only<br/>- View Data"]
    CHECK_PERMISSION -->|Insufficient| REJECT3["403 Forbidden"]
    
    ADMIN_ACCESS --> ALLOW["Allow Request"]
    MANAGER_ACCESS --> ALLOW
    VIEWER_ACCESS --> ALLOW
    
    ALLOW --> PROCESS["Process API Request"]
    
    REJECT1 --> END([End])
    REJECT2 --> END
    REJECT3 --> END
    PROCESS --> END
    
    style CLIENT fill:#e1f5ff
    style LOGIN fill:#fff4e1
    style GENERATE_TOKEN fill:#e8f5e9
    style CHECK_PERMISSION fill:#fff9c4
    style REJECT1 fill:#ffcdd2
    style REJECT2 fill:#ffcdd2
    style REJECT3 fill:#ffcdd2
    style ALLOW fill:#c8e6c9
    style END fill:#c8e6c9
```

---

## 7. ML Model Inference Flow

This diagram shows how ML models are used for alert prediction.

```mermaid
flowchart TD
    SENSOR_DATA([Sensor Data]) --> EXTRACT_FEATURES["Extract Features<br/>- Current values<br/>- Recent averages<br/>- Standard deviations<br/>- Trends"]
    
    EXTRACT_FEATURES --> SCALE_FEATURES["Scale Features<br/>Using StandardScaler"]
    
    SCALE_FEATURES --> ML_MODELS["ML Models"]
    
    subgraph ML_MODELS["ML Model Predictions"]
        TEMP_MODEL["Temperature Anomaly Model<br/>RandomForestClassifier"]
        FIRE_MODEL["Fire Risk Model<br/>RandomForestClassifier"]
        MOTION_MODEL["Motion Anomaly Model<br/>RandomForestClassifier"]
    end
    
    SCALE_FEATURES --> TEMP_MODEL
    SCALE_FEATURES --> FIRE_MODEL
    SCALE_FEATURES --> MOTION_MODEL
    
    TEMP_MODEL --> TEMP_RESULT["Prediction Result<br/>- Probability<br/>- Confidence"]
    FIRE_MODEL --> FIRE_RESULT["Prediction Result<br/>- Probability<br/>- Confidence"]
    MOTION_MODEL --> MOTION_RESULT["Prediction Result<br/>- Probability<br/>- Confidence"]
    
    TEMP_RESULT --> THRESHOLD_CHECK{Probability > 0.5?}
    FIRE_RESULT --> THRESHOLD_CHECK
    MOTION_RESULT --> THRESHOLD_CHECK
    
    THRESHOLD_CHECK -->|YES| DETERMINE_SEVERITY["Determine Severity<br/>Based on Confidence"]
    THRESHOLD_CHECK -->|NO| NO_ALERT["No Alert<br/>Normal Operation"]
    
    DETERMINE_SEVERITY --> CREATE_ALERT["Create ML Alert<br/>- Alert Type<br/>- Severity<br/>- Message<br/>- Confidence Score"]
    
    CREATE_ALERT --> COMBINE_RULE["Combine with<br/>Rule-Based Alerts"]
    
    COMBINE_RULE --> FINAL_ALERTS([Final Alerts])
    
    NO_ALERT --> FINAL_ALERTS
    
    style SENSOR_DATA fill:#e1f5ff
    style ML_MODELS fill:#fff9c4
    style THRESHOLD_CHECK fill:#ffcdd2
    style CREATE_ALERT fill:#f8bbd0
    style FINAL_ALERTS fill:#c8e6c9
```

---

## 8. ESP8266 NodeMCU Pin Connection Diagram

This diagram shows the exact pin connections for the ESP8266 NodeMCU sensor node.

```mermaid
flowchart TB
    subgraph ESP8266["ESP8266 NodeMCU"]
        D5["D5 / GPIO14<br/>Digital Input"]
        D6["D6 / GPIO12<br/>Digital Output"]
        D7["D7 / GPIO13<br/>Digital Input"]
        D2["D2 / GPIO4<br/>Digital I/O"]
        D1["D1 / GPIO5<br/>Digital Output"]
        V33["3.3V<br/>Power Output"]
        GND_ESP["GND<br/>Ground"]
    end
    
    subgraph PIR["PIR Sensor (HC-SR501)"]
        PIR_OUT["OUT"]
        PIR_GND["GND"]
    end
    
    subgraph ULTRASONIC["Ultrasonic Sensor (HC-SR04)"]
        ULTRASONIC_TRIG["TRIG"]
        ULTRASONIC_ECHO["ECHO"]
        ULTRASONIC_GND["GND"]
    end
    
    subgraph DHT22["DHT22 Sensor"]
        DHT22_DATA["DATA"]
        DHT22_VCC["VCC"]
        DHT22_GND["GND"]
    end
    

    
    %% Pin Connections
    PIR_OUT -->|"Signal"| D5
    D6 -->|"Trigger"| ULTRASONIC_TRIG
    ULTRASONIC_ECHO -->|"Echo"| D7
    DHT22_DATA -->|"Data"| D2
    D1 -->|"Control"| BUZZER_POS
    
    %% Power Connection
    V33 -.->|"3.3V ─"| DHT22_VCC
    
    %% Ground Connections (Common Ground)
    GND_ESP -.->|"GND ─"| PIR_GND
    GND_ESP -.->|"GND ─"| ULTRASONIC_GND
    GND_ESP -.->|"GND ─"| DHT22_GND
    GND_ESP -.->|"GND ─"| BUZZER_NEG
    
    style ESP8266 fill:#e1f5ff
    style PIR fill:#fff4e1
    style ULTRASONIC fill:#e8f5e9
    style DHT22 fill:#f3e5f5
    style BUZZER fill:#ffcdd2
```

### Pin Connection List

Based on your specifications:

- **D5 (GPIO14)** ─ PIR OUT
- **D6 (GPIO12)** ─ Ultrasonic TRIG
- **D7 (GPIO13)** ─ Ultrasonic ECHO
- **D2 (GPIO4)** ─ DHT22 DATA
- **D1 (GPIO5)** ─ Buzzer +
- **3.3V** ─ DHT22 VCC
- **GND** ─ Common Ground (all components)

### Connection Details Table

| ESP8266 Pin | Component Pin | Description |
|-------------|---------------|-------------|
| D5 (GPIO14) | PIR OUT | Digital Input - Motion Detection |
| D6 (GPIO12) | Ultrasonic TRIG | Digital Output - Trigger Pulse |
| D7 (GPIO13) | Ultrasonic ECHO | Digital Input - Echo Pulse |
| D2 (GPIO4) | DHT22 DATA | Digital I/O - Data Communication |
| D1 (GPIO5) | Buzzer + | Digital Output - Buzzer Control |
| 3.3V | DHT22 VCC | Power Supply |
| GND | All GND Pins | Common Ground |

**Note:** 
- PIR sensor typically operates at 3.3V-5V (check your specific model)
- Ultrasonic sensor (HC-SR04) requires 5V for VCC, but ECHO pin is 3.3V tolerant
- DHT22 requires a pull-up resistor (4.7kΩ-10kΩ) between DATA and VCC (may be included in module)
- All ground connections must be connected to a common ground point

---

## 9. Circuit-Level Connection Diagram

This diagram shows all physical circuit connections between the ESP8266 NodeMCU and sensors/actuators.

```mermaid
flowchart TB
    subgraph ESP8266_BOARD["ESP8266 NodeMCU Development Board"]
        VIN["VIN<br/>(5V Power Input)"]
        GND_ESP["GND<br/>(Ground)"]
        V33["3.3V<br/>(3.3V Output)"]
        D1_GPIO5["D1 / GPIO5<br/>(Digital Output)"]
        D2_GPIO4["D2 / GPIO4<br/>(Digital Input)"]
        D4_GPIO2["D4 / GPIO2<br/>(Built-in LED)"]
        D5_GPIO14["D5 / GPIO14<br/>(Digital Input)"]
        D6_GPIO12["D6 / GPIO12<br/>(Digital Output)"]
        D7_GPIO13["D7 / GPIO13<br/>(Digital Input)"]
    end
    
    subgraph PIR_SENSOR["PIR Motion Sensor (HC-SR501)"]
        PIR_OUT["OUT<br/>(Digital Output)"]
        PIR_VCC["VCC<br/>(Power)"]
        PIR_GND["GND<br/>(Ground)"]
    end
    
    subgraph ULTRASONIC["Ultrasonic Sensor (HC-SR04)"]
        ULTRASONIC_TRIG["TRIG<br/>(Trigger Pin)"]
        ULTRASONIC_ECHO["ECHO<br/>(Echo Pin)"]
        ULTRASONIC_VCC["VCC<br/>(Power)"]
        ULTRASONIC_GND["GND<br/>(Ground)"]
    end
    
    subgraph DHT22_SENSOR["DHT22 Temperature & Humidity Sensor"]
        DHT22_DATA["DATA<br/>(Data Pin)"]
        DHT22_VCC["VCC<br/>(Power)"]
        DHT22_GND["GND<br/>(Ground)"]
    end
    
    subgraph BUZZER["Active Buzzer"]
        BUZZER_POS["+<br/>(Positive)"]
        BUZZER_NEG["-<br/>(Negative)"]
    end
    
    subgraph POWER["Power Supply"]
        USB_5V["USB 5V<br/>(Power Source)"]
        COMMON_GND["Common Ground<br/>(All GND connected)"]
    end
    
    %% Power Connections
    USB_5V -->|5V Power| VIN
    USB_5V -->|5V Power| ULTRASONIC_VCC
    V33 -->|3.3V Power| PIR_VCC
    V33 -->|3.3V Power| DHT22_VCC
    
    %% Ground Connections (All connected to common ground)
    GND_ESP --> COMMON_GND
    PIR_GND --> COMMON_GND
    ULTRASONIC_GND --> COMMON_GND
    DHT22_GND --> COMMON_GND
    BUZZER_NEG --> COMMON_GND
    
    %% Signal Connections
    PIR_OUT -->|Digital Signal| D5_GPIO14
    D6_GPIO12 -->|Trigger Signal| ULTRASONIC_TRIG
    ULTRASONIC_ECHO -->|Echo Signal| D7_GPIO13
    DHT22_DATA -->|Data Signal| D2_GPIO4
    D1_GPIO5 -->|Control Signal| BUZZER_POS
    
    %% Connection Labels
    PIR_OUT -.->|"Connection: OUT → D5 (GPIO14)"| D5_GPIO14
    D6_GPIO12 -.->|"Connection: D6 (GPIO12) → TRIG"| ULTRASONIC_TRIG
    ULTRASONIC_ECHO -.->|"Connection: ECHO → D7 (GPIO13)"| D7_GPIO13
    DHT22_DATA -.->|"Connection: DATA → D2 (GPIO4)"| D2_GPIO4
    D1_GPIO5 -.->|"Connection: D1 (GPIO5) → Buzzer +"| BUZZER_POS
    
    style ESP8266_BOARD fill:#e1f5ff
    style PIR_SENSOR fill:#fff4e1
    style ULTRASONIC fill:#e8f5e9
    style DHT22_SENSOR fill:#f3e5f5
    style BUZZER fill:#ffcdd2
    style POWER fill:#fff9c4
```

### Detailed Pin Connection Table

| Component | Pin/Port | ESP8266 Pin | Connection Type | Voltage Level |
|-----------|----------|-------------|-----------------|---------------|
| **PIR Sensor** | OUT | D5 (GPIO14) | Digital Input | 3.3V Logic |
| **PIR Sensor** | VCC | 3.3V | Power Supply | 3.3V |
| **PIR Sensor** | GND | GND | Ground | 0V |
| **Ultrasonic** | TRIG | D6 (GPIO12) | Digital Output | 3.3V Logic |
| **Ultrasonic** | ECHO | D7 (GPIO13) | Digital Input | 3.3V Tolerant |
| **Ultrasonic** | VCC | 5V (VIN) | Power Supply | 5V |
| **Ultrasonic** | GND | GND | Ground | 0V |
| **DHT22** | DATA | D2 (GPIO4) | Digital I/O | 3.3V Logic |
| **DHT22** | VCC | 3.3V | Power Supply | 3.3V |
| **DHT22** | GND | GND | Ground | 0V |
| **Buzzer** | + (Positive) | D1 (GPIO5) | Digital Output | 3.3V Logic |
| **Buzzer** | - (Negative) | GND | Ground | 0V |
| **ESP8266** | VIN | USB 5V | Power Input | 5V |
| **ESP8266** | GND | Common | Ground | 0V |

### Circuit Connection Summary

**Power Connections:**
- ESP8266 VIN → USB 5V power supply
- Ultrasonic VCC → 5V (from VIN or separate 5V source)
- PIR VCC → ESP8266 3.3V output
- DHT22 VCC → ESP8266 3.3V output
- All GND pins connected to common ground

**Signal Connections:**
- PIR OUT → ESP8266 D5 (GPIO14) - Reads motion detection
- ESP8266 D6 (GPIO12) → Ultrasonic TRIG - Triggers distance measurement
- Ultrasonic ECHO → ESP8266 D7 (GPIO13) - Receives distance data
- DHT22 DATA → ESP8266 D2 (GPIO4) - Bidirectional data communication
- ESP8266 D1 (GPIO5) → Buzzer + - Controls buzzer activation

**Note:** The DHT22 requires a pull-up resistor (typically 4.7kΩ - 10kΩ) between DATA and VCC. Some DHT22 modules include this resistor internally.

---

## 10. Complete Circuit Wiring Diagram (Alternative View)

This diagram shows the circuit connections in a more traditional wiring diagram format.

```mermaid
flowchart LR
    subgraph LEFT["Left Side - Sensors"]
        PIR["PIR Sensor<br/>HC-SR501<br/>┌─────────┐<br/>│ OUT  VCC │<br/>│ GND      │<br/>└─────────┘"]
        ULTRASONIC["Ultrasonic<br/>HC-SR04<br/>┌─────────┐<br/>│ TRIG ECHO│<br/>│ VCC  GND │<br/>└─────────┘"]
        DHT22["DHT22<br/>Sensor<br/>┌─────────┐<br/>│ DATA VCC │<br/>│ GND      │<br/>└─────────┘"]
    end
    
    subgraph CENTER["Center - ESP8266 NodeMCU"]
        ESP8266["ESP8266 NodeMCU<br/>┌──────────────────┐<br/>│ VIN  GND         │<br/>│ 3.3V             │<br/>│ D1   D2   D4     │<br/>│ D5   D6   D7     │<br/>└──────────────────┘"]
    end
    
    subgraph POWER_SUPPLY["Power Supply"]
        USB["USB 5V<br/>Power Source"]
    end
    
    %% PIR Connections
    PIR -.->|"OUT → D5"| ESP8266
    PIR -.->|"VCC → 3.3V"| ESP8266
    PIR -.->|"GND → GND"| ESP8266
    
    %% Ultrasonic Connections
    ESP8266 -.->|"D6 → TRIG"| ULTRASONIC
    ULTRASONIC -.->|"ECHO → D7"| ESP8266
    ULTRASONIC -.->|"VCC → 5V"| ESP8266
    ULTRASONIC -.->|"GND → GND"| ESP8266
    
    %% DHT22 Connections
    DHT22 -.->|"DATA → D2"| ESP8266
    DHT22 -.->|"VCC → 3.3V"| ESP8266
    DHT22 -.->|"GND → GND"| ESP8266
    
    %% Power Connections
    USB -->|"5V"| ESP8266
    USB -->|"5V"| ULTRASONIC
    
    style LEFT fill:#e1f5ff
    style CENTER fill:#fff4e1
    style RIGHT fill:#ffcdd2
    style POWER_SUPPLY fill:#fff9c4
```

---

## 11. Signal Flow Diagram

This diagram shows the signal flow direction for each connection.

```mermaid
flowchart TD
    subgraph INPUT_SIGNALS["Input Signals (Sensors → ESP8266)"]
        PIR_SIGNAL["PIR OUT<br/>→ D5 (GPIO14)<br/>HIGH/LOW"]
        ECHO_SIGNAL["Ultrasonic ECHO<br/>→ D7 (GPIO13)<br/>Pulse Width"]
        DHT22_SIGNAL["DHT22 DATA<br/>→ D2 (GPIO4)<br/>Serial Data"]
    end
    
    subgraph ESP8266_PROCESSING["ESP8266 Processing"]
        READ_PIR["Read PIR State<br/>digitalRead(D5)"]
        READ_ULTRASONIC["Read Distance<br/>pulseIn(D7)"]
        READ_DHT22["Read Temp/Humidity<br/>dht.read()"]
        PROCESS["Process Data<br/>& Format JSON"]
    end
    
    subgraph OUTPUT_SIGNALS["Output Signals (ESP8266 → Actuators)"]
        TRIG_SIGNAL["D6 (GPIO12)<br/>→ Ultrasonic TRIG<br/>Trigger Pulse"]
    end
    
    subgraph MQTT_OUTPUT["Wireless Output"]
        MQTT_PUBLISH["Publish to MQTT<br/>WiFi Transmission"]
    end
    
    PIR_SIGNAL --> READ_PIR
    ECHO_SIGNAL --> READ_ULTRASONIC
    DHT22_SIGNAL --> READ_DHT22
    
    READ_PIR --> PROCESS
    READ_ULTRASONIC --> PROCESS
    READ_DHT22 --> PROCESS
    
    PROCESS --> TRIG_SIGNAL
    PROCESS --> MQTT_PUBLISH
    
    style INPUT_SIGNALS fill:#c8e6c9
    style ESP8266_PROCESSING fill:#fff9c4
    style OUTPUT_SIGNALS fill:#ffcdd2
    style MQTT_OUTPUT fill:#e1f5ff
```

---

## Usage Instructions

### In Markdown Files
Simply paste the Mermaid code blocks into your Markdown file. Most Markdown renderers (GitHub, GitLab, VS Code with extensions) support Mermaid.

### Online Editors
1. Go to [Mermaid Live Editor](https://mermaid.live/)
2. Paste the Mermaid code
3. Export as PNG, SVG, or copy the code

### In Documentation Tools
- **Notion**: Supports Mermaid natively
- **Confluence**: Use Mermaid plugin
- **Jupyter Notebooks**: Use `%%mermaid` magic command
- **VS Code**: Install "Markdown Preview Mermaid Support" extension

### Customization
You can customize the diagrams by:
- Changing colors: Modify `fill:#color` in style definitions
- Adjusting layout: Change `flowchart TD` (top-down) to `flowchart LR` (left-right)
- Adding/removing nodes: Follow the Mermaid syntax
- Changing shapes: Use different node types (`[]`, `()`, `{}`, `[()]`)

---

## Mermaid Syntax Reference

- `flowchart TD` - Top-down flowchart
- `flowchart LR` - Left-right flowchart
- `A --> B` - Arrow from A to B
- `A -->|Label| B` - Arrow with label
- `A{Decision}` - Decision node (diamond)
- `A([Start/End])` - Rounded rectangle (start/end)
- `subgraph X["Title"]` - Grouping
- `style A fill:#color` - Styling nodes

For more details, visit: https://mermaid.js.org/

