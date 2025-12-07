"""
Test script to verify DHT22 sensor data is being received via MQTT and stored in database
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.sqlite_db import get_sensor_readings, init_database
from mqtt_broker.mqtt_client import MQTTClient
import json
from datetime import datetime

async def test_dht22_data():
    """Test DHT22 data reception and storage"""
    print("=" * 60)
    print("DHT22 Sensor Data Test")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    await init_database()
    print("   ✓ Database initialized")
    
    # Check existing DHT22 data
    print("\n2. Checking existing DHT22 data in database...")
    existing_readings = await get_sensor_readings(sensor_type="dht22", limit=10)
    print(f"   Found {len(existing_readings)} existing DHT22 readings")
    
    if existing_readings:
        print("\n   Recent DHT22 readings:")
        for i, reading in enumerate(existing_readings[:5], 1):
            print(f"   {i}. Device: {reading.get('device_id')}, "
                  f"Timestamp: {reading.get('timestamp')}")
            data = reading.get('data', {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    data = {}
            print(f"      Temperature: {data.get('temperature_c', 'N/A')}°C")
            print(f"      Humidity: {data.get('humidity_percent', 'N/A')}%")
            print(f"      Topic: {reading.get('topic', 'N/A')}")
    else:
        print("   ⚠️  No DHT22 readings found in database")
    
    # Test MQTT connection
    print("\n3. Testing MQTT connection...")
    mqtt_client = MQTTClient()
    
    # Track received messages
    received_messages = []
    
    async def test_message_handler(topic: str, payload: dict):
        """Test message handler to capture DHT22 messages"""
        if "dht22" in topic.lower():
            received_messages.append({
                "topic": topic,
                "payload": payload,
                "timestamp": datetime.now().isoformat()
            })
            print(f"\n   📨 DHT22 MQTT Message Received!")
            print(f"      Topic: {topic}")
            print(f"      Payload: {json.dumps(payload, indent=2)}")
            
            # Check for temperature and humidity
            temp = payload.get("temperature_c")
            hum = payload.get("humidity_percent")
            if temp is not None:
                print(f"      ✓ Temperature: {temp}°C")
            else:
                print(f"      ✗ Temperature: NOT FOUND")
            if hum is not None:
                print(f"      ✓ Humidity: {hum}%")
            else:
                print(f"      ✗ Humidity: NOT FOUND")
    
    try:
        print(f"   Connecting to broker: {mqtt_client.broker_host}:{mqtt_client.broker_port}")
        await mqtt_client.connect(retry_on_failure=False)
        # Wait a bit for connection to establish
        await asyncio.sleep(2)
        if mqtt_client.is_connected():
            print("   ✓ MQTT client connected")
            print(f"   Broker: {mqtt_client.broker_host}:{mqtt_client.broker_port}")
            
            # Check subscriptions
            print("\n   Subscribed topics:")
            for topic in mqtt_client.topics:
                if "dht22" in topic:
                    print(f"      ✓ {topic}")
            
            # Set message handler
            mqtt_client.set_message_handler(test_message_handler)
            print("\n   ⏳ Waiting 30 seconds for DHT22 messages...")
            print("   (Make sure your ESP8266 is running and publishing DHT22 data)")
            
            # Wait for messages
            await asyncio.sleep(30)
            
            # Check received messages
            print(f"\n4. Message Reception Summary:")
            print(f"   Received {len(received_messages)} DHT22 messages during test")
            
            if received_messages:
                print("\n   Message details:")
                for i, msg in enumerate(received_messages, 1):
                    print(f"   {i}. Topic: {msg['topic']}")
                    print(f"      Time: {msg['timestamp']}")
                    payload = msg['payload']
                    temp = payload.get("temperature_c")
                    hum = payload.get("humidity_percent")
                    if temp is not None and hum is not None:
                        print(f"      ✓ Has temperature ({temp}°C) and humidity ({hum}%)")
                    else:
                        print(f"      ✗ Missing temperature or humidity data")
                        print(f"      Payload keys: {list(payload.keys())}")
            else:
                print("   ⚠️  No DHT22 messages received!")
                print("\n   Troubleshooting:")
                print("   1. Check if ESP8266 is powered on and connected to WiFi")
                print("   2. Verify ESP8266 is publishing to: sensors/dht22/ESP8266_NODE_01")
                print("   3. Check MQTT broker is running and accessible")
                print("   4. Verify MQTT credentials in .env file")
            
            # Check database again after waiting
            print("\n5. Checking database after message reception...")
            await asyncio.sleep(2)  # Give time for database writes
            new_readings = await get_sensor_readings(sensor_type="dht22", limit=10)
            print(f"   Found {len(new_readings)} DHT22 readings (was {len(existing_readings)})")
            
            if len(new_readings) > len(existing_readings):
                print(f"   ✓ New readings added: {len(new_readings) - len(existing_readings)}")
                latest = new_readings[0]
                data = latest.get('data', {})
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except:
                        data = {}
                print(f"\n   Latest reading:")
                print(f"      Device: {latest.get('device_id')}")
                print(f"      Temperature: {data.get('temperature_c', 'N/A')}°C")
                print(f"      Humidity: {data.get('humidity_percent', 'N/A')}%")
            else:
                print("   ⚠️  No new readings in database")
                print("   This could mean:")
                print("      - Messages were received but not stored")
                print("      - No new messages were received")
            
            await mqtt_client.disconnect()
        else:
            print("   ✗ MQTT client not connected")
            print("   Check MQTT broker configuration")
    except Exception as e:
        print(f"   ✗ MQTT connection error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_dht22_data())

