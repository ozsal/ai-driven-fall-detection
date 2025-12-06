"""
FastAPI Main Application
Raspberry Pi Backend for Fall Detection System
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
from contextlib import asynccontextmanager

from database.sqlite_db import (
    init_database, insert_sensor_reading, insert_fall_event,
    get_sensor_readings as db_get_sensor_readings, get_fall_events, get_fall_event,
    acknowledge_fall_event, get_devices as db_get_devices, get_recent_room_sensor_data,
    count_fall_events, count_sensor_readings, count_active_devices
)
from mqtt_broker.mqtt_client import MQTTClient
from ml_models.fall_detector import FallDetector
from alerts.alert_manager import AlertManager

# ==================== Global Variables ====================
mqtt_client: Optional[MQTTClient] = None
fall_detector: Optional[FallDetector] = None
alert_manager: Optional[AlertManager] = None
websocket_connections: List[WebSocket] = []

# ==================== Pydantic Models ====================
class SensorReading(BaseModel):
    device_id: str
    sensor_type: str
    timestamp: int
    data: dict

class FallEvent(BaseModel):
    user_id: str
    timestamp: datetime
    severity_score: float
    verified: bool
    sensor_data: dict
    location: Optional[str] = None

class DeviceStatus(BaseModel):
    device_id: str
    status: str
    last_seen: datetime
    location: Optional[str] = None

class AlertResponse(BaseModel):
    alert_id: str
    event_id: str
    sent_at: datetime
    channels: List[str]  # ['push', 'email', 'dashboard']

# ==================== Lifespan Events ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global mqtt_client, fall_detector, alert_manager
    
    # Startup
    print("Initializing Fall Detection System...")
    
    # Initialize database
    await init_database()
    print("Database initialized")
    
    # Initialize MQTT client (non-blocking - allow API to start even if MQTT fails)
    mqtt_client = MQTTClient()
    try:
        # Try with retry_on_failure parameter (newer version)
        try:
            await mqtt_client.connect(retry_on_failure=False)
        except TypeError:
            # Fallback for older version without retry_on_failure parameter
            await mqtt_client.connect()
        
        if mqtt_client.is_connected():
            print("✓ MQTT client connected")
            # Start MQTT message processing
            mqtt_client.set_message_handler(handle_mqtt_message)
        else:
            print("⚠️  MQTT client initialized but not connected. Will retry in background.")
    except Exception as e:
        print(f"⚠️  MQTT initialization failed: {e}")
        print("⚠️  API will continue without MQTT. Start MQTT broker to enable sensor data reception.")
    
    # Initialize fall detector
    fall_detector = FallDetector()
    await fall_detector.load_model()
    print("✓ Fall detector model loaded")
    
    # Initialize alert manager
    alert_manager = AlertManager()
    print("✓ Alert manager initialized")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if mqtt_client:
        await mqtt_client.disconnect()
    print("Shutdown complete")

# ==================== FastAPI App ====================
app = FastAPI(
    title="Fall Detection System API",
    description="REST API for IoT-based fall detection system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MQTT Message Handler ====================
async def handle_mqtt_message(topic: str, payload: dict):
    """Process incoming MQTT messages and store in database in real-time"""
    try:
        # Ensure payload is a dictionary
        # If payload is a primitive type (int, float, str), convert it to a dict
        if not isinstance(payload, dict):
            if isinstance(payload, (int, float)):
                payload = {"value": payload, "raw": payload}
            elif isinstance(payload, str):
                payload = {"value": payload, "raw": payload}
            else:
                # Try to convert to dict if possible
                try:
                    payload = dict(payload)
                except:
                    payload = {"value": str(payload), "raw": payload}
        
        # Parse topic parts for extracting information
        topic_parts = topic.split("/")
        
        # Extract device_id from payload or topic
        # Topic format: sensors/pir/ESP8266_NODE_01 -> device_id is in topic_parts[2]
        device_id = payload.get("device_id") or payload.get("deviceId")
        if not device_id and len(topic_parts) >= 3:
            # Extract from topic (e.g., "sensors/pir/ESP8266_NODE_01" -> "ESP8266_NODE_01")
            device_id = topic_parts[2]
        if not device_id:
            device_id = "unknown"
        
        # Extract sensor_type from topic or payload
        sensor_type = payload.get("sensor_type") or payload.get("sensorType")
        if not sensor_type:
            # Try to extract from topic (e.g., "sensors/dht22/ESP8266_001" -> "dht22")
            if len(topic_parts) >= 2:
                sensor_type = topic_parts[1]  # e.g., "dht22", "pir", "ultrasonic", "combined"
            else:
                sensor_type = "unknown"
        
        # Extract location from payload or topic
        location = payload.get("location") or payload.get("Location")
        # Don't use topic_parts[2] for location since that's device_id
        
        # Extract timestamp from payload or use current time
        timestamp = payload.get("timestamp") or payload.get("time") or payload.get("Timestamp")
        if timestamp:
            # Convert to int if it's a float or string
            if isinstance(timestamp, float):
                timestamp = int(timestamp)
            elif isinstance(timestamp, str):
                try:
                    timestamp = int(float(timestamp))
                except:
                    timestamp = int(datetime.utcnow().timestamp())
        else:
            timestamp = int(datetime.utcnow().timestamp())
        
        # Extract actual sensor data (exclude metadata fields)
        metadata_fields = {"device_id", "deviceId", "sensor_type", "sensorType", 
                          "timestamp", "time", "Timestamp", "location", "Location", 
                          "topic", "received_at", "receivedAt"}
        sensor_data = {k: v for k, v in payload.items() if k not in metadata_fields}
        
        # If sensor_data is empty or only has "value"/"raw" (from primitive conversion),
        # create proper sensor data structure
        if not sensor_data or (len(sensor_data) <= 2 and "value" in payload):
            # For primitive payloads (like "1" or "25.5"), use the value
            if "value" in payload:
                # Create sensor-specific data structure
                if sensor_type == "pir":
                    sensor_data = {"motion_detected": bool(payload.get("value") == "1" or payload.get("value") == 1)}
                elif sensor_type == "ultrasonic":
                    try:
                        distance = float(payload.get("value", 0))
                        sensor_data = {"distance_cm": distance}
                    except:
                        sensor_data = {"distance_cm": 0.0}
                elif sensor_type == "dht22":
                    # DHT22 should have JSON, but handle primitive case
                    sensor_data = {"value": payload.get("value")}
                else:
                    sensor_data = {"value": payload.get("value")}
            else:
                # Use entire payload as data, removing metadata
                sensor_data = payload.copy()
                for key in metadata_fields:
                    sensor_data.pop(key, None)
        
        # Prepare data for database insertion
        db_reading = {
            "device_id": device_id,
            "sensor_type": sensor_type,
            "timestamp": timestamp,
            "data": sensor_data,  # This will be JSON stringified in insert_sensor_reading
            "location": location,
            "topic": topic
        }
        
        # Store sensor reading in database (real-time storage)
        reading_id = await insert_sensor_reading(db_reading)
        print(f"✓ Stored sensor reading #{reading_id} from {device_id} ({sensor_type}) on topic '{topic}' at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Device ID: {device_id}, Sensor Type: {sensor_type}, Location: {location}")
        print(f"  Data: {sensor_data}")
        
        # Check for fall detection if from wearable (legacy support)
        if "wearable" in topic or "MICROBIT" in device_id.upper():
            await process_fall_detection(payload)
        
        # Broadcast to WebSocket connections for real-time frontend updates
        await broadcast_to_websockets({
            "type": "sensor_data",
            "topic": topic,
            "device_id": device_id,
            "sensor_type": sensor_type,
            "timestamp": timestamp,
            "data": sensor_data,
            "location": location
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error handling MQTT message from topic '{topic}': {e}")
        print(f"Payload: {payload}")
        traceback.print_exc()

async def process_fall_detection(payload: dict):
    """Process potential fall detection"""
    global fall_detector, alert_manager
    
    if not fall_detector or not alert_manager:
        return
    
    try:
        # Get room sensor data for verification
        room_data = await fetch_recent_room_sensor_data()
        
        # Run fall detection algorithm
        result = await fall_detector.detect_fall(
            wearable_data=payload,
            room_sensor_data=room_data
        )
        
        if result["fall_detected"]:
            # Create fall event
            fall_event = {
                "user_id": payload.get("device_id", "unknown"),
                "timestamp": datetime.utcnow(),
                "severity_score": result["severity_score"],
                "verified": result["verified"],
                "sensor_data": {
                    "wearable": payload,
                    "room_sensors": room_data
                },
                "location": result.get("location", "unknown")
            }
            
            # Save to database
            event_id = await insert_fall_event(fall_event)
            
            # Trigger alerts
            await alert_manager.send_fall_alert(fall_event, event_id)
            
            # Broadcast to WebSocket
            await broadcast_to_websockets({
                "type": "fall_event",
                "event": fall_event,
                "event_id": event_id
            })
            
    except Exception as e:
        print(f"Error processing fall detection: {e}")

async def fetch_recent_room_sensor_data():
    """Get recent room sensor readings for verification"""
    # Convert 30 seconds to minutes (approximately 0.5 minutes)
    recent_readings = await get_recent_room_sensor_data(minutes=1, limit=20)
    return recent_readings

# ==================== WebSocket Manager ====================
async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []
    for connection in websocket_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        websocket_connections.remove(conn)

# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fall Detection System API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mqtt_connected": mqtt_client.is_connected() if mqtt_client else False,
        "database_connected": True,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/devices", response_model=List[DeviceStatus])
async def get_devices_endpoint():
    """Get all device statuses"""
    devices = await db_get_devices()
    return devices

@app.get("/api/sensor-readings")
async def get_sensor_readings_endpoint(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    limit: int = 100
):
    """Get sensor readings with optional filters"""
    try:
        readings = await db_get_sensor_readings(
            device_id=device_id,
            sensor_type=sensor_type,
            limit=limit
        )
        return readings
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error fetching sensor readings: {e}")
        print(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching sensor readings: {str(e)}. Check server logs for details."
        )

@app.get("/api/fall-events")
async def get_fall_events(
    user_id: Optional[str] = None,
    limit: int = 50
):
    """Get fall events"""
    events = await get_fall_events(user_id=user_id, limit=limit)
    return events

@app.get("/api/fall-events/{event_id}")
async def get_fall_event(event_id: str):
    """Get specific fall event"""
    event = await get_fall_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@app.post("/api/fall-events/{event_id}/acknowledge")
async def acknowledge_fall_event_endpoint(event_id: str):
    """Acknowledge a fall event"""
    result = await acknowledge_fall_event(event_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event acknowledged", "event_id": event_id}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back or process message
            await websocket.send_json({"type": "ack", "message": "received"})
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)

@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    total_events = await count_fall_events()
    recent_events = await count_fall_events({
        "timestamp_gte": datetime.utcnow() - timedelta(days=7)
    })
    total_readings = await count_sensor_readings()
    active_devices = await count_active_devices()
    
    return {
        "total_fall_events": total_events,
        "recent_events_7d": recent_events,
        "total_sensor_readings": total_readings,
        "active_devices": active_devices
    }

# ==================== Run Server ====================
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

