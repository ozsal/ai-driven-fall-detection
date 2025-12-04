"""
Fall Detection AI/ML Model
Implements multi-sensor fusion and fall severity scoring
"""

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Fallback: use math for basic calculations
    import math

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from database.sqlite_db import get_recent_room_sensor_data

class FallDetector:
    """Fall detection using multi-sensor fusion"""
    
    def __init__(self):
        self.model_loaded = False
        # Updated weights for room-sensor-only detection (no wearable)
        self.weights = {
            "room_verification": 0.5,  # Increased weight since no wearable
            "duration": 0.3,
            "environmental": 0.2
        }
    
    async def load_model(self):
        """Load ML model (placeholder for actual model loading)"""
        # In production, load trained model here
        # self.model = tf.keras.models.load_model('models/fall_detection_model.h5')
        self.model_loaded = True
        print("Fall detection model loaded")
    
    async def detect_fall(
        self,
        room_sensor_data: List[Dict]
    ) -> Dict:
        """
        Detect fall using room sensors only (PIR, Ultrasonic, DHT22)
        
        Args:
            room_sensor_data: Recent room sensor readings from ESP8266 nodes
            
        Returns:
            Dictionary with fall_detected, severity_score, verified, location
        """
        
        # Calculate room verification score (PIR + Ultrasonic)
        room_score = self._calculate_room_verification_score(room_sensor_data)
        
        # Calculate duration score (time since last movement)
        duration_score = self._calculate_duration_score(room_sensor_data)
        
        # Calculate environmental score (temperature/humidity changes)
        env_score = self._calculate_environmental_score(room_sensor_data)
        
        # Calculate overall severity score (no accelerometer component)
        severity_score = (
            room_score * self.weights["room_verification"] +
            duration_score * self.weights["duration"] +
            env_score * self.weights["environmental"]
        )
        
        # Determine if fall is detected (lower threshold since no wearable confirmation)
        fall_detected = severity_score >= 6.0  # Threshold adjusted for room-sensor-only
        
        # Verify with room sensors
        verified = self._verify_with_room_sensors(room_sensor_data)
        
        # Determine location
        location = self._determine_location(room_sensor_data)
        
        return {
            "fall_detected": fall_detected,
            "severity_score": round(severity_score, 2),
            "verified": verified,
            "location": location,
            "component_scores": {
                "room_verification": room_score,
                "duration": duration_score,
                "environmental": env_score
            }
        }
    
    # Removed _calculate_accelerometer_score - no longer needed without wearable device
    
    def _calculate_room_verification_score(self, room_data: List[Dict]) -> float:
        """Calculate score based on room sensor verification"""
        if not room_data:
            return 0.0
        
        score = 0.0
        factors = 0
        
        # Check PIR sensors (no motion = person on ground)
        for reading in room_data:
            if "sensors" in reading and "pir" in reading["sensors"]:
                pir_motion = reading["sensors"]["pir"].get("motion_detected", True)
                if not pir_motion:  # No motion detected
                    score += 3.0
                factors += 1
            
            # Check ultrasonic (distance to ground)
            if "sensors" in reading and "ultrasonic" in reading["sensors"]:
                distance = reading["sensors"]["ultrasonic"].get("distance_cm", 400)
                if distance < 50:  # Close to ground
                    score += 3.0
                elif distance < 100:
                    score += 1.5
                factors += 1
        
        if factors > 0:
            return min(10.0, score / factors * 3.33)  # Normalize to 0-10
        return 0.0
    
    def _calculate_duration_score(self, room_data: List[Dict]) -> float:
        """Calculate score based on duration of inactivity"""
        if not room_data:
            return 0.0
        
        # Check how long PIR has been inactive
        inactive_duration = 0
        last_motion_time = None
        
        for reading in sorted(room_data, key=lambda x: x.get("timestamp", 0), reverse=True):
            if "sensors" in reading and "pir" in reading["sensors"]:
                if reading["sensors"]["pir"].get("motion_detected", False):
                    break
                else:
                    inactive_duration += 2  # Assuming 2-second intervals
        
        # Score based on duration
        if inactive_duration >= 30:  # 30+ seconds
            return 10.0
        elif inactive_duration >= 20:
            return 7.0
        elif inactive_duration >= 10:
            return 4.0
        else:
            return 2.0
    
    def _calculate_environmental_score(self, room_data: List[Dict]) -> float:
        """Calculate score based on environmental changes"""
        if len(room_data) < 2:
            return 0.0
        
        # Check for sudden temperature/humidity changes
        recent = room_data[0]
        older = room_data[-1] if len(room_data) > 1 else recent
        
        temp_change = 0
        hum_change = 0
        
        if "sensors" in recent and "dht22" in recent["sensors"]:
            recent_temp = recent["sensors"]["dht22"].get("temperature_c", 0)
            recent_hum = recent["sensors"]["dht22"].get("humidity_percent", 0)
            
            if "sensors" in older and "dht22" in older["sensors"]:
                older_temp = older["sensors"]["dht22"].get("temperature_c", 0)
                older_hum = older["sensors"]["dht22"].get("humidity_percent", 0)
                
                temp_change = abs(recent_temp - older_temp)
                hum_change = abs(recent_hum - older_hum)
        
        # Score based on changes (door opening, etc.)
        score = 0.0
        if temp_change > 2.0:
            score += 3.0
        if hum_change > 5.0:
            score += 2.0
        
        return min(10.0, score)
    
    def _verify_with_room_sensors(self, room_data: List[Dict]) -> bool:
        """Verify fall with room sensor data"""
        if not room_data:
            return False
        
        verification_factors = 0
        
        for reading in room_data:
            # PIR: No motion
            if "sensors" in reading and "pir" in reading["sensors"]:
                if not reading["sensors"]["pir"].get("motion_detected", True):
                    verification_factors += 1
            
            # Ultrasonic: Close to ground
            if "sensors" in reading and "ultrasonic" in reading["sensors"]:
                distance = reading["sensors"]["ultrasonic"].get("distance_cm", 400)
                if distance < 50:
                    verification_factors += 1
        
        # Verified if at least 2 factors present
        return verification_factors >= 2
    
    def _determine_location(self, room_data: List[Dict]) -> str:
        """Determine location based on sensor data"""
        if not room_data:
            return "unknown"
        
        # Get device location from most recent reading
        latest = room_data[0]
        return latest.get("location", latest.get("device_id", "unknown"))

