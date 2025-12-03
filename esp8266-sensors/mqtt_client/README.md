# ESP8266 MQTT Client

This directory contains the MQTT communication code for ESP8266 sensor nodes.

## Installation

1. Install Arduino IDE
2. Add ESP8266 board support:
   - File → Preferences → Additional Board Manager URLs
   - Add: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
   - Tools → Board → Boards Manager → Search "ESP8266" → Install

3. Install required libraries:
   - Sketch → Include Library → Manage Libraries
   - Install:
     - PubSubClient (by Nick O'Leary)
     - DHT sensor library (by Adafruit)
     - ArduinoJson (by Benoit Blanchon)

4. Configure settings:
   - Copy `config.h.example` to `config.h`
   - Update WiFi credentials and MQTT server IP

5. Upload code to ESP8266

## MQTT Topics

### Published Topics
- `sensors/pir/{device_id}` - PIR motion state (0 or 1)
- `sensors/ultrasonic/{device_id}` - Distance in cm
- `sensors/dht22/{device_id}` - Temperature and humidity (JSON)
- `sensors/combined/{device_id}` - All sensor data (JSON)
- `devices/{device_id}/status` - Device online/offline status

### Subscribed Topics
- `devices/{device_id}/control` - Control commands (reset, read_now)

## Testing

1. Monitor serial output at 115200 baud
2. Check MQTT broker for published messages
3. Verify sensor readings are within expected ranges

