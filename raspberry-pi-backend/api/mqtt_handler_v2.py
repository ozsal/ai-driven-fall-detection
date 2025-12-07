"""
Extended MQTT Message Handler for v2 Schema
This module extends the existing handle_mqtt_message to support the new JSON format
while maintaining backward compatibility with existing MQTT topics.
"""

import json
from datetime import datetime
from typing import Dict, Any
from database.database_v2 import (
    get_or_create_device, get_or_create_sensor,
    insert_pir_reading, insert_ultrasonic_reading,
    insert_dht22_reading, insert_wifi_reading
)
from database.sqlite_db import insert_sensor_reading  # Keep for backward compatibility

async def handle_mqtt_message_v2(topic: str, payload: dict, broadcast_to_websockets=None):
    """
    Extended MQTT message handler that supports new JSON format:
    {
      "device_id": "ESP8266_NODE_01",
      "location": "Living_Room",
      "timestamp": 123456789,
      "sensors": {
        "pir": { "motion_detected": true },
        "ultrasonic": { "distance_cm": 123.4 },
        "dht22": { "temperature_c": 25.6, "humidity_percent": 60.2 }
      },
      "wifi": { "rssi": -55 }
    }
    
    Also maintains backward compatibility with existing topic-based format.
    """
    try:
        # Ensure payload is a dictionary
        if not isinstance(payload, dict):
            if isinstance(payload, (int, float)):
                payload = {"value": payload, "raw": payload}
            elif isinstance(payload, str):
                payload = {"value": payload, "raw": payload}
            else:
                try:
                    payload = dict(payload)
                except:
                    payload = {"value": str(payload), "raw": payload}
        
        # Check if this is the new v2 JSON format (has "sensors" key)
        if "sensors" in payload and isinstance(payload["sensors"], dict):
            # ============================================
            # NEW V2 FORMAT: Process structured JSON
            # ============================================
            await process_v2_json_format(topic, payload, broadcast_to_websockets)
        else:
            # ============================================
            # LEGACY FORMAT: Use existing handler
            # ============================================
            # Import and call the original handler (avoid circular import)
            import sys
            import importlib
            if 'api.main' in sys.modules:
                main_module = sys.modules['api.main']
                if hasattr(main_module, 'handle_mqtt_message'):
                    await main_module.handle_mqtt_message(topic, payload)
                else:
                    # Fallback: create a simple handler
                    print(f"⚠️ Legacy handler not available, processing as basic message")
                    from database.sqlite_db import insert_sensor_reading
                    # Extract basic info and store
                    device_id = payload.get("device_id", "unknown")
                    sensor_type = payload.get("sensor_type", "unknown")
                    await insert_sensor_reading({
                        "device_id": device_id,
                        "sensor_type": sensor_type,
                        "timestamp": payload.get("timestamp", int(datetime.utcnow().timestamp())),
                        "data": payload,
                        "location": payload.get("location"),
                        "topic": topic
                    })
            else:
                # If main module not loaded, use basic storage
                from database.sqlite_db import insert_sensor_reading
                await insert_sensor_reading({
                    "device_id": payload.get("device_id", "unknown"),
                    "sensor_type": payload.get("sensor_type", "unknown"),
                    "timestamp": payload.get("timestamp", int(datetime.utcnow().timestamp())),
                    "data": payload,
                    "location": payload.get("location"),
                    "topic": topic
                })
            
    except Exception as e:
        print(f"❌ Error in handle_mqtt_message_v2: {e}")
        import traceback
        traceback.print_exc()
        raise

