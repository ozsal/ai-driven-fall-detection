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

from database.mongodb import get_database, init_database
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
    
    # Initialize MQTT client
    mqtt_client = MQTTClient()
    await mqtt_client.connect()
    print("MQTT client connected")
    
    # Initialize fall detector
    fall_detector = FallDetector()
    await fall_detector.load_model()
    print("Fall detector model loaded")
    
    # Initialize alert manager
    alert_manager = AlertManager()
    print("Alert manager initialized")
    
    # Start MQTT message processing
    mqtt_client.set_message_handler(handle_mqtt_message)
    
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
    """Process incoming MQTT messages"""
    try:
        # Store sensor reading in database
        db = await get_database()
        await db.sensor_readings.insert_one({
            **payload,
            "received_at": datetime.utcnow()
        })
        
        # Check for fall detection if from wearable
        if "wearable" in topic or "MICROBIT" in payload.get("device_id", ""):
            await process_fall_detection(payload)
        
        # Broadcast to WebSocket connections
        await broadcast_to_websockets({
            "type": "sensor_data",
            "topic": topic,
            "data": payload
        })
        
    except Exception as e:
        print(f"Error handling MQTT message: {e}")

async def process_fall_detection(payload: dict):
    """Process potential fall detection"""
    global fall_detector, alert_manager
    
    if not fall_detector or not alert_manager:
        return
    
    try:
        # Get room sensor data for verification
        room_data = await get_recent_room_sensor_data()
        
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
            db = await get_database()
            event_id = str(await db.fall_events.insert_one(fall_event).inserted_id)
            
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

async def get_recent_room_sensor_data():
    """Get recent room sensor readings for verification"""
    db = await get_database()
    recent_readings = await db.sensor_readings.find({
        "device_id": {"$regex": "ESP8266"},
        "received_at": {
            "$gte": datetime.utcnow() - timedelta(seconds=30)
        }
    }).sort("received_at", -1).limit(10).to_list(length=10)
    
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
async def get_devices():
    """Get all device statuses"""
    db = await get_database()
    devices = await db.devices.find().to_list(length=100)
    return devices

@app.get("/api/sensor-readings")
async def get_sensor_readings(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    limit: int = 100
):
    """Get sensor readings with optional filters"""
    db = await get_database()
    query = {}
    
    if device_id:
        query["device_id"] = device_id
    if sensor_type:
        query["sensor_type"] = sensor_type
    
    readings = await db.sensor_readings.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
    return readings

@app.get("/api/fall-events")
async def get_fall_events(
    user_id: Optional[str] = None,
    limit: int = 50
):
    """Get fall events"""
    db = await get_database()
    query = {}
    
    if user_id:
        query["user_id"] = user_id
    
    events = await db.fall_events.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
    return events

@app.get("/api/fall-events/{event_id}")
async def get_fall_event(event_id: str):
    """Get specific fall event"""
    db = await get_database()
    from bson import ObjectId
    
    event = await db.fall_events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@app.post("/api/fall-events/{event_id}/acknowledge")
async def acknowledge_fall_event(event_id: str):
    """Acknowledge a fall event"""
    db = await get_database()
    from bson import ObjectId
    
    result = await db.fall_events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"acknowledged": True, "acknowledged_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
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
    db = await get_database()
    
    total_events = await db.fall_events.count_documents({})
    recent_events = await db.fall_events.count_documents({
        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    total_readings = await db.sensor_readings.count_documents({})
    active_devices = await db.devices.count_documents({"status": "online"})
    
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

