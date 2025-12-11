#!/usr/bin/env python3
"""
Test script to verify MQTT message storage is working
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.sqlite_db import insert_sensor_reading, get_sensor_readings, count_sensor_readings, init_database, DB_PATH
from datetime import datetime

async def test_database_insertion():
    """Test if database insertion works"""
    print("=" * 60)
    print("Testing Database Insertion")
    print("=" * 60)
    
    # Initialize database
    await init_database()
    print(f"✓ Database initialized at: {DB_PATH}")
    
    # Test insertion
    test_reading = {
        "device_id": "TEST_DEVICE",
        "sensor_type": "test",
        "timestamp": int(datetime.utcnow().timestamp()),
        "data": {"test_value": 123, "test_string": "hello"},
        "location": "test_location",
        "topic": "test/topic"
    }
    
    try:
        print(f"\n📝 Attempting to insert test reading...")
        reading_id = await insert_sensor_reading(test_reading)
        print(f"✅ SUCCESS: Inserted reading with ID: {reading_id}")
        
        # Verify it was stored
        count = await count_sensor_readings()
        print(f"✓ Total readings in database: {count}")
        
        if count > 0:
            readings = await get_sensor_readings(limit=1)
            if readings:
                print(f"✓ Retrieved reading: {readings[0]}")
            else:
                print("⚠️ Warning: Count > 0 but couldn't retrieve reading")
        else:
            print("❌ ERROR: Reading was inserted but count is still 0!")
            
    except Exception as e:
        print(f"❌ ERROR inserting test reading: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def check_mqtt_setup():
    """Check MQTT client setup"""
    print("\n" + "=" * 60)
    print("Checking MQTT Setup")
    print("=" * 60)
    
    try:
        from mqtt_broker.mqtt_client import MQTTClient
        
        mqtt_client = MQTTClient()
        print(f"✓ MQTT client created")
        print(f"  Broker: {mqtt_client.broker_host}:{mqtt_client.broker_port}")
        print(f"  Topics: {mqtt_client.topics}")
        
        # Try to connect
        try:
            await mqtt_client.connect(retry_on_failure=False)
        except TypeError:
            await mqtt_client.connect()
        
        if mqtt_client.is_connected():
            print(f"✅ MQTT client is connected")
        else:
            print(f"⚠️ MQTT client is NOT connected")
            print(f"  This is OK if broker is not running, but messages won't be received")
        
        # Check if message handler is set
        if mqtt_client.message_handler:
            print(f"✓ Message handler is set")
        else:
            print(f"❌ Message handler is NOT set - messages won't be processed!")
        
        if mqtt_client.event_loop:
            print(f"✓ Event loop is available")
        else:
            print(f"❌ Event loop is NOT available - messages can't be processed!")
            
    except Exception as e:
        print(f"❌ Error checking MQTT setup: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("\n" + "=" * 60)
    print("MQTT Storage Diagnostic Test")
    print("=" * 60 + "\n")
    
    # Test database
    db_ok = await test_database_insertion()
    
    # Check MQTT
    await check_mqtt_setup()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if db_ok:
        print("✅ Database insertion is working")
    else:
        print("❌ Database insertion is NOT working")
    
    print("\nNext steps:")
    print("1. Check backend logs when MQTT messages arrive")
    print("2. Look for: '📨 Received MQTT message'")
    print("3. Look for: '🔄 Scheduling message handler'")
    print("4. Look for: '💾 Attempting to store reading'")
    print("5. Look for: '✅ Inserted reading with ID: X' or error messages")

if __name__ == "__main__":
    asyncio.run(main())










