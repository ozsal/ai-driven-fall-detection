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
    get_sensor_readings, get_fall_events, get_fall_event,
    acknowledge_fall_event, get_devices, get_recent_room_sensor_data,
    count_fall_events, count_sensor_readings, count_active_devices
)
from mqtt_broker.mqtt_client import MQTTClient
from ml_models.fall_detector import FallDetector
from ml_models.environment_advisor import EnvironmentAdvisor
from alerts.alert_manager import AlertManager

# ==================== Global Variables ====================
mqtt_client: Optional[MQTTClient] = None
fall_detector: Optional[FallDetector] = None
environment_advisor: Optional[EnvironmentAdvisor] = None
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
    global mqtt_client, fall_detector, environment_advisor, alert_manager
    
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
    
    # Initialize environment advisor
    environment_advisor = EnvironmentAdvisor()
    print("Environment advisor initialized")
    
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
        sensor_data = {
            **payload,
            "topic": topic,
            "received_at": datetime.utcnow()
        }
        await insert_sensor_reading(sensor_data)
        
        # Check for fall detection based on room sensors
        # Trigger analysis when we receive ESP8266 sensor data
        if "sensors" in topic or "ESP8266" in payload.get("device_id", ""):
            await process_fall_detection()
        
        # Broadcast to WebSocket connections
        await broadcast_to_websockets({
            "type": "sensor_data",
            "topic": topic,
            "data": payload
        })
        
    except Exception as e:
        print(f"Error handling MQTT message: {e}")

async def process_fall_detection():
    """Process potential fall detection using room sensors only"""
    global fall_detector, alert_manager
    
    if not fall_detector or not alert_manager:
        return
    
    try:
        # Get recent room sensor data for analysis
        room_data = await fetch_recent_room_sensor_data()
        
        # Need minimum data points for reliable detection
        if len(room_data) < 3:
            return
        
        # Run fall detection algorithm (room sensors only)
        result = await fall_detector.detect_fall(
            room_sensor_data=room_data
        )
        
        if result["fall_detected"]:
            # Get device ID from most recent sensor reading
            device_id = room_data[0].get("device_id", "unknown") if room_data else "unknown"
            
            # Create fall event
            fall_event = {
                "user_id": device_id,  # Using device_id instead of user_id
                "timestamp": datetime.utcnow(),
                "severity_score": result["severity_score"],
                "verified": result["verified"],
                "sensor_data": {
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
    recent_readings = await get_recent_room_sensor_data(seconds=30)
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
    devices = await get_devices()
    return devices

@app.get("/api/sensor-readings")
async def get_sensor_readings(
    device_id: Optional[str] = None,
    sensor_type: Optional[str] = None,
    limit: int = 100
):
    """Get sensor readings with optional filters"""
    readings = await get_sensor_readings(
        device_id=device_id,
        sensor_type=sensor_type,
        limit=limit
    )
    return readings

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Fall Detection System API",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    try:
        total_events = await count_fall_events()
        
        # Calculate recent events (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_events = await count_fall_events({
            "timestamp_gte": seven_days_ago
        })
        
        total_readings = await count_sensor_readings()
        active_devices = await count_active_devices()
        
        return {
            "total_fall_events": total_events,
            "recent_events_7d": recent_events,
            "total_sensor_readings": total_readings,
            "active_devices": active_devices
        }
    except Exception as e:
        print(f"Error in get_statistics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@app.get("/api/environment/recommendations")
async def get_environment_recommendations(
    device_id: Optional[str] = None,
    hours: int = 24
):
    """Get environment recommendations based on sensor data analysis"""
    global environment_advisor
    
    if environment_advisor is None:
        environment_advisor = EnvironmentAdvisor()
    
    try:
        recommendations = await environment_advisor.analyze_environment(
            device_id=device_id,
            hours=hours
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing environment: {str(e)}"
        )

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