async def process_v2_json_format(topic: str, payload: dict, broadcast_to_websockets=None):
    """
    Process the new v2 JSON format with structured sensors data
    """
    # Extract device information
    device_id = payload.get("device_id") or payload.get("deviceId") or "unknown"
    location = payload.get("location")
    timestamp = payload.get("timestamp")
    
    if not timestamp:
        timestamp = int(datetime.utcnow().timestamp())
    elif isinstance(timestamp, float):
        timestamp = int(timestamp)
    elif isinstance(timestamp, str):
        try:
            timestamp = int(float(timestamp))
        except:
            timestamp = int(datetime.utcnow().timestamp())
    
    # Extract device name (optional, defaults to device_id)
    device_name = payload.get("device_name") or device_id
    
    print(f"📥 Processing v2 JSON format: device_id={device_id}, location={location}")
    
    # 1. Get or create device
    device = await get_or_create_device(device_id, device_name, location)
    device_db_id = device.get("id") or device.get("device_id")
    
    # 2. Process sensors data
    sensors_data = payload.get("sensors", {})
    readings_inserted = []
    
    # Process PIR sensor
    if "pir" in sensors_data:
        pir_data = sensors_data["pir"]
        motion_detected = pir_data.get("motion_detected", False)
        
        # Get or create PIR sensor
        sensor = await get_or_create_sensor(
            device_id, "pir", "PIR Motion Sensor", device
        )
        
        if sensor and sensor.get("id"):
            # Insert into pir_readings table
            reading_id = await insert_pir_reading(sensor["id"], motion_detected, timestamp)
            readings_inserted.append({
                "sensor_type": "pir",
                "reading_id": reading_id,
                "data": {"motion_detected": motion_detected}
            })
            print(f"   ✅ Inserted PIR reading: motion_detected={motion_detected}")
        
        # Also store in legacy sensor_readings table for backward compatibility
        await insert_sensor_reading({
            "device_id": device_id,
            "sensor_type": "pir",
            "timestamp": timestamp,
            "data": {"motion_detected": motion_detected},
            "location": location,
            "topic": topic
        })
    
    # Process Ultrasonic sensor
    if "ultrasonic" in sensors_data:
        ultrasonic_data = sensors_data["ultrasonic"]
        distance_cm = ultrasonic_data.get("distance_cm", 0.0)
        
        # Get or create Ultrasonic sensor
        sensor = await get_or_create_sensor(
            device_id, "ultrasonic", "Ultrasonic Distance Sensor", device
        )
        
        if sensor and sensor.get("id"):
            # Insert into ultrasonic_readings table
            reading_id = await insert_ultrasonic_reading(sensor["id"], distance_cm, timestamp)
            readings_inserted.append({
                "sensor_type": "ultrasonic",
                "reading_id": reading_id,
                "data": {"distance_cm": distance_cm}
            })
            print(f"   ✅ Inserted Ultrasonic reading: distance_cm={distance_cm}")
        
        # Also store in legacy sensor_readings table
        await insert_sensor_reading({
            "device_id": device_id,
            "sensor_type": "ultrasonic",
            "timestamp": timestamp,
            "data": {"distance_cm": distance_cm},
            "location": location,
            "topic": topic
        })
    
    # Process DHT22 sensor
    if "dht22" in sensors_data:
        dht22_data = sensors_data["dht22"]
        temperature_c = dht22_data.get("temperature_c", 0.0)
        humidity_percent = dht22_data.get("humidity_percent", 0.0)
        
        # Get or create DHT22 sensor
        sensor = await get_or_create_sensor(
            device_id, "dht22", "DHT22 Temperature & Humidity Sensor", device
        )
        
        if sensor and sensor.get("id"):
            # Insert into dht22_readings table
            reading_id = await insert_dht22_reading(
                sensor["id"], temperature_c, humidity_percent, timestamp
            )
            readings_inserted.append({
                "sensor_type": "dht22",
                "reading_id": reading_id,
                "data": {
                    "temperature_c": temperature_c,
                    "humidity_percent": humidity_percent
                }
            })
            print(f"   ✅ Inserted DHT22 reading: temp={temperature_c}°C, humidity={humidity_percent}%")
        
        # Also store in legacy sensor_readings table
        await insert_sensor_reading({
            "device_id": device_id,
            "sensor_type": "dht22",
            "timestamp": timestamp,
            "data": {
                "temperature_c": temperature_c,
                "humidity_percent": humidity_percent
            },
            "location": location,
            "topic": topic
        })
    
    # Process WiFi data
    if "wifi" in payload:
        wifi_data = payload["wifi"]
        rssi = wifi_data.get("rssi", 0)
        
        # Get or create WiFi sensor
        sensor = await get_or_create_sensor(
            device_id, "wifi", "WiFi Signal Sensor", device
        )
        
        if sensor and sensor.get("id"):
            # Insert into wifi_readings table
            reading_id = await insert_wifi_reading(sensor["id"], rssi, timestamp)
            readings_inserted.append({
                "sensor_type": "wifi",
                "reading_id": reading_id,
                "data": {"rssi": rssi}
            })
            print(f"   ✅ Inserted WiFi reading: rssi={rssi}")
        
        # Also store in legacy sensor_readings table
        await insert_sensor_reading({
            "device_id": device_id,
            "sensor_type": "wifi",
            "timestamp": timestamp,
            "data": {"rssi": rssi},
            "location": location,
            "topic": topic
        })
    
    # 3. Broadcast to WebSocket clients
    if broadcast_to_websockets:
        websocket_message = {
            "type": "sensor_data_v2",
            "device_id": device_id,
            "device_name": device_name,
            "location": location,
            "timestamp": timestamp,
            "readings": readings_inserted
        }
        await broadcast_to_websockets(websocket_message)
        
        # Also send individual sensor messages for backward compatibility
        for reading in readings_inserted:
            await broadcast_to_websockets({
                "type": f"sensor_{reading['sensor_type']}",
                "sensor_type": reading["sensor_type"],
                "device_id": device_id,
                "timestamp": timestamp,
                "data": reading["data"],
                "location": location
            })
    
    print(f"✅ Successfully processed v2 JSON format for device {device_id}")

