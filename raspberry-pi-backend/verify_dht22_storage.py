"""
Verify DHT22 data is being stored in database
"""

import asyncio
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.sqlite_db import get_sensor_readings, init_database

async def check_dht22_storage():
    print("=" * 60)
    print("DHT22 Database Storage Verification")
    print("=" * 60)
    
    await init_database()
    
    # Check all sensor types
    print("\n1. Checking all sensor readings in database:")
    all_readings = await get_sensor_readings(limit=20)
    print(f"   Total readings: {len(all_readings)}")
    
    # Group by sensor type
    by_type = {}
    for reading in all_readings:
        sensor_type = reading.get('sensor_type', 'unknown')
        by_type[sensor_type] = by_type.get(sensor_type, 0) + 1
    
    print("\n   Readings by sensor type:")
    for sensor_type, count in by_type.items():
        print(f"   - {sensor_type}: {count}")
    
    # Check DHT22 specifically
    print("\n2. Checking DHT22 readings:")
    dht22_readings = await get_sensor_readings(sensor_type="dht22", limit=10)
    print(f"   Found {len(dht22_readings)} DHT22 readings")
    
    if dht22_readings:
        print("\n   Recent DHT22 readings:")
        for i, reading in enumerate(dht22_readings[:5], 1):
            print(f"\n   {i}. Reading ID: {reading.get('id')}")
            print(f"      Device: {reading.get('device_id')}")
            print(f"      Timestamp: {reading.get('timestamp')}")
            print(f"      Topic: {reading.get('topic')}")
            
            data = reading.get('data', {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    data = {}
            
            temp = data.get('temperature_c')
            hum = data.get('humidity_percent')
            
            if temp is not None:
                print(f"      ✓ Temperature: {temp}°C")
            else:
                print(f"      ✗ Temperature: NOT FOUND")
            
            if hum is not None:
                print(f"      ✓ Humidity: {hum}%")
            else:
                print(f"      ✗ Humidity: NOT FOUND")
            
            if temp is None and hum is None:
                print(f"      ⚠️  Data field: {data}")
    else:
        print("   ⚠️  No DHT22 readings found in database!")
        print("\n   Possible reasons:")
        print("   1. ESP8266 is not publishing DHT22 data")
        print("   2. DHT22 sensor is not connected or not working")
        print("   3. Messages are being received but not stored")
        print("   4. Topic mismatch (ESP8266 publishing to different topic)")
    
    # Check recent readings from all sensors to see what's coming in
    print("\n3. Recent sensor readings (all types):")
    recent = await get_sensor_readings(limit=10)
    for i, reading in enumerate(recent[:5], 1):
        print(f"   {i}. {reading.get('sensor_type')} from {reading.get('device_id')} - Topic: {reading.get('topic')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_dht22_storage())

