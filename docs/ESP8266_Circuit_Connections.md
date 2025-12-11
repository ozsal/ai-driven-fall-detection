# ESP8266 NodeMCU Circuit Connections

Mermaid diagram showing the exact pin connections for the ESP8266 NodeMCU sensor node.

```mermaid
flowchart TB
    subgraph ESP8266["ESP8266 NodeMCU"]
        D5["D5 (GPIO14)"]
        D6["D6 (GPIO12)"]
        D7["D7 (GPIO13)"]
        D2["D2 (GPIO4)"]
        D1["D1 (GPIO5)"]
        V33["3.3V"]
        GND_ESP["GND"]
    end
    
    subgraph PIR["PIR Sensor"]
        PIR_OUT["OUT"]
        PIR_GND["GND"]
    end
    
    subgraph ULTRASONIC["Ultrasonic Sensor"]
        ULTRASONIC_TRIG["TRIG"]
        ULTRASONIC_ECHO["ECHO"]
        ULTRASONIC_GND["GND"]
    end
    
    subgraph DHT22["DHT22 Sensor"]
        DHT22_DATA["DATA"]
        DHT22_VCC["VCC"]
        DHT22_GND["GND"]
    end
    
    subgraph BUZZER["Buzzer"]
        BUZZER_POS["+"]
        BUZZER_NEG["-"]
    end
    
    %% Pin Connections (as specified)
    D5 -.->|"D5 (GPIO14) ─"| PIR_OUT
    D6 -.->|"D6 (GPIO12) ─"| ULTRASONIC_TRIG
    ULTRASONIC_ECHO -.->|"─ D7 (GPIO13)"| D7
    D2 -.->|"D2 (GPIO4) ─"| DHT22_DATA
    D1 -.->|"D1 (GPIO5) ─"| BUZZER_POS
    
    %% Power Connection
    V33 -.->|"3.3V ─"| DHT22_VCC
    
    %% Ground Connections (Common Ground)
    GND_ESP -.->|"GND ─"| PIR_GND
    GND_ESP -.->|"GND ─"| ULTRASONIC_GND
    GND_ESP -.->|"GND ─"| DHT22_GND
    GND_ESP -.->|"GND ─"| BUZZER_NEG
    
    style ESP8266 fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    style PIR fill:#fff4e1,stroke:#e65100,stroke-width:2px
    style ULTRASONIC fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style DHT22 fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    style BUZZER fill:#ffcdd2,stroke:#c62828,stroke-width:2px
```

## Connection List

Based on your specifications:

- **D5 (GPIO14)** ─ PIR OUT
- **D6 (GPIO12)** ─ Ultrasonic TRIG
- **D7 (GPIO13)** ─ Ultrasonic ECHO
- **D2 (GPIO4)** ─ DHT22 DATA
- **D1 (GPIO5)** ─ Buzzer +
- **3.3V** ─ DHT22 VCC
- **GND** ─ Common Ground (all components)

## Connection Table

| ESP8266 Pin | Component Pin | Description |
|-------------|---------------|-------------|
| D5 (GPIO14) | PIR OUT | Digital Input - Motion Detection |
| D6 (GPIO12) | Ultrasonic TRIG | Digital Output - Trigger Pulse |
| D7 (GPIO13) | Ultrasonic ECHO | Digital Input - Echo Pulse |
| D2 (GPIO4) | DHT22 DATA | Digital I/O - Data Communication |
| D1 (GPIO5) | Buzzer + | Digital Output - Buzzer Control |
| 3.3V | DHT22 VCC | Power Supply |
| GND | All GND Pins | Common Ground |







