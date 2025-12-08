"""
Quick script to test MQTT connection and check for DHT22 messages
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mqtt_broker.mqtt_client import MQTTClient
import json

async def test_connection():
    print("Testing MQTT Connection...")
    print("=" * 60)
    
    mqtt_client = MQTTClient()
    print(f"Broker: {mqtt_client.broker_host}:{mqtt_client.broker_port}")
    print(f"Username: {mqtt_client.username or '(none)'}")
    print(f"Password: {'*' * len(mqtt_client.password) if mqtt_client.password else '(none)'}")
    print()
    
    dht22_messages = []
    
    async def message_handler(topic: str, payload: dict):
        if "dht22" in topic.lower():
            dht22_messages.append({
                "topic": topic,
                "payload": payload,
                "timestamp": asyncio.get_event_loop().time()
            })
            print(f"\n🌡️ DHT22 Message Received!")
            print(f"   Topic: {topic}")
            print(f"   Temperature: {payload.get('temperature_c', 'N/A')}°C")
            print(f"   Humidity: {payload.get('humidity_percent', 'N/A')}%")
            print(f"   Full payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("Connecting to MQTT broker...")
        await mqtt_client.connect(retry_on_failure=False)
        await asyncio.sleep(2)  # Wait for connection
        
        if mqtt_client.is_connected():
            print("✓ Connected successfully!")
            print(f"\nSubscribed topics:")
            for topic in mqtt_client.topics:
                print(f"  - {topic}")
            
            mqtt_client.set_message_handler(message_handler)
            
            print(f"\n⏳ Listening for DHT22 messages for 30 seconds...")
            print("   (Make sure ESP8266 is running and publishing data)")
            await asyncio.sleep(30)
            
            print(f"\n📊 Summary:")
            print(f"   Received {len(dht22_messages)} DHT22 messages")
            
            if dht22_messages:
                print(f"\n   Latest message:")
                latest = dht22_messages[-1]
                print(f"   Topic: {latest['topic']}")
                print(f"   Temperature: {latest['payload'].get('temperature_c', 'N/A')}°C")
                print(f"   Humidity: {latest['payload'].get('humidity_percent', 'N/A')}%")
            else:
                print("\n   ⚠️  No DHT22 messages received!")
                print("   Possible issues:")
                print("   1. ESP8266 not powered on or not connected")
                print("   2. ESP8266 not publishing to sensors/dht22/+ topic")
                print("   3. MQTT broker not receiving messages")
                print("   4. Network connectivity issue")
            
            await mqtt_client.disconnect()
        else:
            print("✗ Connection failed!")
            print("\nTroubleshooting:")
            print("1. Check if MQTT broker is running")
            print("2. Verify broker host and port are correct")
            print("3. Check network connectivity")
            print("4. Verify authentication credentials if required")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())


