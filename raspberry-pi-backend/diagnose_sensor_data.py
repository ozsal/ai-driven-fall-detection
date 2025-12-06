#!/usr/bin/env python3
"""
Diagnostic script to check why sensor data is not appearing
"""

import asyncio
import aiosqlite
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "fall_detection.db")

async def check_database():
    """Check database for sensor readings"""
    print("\n=== Database Check ===")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found at: {DB_PATH}")
        return
    
    print(f"✓ Database file exists: {DB_PATH}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Check sensor_readings table
        cursor = await db.execute("SELECT COUNT(*) as count FROM sensor_readings")
        row = await cursor.fetchone()
        total_readings = row[0] if row else 0
        print(f"Total sensor readings in database: {total_readings}")
        
        if total_readings > 0:
            # Get recent readings
            cursor = await db.execute("""
                SELECT device_id, sensor_type, timestamp, topic, received_at
                FROM sensor_readings
                ORDER BY id DESC
                LIMIT 10
            """)
            rows = await cursor.fetchall()
            
            print("\nRecent sensor readings (last 10):")
            for row in rows:
                print(f"  - Device: {row[0]}, Type: {row[1]}, Topic: {row[3]}, Time: {row[4]}")
        else:
            print("⚠️  No sensor readings found in database")
        
        # Check devices table
        cursor = await db.execute("SELECT COUNT(*) as count FROM devices")
        row = await cursor.fetchone()
        total_devices = row[0] if row else 0
        print(f"\nTotal devices in database: {total_devices}")
        
        if total_devices > 0:
            cursor = await db.execute("""
                SELECT device_id, device_type, status, last_seen, location
                FROM devices
                ORDER BY last_seen DESC
            """)
            rows = await cursor.fetchall()
            
            print("\nDevices:")
            for row in rows:
                print(f"  - {row[0]} ({row[1]}): Status={row[2]}, Last seen: {row[3]}, Location: {row[4]}")
        else:
            print("⚠️  No devices found in database")

async def check_mqtt_topics():
    """Check expected MQTT topics"""
    print("\n=== Expected MQTT Topics ===")
    topics = [
        "sensors/pir/+",
        "sensors/ultrasonic/+",
        "sensors/dht22/+",
        "sensors/combined/+",
        "wearable/fall/+",
        "wearable/accelerometer/+",
        "devices/+/status"
    ]
    
    print("Backend subscribes to these topics:")
    for topic in topics:
        print(f"  - {topic}")
    
    print("\nMake sure your sensors are publishing to matching topics!")
    print("Example topics your sensors should use:")
    print("  - sensors/dht22/ESP8266_001")
    print("  - sensors/pir/ESP8266_001")
    print("  - sensors/ultrasonic/ESP8266_001")
    print("  - sensors/combined/ESP8266_001")

async def main():
    print("=" * 60)
    print("Sensor Data Diagnostic Tool")
    print("=" * 60)
    
    await check_database()
    await check_mqtt_topics()
    
    print("\n=== Troubleshooting Steps ===")
    print("1. Check if MQTT broker is running:")
    print("   - Check backend logs for 'MQTT client connected successfully'")
    print("   - Check if you see 'Subscribed to: sensors/...' messages")
    
    print("\n2. Check if sensors are publishing:")
    print("   - Verify sensors are powered on and connected to WiFi")
    print("   - Check sensor code is publishing to correct topics")
    print("   - Use MQTT client (like mosquitto_sub) to verify messages:")
    print("     mosquitto_sub -h 10.162.131.191 -p 8883 -u ozsal -P '@@Ozsal23##' -t 'sensors/#' -v")
    
    print("\n3. Check backend logs:")
    print("   - Look for '✓ Stored sensor reading #X' messages")
    print("   - Look for any error messages")
    
    print("\n4. Test API endpoint:")
    print("   curl http://10.162.131.191:8000/api/sensor-readings?limit=5")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

