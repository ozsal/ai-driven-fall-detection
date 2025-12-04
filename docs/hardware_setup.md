# Hardware Setup Guide

## Component List

### Required Components
- Raspberry Pi 4 (4GB RAM recommended)
- ESP8266 NodeMCU v1.0 (2x for multiple rooms)
- PIR Motion Sensor (HC-SR501 or similar) - 2x
- Ultrasonic Distance Sensor (HC-SR04) - 2x
- DHT22 Temperature/Humidity Sensor - 2x
- Resistors: 10kΩ (for DHT22), 1kΩ (for HC-SR04)
- Jumper wires
- Breadboards
- 5V power supply for sensors
- USB cables

## ESP8266 Sensor Node Connections

### NodeMCU Pin Mapping

```
ESP8266 NodeMCU Pinout:
- D0  (GPIO16) - Wake pin
- D1  (GPIO5)  - I2C SCL
- D2  (GPIO4)  - I2C SDA
- D3  (GPIO0)  - Flash button
- D4  (GPIO2)  - Built-in LED
- D5  (GPIO14) - SPI CLK
- D6  (GPIO12) - SPI MISO
- D7  (GPIO13) - SPI MOSI
- D8  (GPIO15) - SPI CS
- A0  (ADC)    - Analog input
```

### Connection Diagram for ESP8266 Node 1

```
┌─────────────────────────────────────────────────────────┐
│                    ESP8266 NodeMCU                      │
│                                                          │
│  PIR Sensor (HC-SR501)                                  │
│  ┌──────────────┐                                       │
│  │ VCC ─────────┼──> 5V                                 │
│  │ GND ─────────┼──> GND                                │
│  │ OUT ─────────┼──> D5 (GPIO14)                        │
│  └──────────────┘                                       │
│                                                          │
│  Ultrasonic Sensor (HC-SR04)                            │
│  ┌──────────────┐                                       │
│  │ VCC ─────────┼──> 5V                                 │
│  │ GND ─────────┼──> GND                                │
│  │ Trig ────────┼──> D6 (GPIO12)                        │
│  │ Echo ────────┼──> D7 (GPIO13)                        │
│  └──────────────┘                                       │
│                                                          │
│  DHT22 Temperature/Humidity                             │
│  ┌──────────────┐                                       │
│  │ VCC ─────────┼──> 3.3V                               │
│  │ GND ─────────┼──> GND                                │
│  │ DATA ────────┼──> D2 (GPIO4)                         │
│  │              │    └──> 10kΩ pull-up to 3.3V          │
│  └──────────────┘                                       │
│                                                          │
│  Built-in LED: D4 (GPIO2) - Status indicator            │
└─────────────────────────────────────────────────────────┘
```

### Detailed Pin Connections

#### PIR Motion Sensor (HC-SR501)
- **VCC** → 5V (NodeMCU)
- **GND** → GND (NodeMCU)
- **OUT** → GPIO14 (D5 on NodeMCU)
- **Note**: Adjust sensitivity and time delay potentiometers on PIR sensor

#### Ultrasonic Sensor (HC-SR04)
- **VCC** → 5V (NodeMCU)
- **GND** → GND (NodeMCU)
- **Trig** → GPIO12 (D6 on NodeMCU)
- **Echo** → GPIO13 (D7 on NodeMCU)
- **Note**: Echo pin outputs 5V, but ESP8266 GPIO is 3.3V tolerant. Use voltage divider if needed:
  - Echo → 1kΩ resistor → GPIO13
  - GPIO13 → 2kΩ resistor → GND

#### DHT22 Sensor
- **VCC** → 3.3V (NodeMCU)
- **GND** → GND (NodeMCU)
- **DATA** → GPIO4 (D2 on NodeMCU)
- **Pull-up Resistor**: 10kΩ between DATA and 3.3V

### ESP8266 Node 2 (Second Room)
Use the same pin configuration as Node 1. Each node will have a unique device ID.

## Raspberry Pi Setup

### Required Connections
- **Power**: USB-C power supply (5V, 3A)
- **Network**: Ethernet or WiFi
- **Storage**: MicroSD card (32GB+ recommended)
- **Display**: HDMI (optional, for initial setup)

### GPIO Pins (if needed for future expansion)
- GPIO pins available for additional sensors
- I2C bus available for sensor expansion

## Power Requirements

### ESP8266 Nodes
- **Input**: 5V via USB or external power
- **Current**: ~200-300mA during operation
- **Power Supply**: USB adapter (5V, 1A minimum)

### Raspberry Pi 4
- **Input**: 5V via USB-C
- **Current**: 2.5-3A typical
- **Power Supply**: Official Raspberry Pi power supply (5V, 3A)

## Network Configuration

### WiFi Setup for ESP8266
Each ESP8266 node needs:
- SSID and password for your WiFi network
- Static IP (optional, recommended) or DHCP
- MQTT broker IP address (Raspberry Pi IP)

### Raspberry Pi Network
- Static IP recommended for MQTT broker
- Port 1883 (MQTT) should be open
- Port 8000 (FastAPI) should be accessible

## Physical Placement

### ESP8266 Sensor Nodes
- **Height**: Mount 1.5-2 meters above floor
- **Orientation**: PIR sensor facing room center
- **Ultrasonic**: Pointed downward at 45° angle
- **Location**: One per room to monitor

## Testing Checklist

1. ✅ ESP8266 powers on (LED indicator)
2. ✅ WiFi connection established
3. ✅ MQTT connection to broker successful
4. ✅ PIR sensor detects motion
5. ✅ Ultrasonic sensor reads distance
6. ✅ DHT22 reads temperature/humidity
7. ✅ Data appears in MQTT broker
9. ✅ Raspberry Pi receives sensor data
10. ✅ Database stores readings

## Troubleshooting

### ESP8266 Issues
- **No WiFi connection**: Check SSID/password, signal strength
- **Sensor not reading**: Verify pin connections, power supply
- **MQTT connection failed**: Check broker IP, port 1883, credentials

### Raspberry Pi Issues
- **MQTT broker not starting**: Check Mosquitto installation, port availability
- **Database connection failed**: Verify SQLite database file permissions and path

