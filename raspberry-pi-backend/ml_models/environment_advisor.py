"""
Environment Advisor - ML-based Room Environment Recommendations
Analyzes sensor data and provides suggestions to optimize room conditions
for fall prevention and comfort.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database.sqlite_db import get_recent_room_sensor_data
import math

class EnvironmentAdvisor:
    """Provides environment recommendations based on sensor data analysis"""
    
    # Optimal ranges for fall prevention
    OPTIMAL_TEMP_MIN = 20.0  # °C
    OPTIMAL_TEMP_MAX = 24.0  # °C
    OPTIMAL_HUMIDITY_MIN = 40.0  # %
    OPTIMAL_HUMIDITY_MAX = 60.0  # %
    
    # Risk thresholds
    TEMP_RISK_HIGH = 26.0  # Too hot
    TEMP_RISK_LOW = 18.0   # Too cold
    HUMIDITY_RISK_HIGH = 70.0  # Too humid
    HUMIDITY_RISK_LOW = 30.0   # Too dry
    
    # Motion activity thresholds (for room usage analysis)
    LOW_ACTIVITY_THRESHOLD = 0.2  # Less than 20% motion detected
    HIGH_ACTIVITY_THRESHOLD = 0.8  # More than 80% motion detected
    
    def __init__(self):
        self.recommendations_cache = {}
        self.last_analysis = None
    
    async def analyze_environment(
        self,
        device_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict:
        """
        Analyze room environment and provide recommendations
        
        Args:
            device_id: Specific device to analyze (None for all devices)
            hours: Number of hours of data to analyze
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        # Get recent sensor data (convert hours to seconds)
        # Note: get_recent_room_sensor_data has a limit, so we'll get what we can
        seconds = min(hours * 3600, 86400)  # Max 24 hours
        room_data = await get_recent_room_sensor_data(seconds=seconds)
        
        # Filter by device_id if specified
        if device_id:
            room_data = [r for r in room_data if r.get("device_id") == device_id]
        
        # Also try to get more data from get_sensor_readings if needed
        if len(room_data) < 10:
            from database.sqlite_db import get_sensor_readings
            additional_data = await get_sensor_readings(
                device_id=device_id if device_id else None,
                limit=100
            )
            # Merge and deduplicate
            existing_ids = {r.get("id") for r in room_data}
            for item in additional_data:
                if item.get("id") not in existing_ids:
                    # Parse JSON data if needed
                    if isinstance(item.get("data"), str):
                        try:
                            import json
                            item["data"] = json.loads(item["data"])
                        except:
                            pass
                    room_data.append(item)
        
        if not room_data:
            return {
                "status": "insufficient_data",
                "message": "Not enough sensor data available",
                "recommendations": []
            }
        
        # Analyze different aspects
        temp_analysis = self._analyze_temperature(room_data)
        humidity_analysis = self._analyze_humidity(room_data)
        motion_analysis = self._analyze_motion_patterns(room_data)
        air_quality_analysis = self._analyze_air_quality_indicators(room_data)
        fall_risk_analysis = self._analyze_fall_risk_factors(room_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            temp_analysis,
            humidity_analysis,
            motion_analysis,
            air_quality_analysis,
            fall_risk_analysis
        )
        
        # Calculate overall environment score (0-100)
        environment_score = self._calculate_environment_score(
            temp_analysis,
            humidity_analysis,
            motion_analysis,
            air_quality_analysis
        )
        
        return {
            "status": "success",
            "environment_score": environment_score,
            "analysis": {
                "temperature": temp_analysis,
                "humidity": humidity_analysis,
                "motion": motion_analysis,
                "air_quality": air_quality_analysis,
                "fall_risk": fall_risk_analysis
            },
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
            "data_points_analyzed": len(room_data)
        }
    
    def _analyze_temperature(self, room_data: List[Dict]) -> Dict:
        """Analyze temperature patterns"""
        temps = []
        for reading in room_data:
            # Check both possible data structures
            data = reading.get("data", {})
            if isinstance(data, str):
                try:
                    import json
                    data = json.loads(data)
                except:
                    data = {}
            
            # Check for sensors.dht22 structure
            if "sensors" in data and "dht22" in data["sensors"]:
                temp = data["sensors"]["dht22"].get("temperature_c")
                if temp is not None:
                    temps.append(temp)
            # Check for direct temperature field
            elif "temperature" in data:
                temp = data.get("temperature")
                if temp is not None:
                    temps.append(temp)
            elif "temperature_c" in data:
                temp = data.get("temperature_c")
                if temp is not None:
                    temps.append(temp)
        
        if not temps:
            return {"status": "no_data", "current": None, "average": None}
        
        current_temp = temps[0] if temps else None
        avg_temp = sum(temps) / len(temps) if temps else None
        min_temp = min(temps) if temps else None
        max_temp = max(temps) if temps else None
        
        # Determine status
        if current_temp is None:
            status = "no_data"
        elif current_temp < self.TEMP_RISK_LOW:
            status = "too_cold"
        elif current_temp > self.TEMP_RISK_HIGH:
            status = "too_hot"
        elif self.OPTIMAL_TEMP_MIN <= current_temp <= self.OPTIMAL_TEMP_MAX:
            status = "optimal"
        elif current_temp < self.OPTIMAL_TEMP_MIN:
            status = "slightly_cold"
        else:
            status = "slightly_warm"
        
        return {
            "status": status,
            "current": round(current_temp, 1) if current_temp else None,
            "average": round(avg_temp, 1) if avg_temp else None,
            "min": round(min_temp, 1) if min_temp else None,
            "max": round(max_temp, 1) if max_temp else None,
            "optimal_range": [self.OPTIMAL_TEMP_MIN, self.OPTIMAL_TEMP_MAX]
        }
    
    def _analyze_humidity(self, room_data: List[Dict]) -> Dict:
        """Analyze humidity patterns"""
        humidities = []
        for reading in room_data:
            # Check both possible data structures
            data = reading.get("data", {})
            if isinstance(data, str):
                try:
                    import json
                    data = json.loads(data)
                except:
                    data = {}
            
            # Check for sensors.dht22 structure
            if "sensors" in data and "dht22" in data["sensors"]:
                humidity = data["sensors"]["dht22"].get("humidity_percent")
                if humidity is not None:
                    humidities.append(humidity)
            # Check for direct humidity field
            elif "humidity" in data:
                humidity = data.get("humidity")
                if humidity is not None:
                    humidities.append(humidity)
            elif "humidity_percent" in data:
                humidity = data.get("humidity_percent")
                if humidity is not None:
                    humidities.append(humidity)
        
        if not humidities:
            return {"status": "no_data", "current": None, "average": None}
        
        current_humidity = humidities[0] if humidities else None
        avg_humidity = sum(humidities) / len(humidities) if humidities else None
        min_humidity = min(humidities) if humidities else None
        max_humidity = max(humidities) if humidities else None
        
        # Determine status
        if current_humidity is None:
            status = "no_data"
        elif current_humidity < self.HUMIDITY_RISK_LOW:
            status = "too_dry"
        elif current_humidity > self.HUMIDITY_RISK_HIGH:
            status = "too_humid"
        elif self.OPTIMAL_HUMIDITY_MIN <= current_humidity <= self.OPTIMAL_HUMIDITY_MAX:
            status = "optimal"
        elif current_humidity < self.OPTIMAL_HUMIDITY_MIN:
            status = "slightly_dry"
        else:
            status = "slightly_humid"
        
        return {
            "status": status,
            "current": round(current_humidity, 1) if current_humidity else None,
            "average": round(avg_humidity, 1) if avg_humidity else None,
            "min": round(min_humidity, 1) if min_humidity else None,
            "max": round(max_humidity, 1) if max_humidity else None,
            "optimal_range": [self.OPTIMAL_HUMIDITY_MIN, self.OPTIMAL_HUMIDITY_MAX]
        }
    
    def _analyze_motion_patterns(self, room_data: List[Dict]) -> Dict:
        """Analyze motion patterns to understand room usage"""
        motion_detections = []
        for reading in room_data:
            # Check both possible data structures
            data = reading.get("data", {})
            if isinstance(data, str):
                try:
                    import json
                    data = json.loads(data)
                except:
                    data = {}
            
            # Check for sensors.pir structure
            if "sensors" in data and "pir" in data["sensors"]:
                motion = data["sensors"]["pir"].get("motion_detected", False)
                motion_detections.append(1 if motion else 0)
            # Check for direct motion field
            elif "motion" in data or "motion_detected" in data:
                motion = data.get("motion_detected", data.get("motion", False))
                motion_detections.append(1 if motion else 0)
        
        if not motion_detections:
            return {"status": "no_data", "activity_level": None}
        
        activity_ratio = sum(motion_detections) / len(motion_detections)
        
        # Determine activity level
        if activity_ratio < self.LOW_ACTIVITY_THRESHOLD:
            activity_level = "low"
        elif activity_ratio > self.HIGH_ACTIVITY_THRESHOLD:
            activity_level = "high"
        else:
            activity_level = "moderate"
        
        return {
            "status": "success",
            "activity_level": activity_level,
            "activity_ratio": round(activity_ratio, 2),
            "motion_detections": len([m for m in motion_detections if m == 1]),
            "total_readings": len(motion_detections)
        }
    
    def _analyze_air_quality_indicators(self, room_data: List[Dict]) -> Dict:
        """Analyze air quality indicators from temperature/humidity patterns"""
        if len(room_data) < 2:
            return {"status": "insufficient_data"}
        
        # Check for stale air (little variation in temp/humidity)
        temp_variations = []
        humidity_variations = []
        
        for i in range(1, min(10, len(room_data))):
            prev = room_data[i]
            curr = room_data[i-1]
            
            # Parse data if needed
            prev_data = prev.get("data", {})
            if isinstance(prev_data, str):
                try:
                    import json
                    prev_data = json.loads(prev_data)
                except:
                    prev_data = {}
            
            curr_data = curr.get("data", {})
            if isinstance(curr_data, str):
                try:
                    import json
                    curr_data = json.loads(curr_data)
                except:
                    curr_data = {}
            
            # Extract temperature and humidity
            if "sensors" in prev_data and "dht22" in prev_data["sensors"]:
                prev_temp = prev_data["sensors"]["dht22"].get("temperature_c")
                prev_hum = prev_data["sensors"]["dht22"].get("humidity_percent")
            else:
                prev_temp = prev_data.get("temperature") or prev_data.get("temperature_c")
                prev_hum = prev_data.get("humidity") or prev_data.get("humidity_percent")
            
            if "sensors" in curr_data and "dht22" in curr_data["sensors"]:
                curr_temp = curr_data["sensors"]["dht22"].get("temperature_c")
                curr_hum = curr_data["sensors"]["dht22"].get("humidity_percent")
            else:
                curr_temp = curr_data.get("temperature") or curr_data.get("temperature_c")
                curr_hum = curr_data.get("humidity") or curr_data.get("humidity_percent")
                    
                    if prev_temp and curr_temp:
                        temp_variations.append(abs(curr_temp - prev_temp))
                    if prev_hum and curr_hum:
                        humidity_variations.append(abs(curr_hum - prev_hum))
        
        avg_temp_variation = sum(temp_variations) / len(temp_variations) if temp_variations else 0
        avg_humidity_variation = sum(humidity_variations) / len(humidity_variations) if humidity_variations else 0
        
        # Low variation suggests stale air
        stale_air = avg_temp_variation < 0.5 and avg_humidity_variation < 2.0
        
        return {
            "status": "success",
            "stale_air_detected": stale_air,
            "temperature_variation": round(avg_temp_variation, 2),
            "humidity_variation": round(avg_humidity_variation, 2)
        }
    
    def _analyze_fall_risk_factors(self, room_data: List[Dict]) -> Dict:
        """Analyze environmental factors that increase fall risk"""
        risk_factors = []
        risk_score = 0
        
        # Check temperature extremes
        temp_analysis = self._analyze_temperature(room_data)
        if temp_analysis["status"] in ["too_cold", "too_hot"]:
            risk_factors.append("extreme_temperature")
            risk_score += 2
        elif temp_analysis["status"] in ["slightly_cold", "slightly_warm"]:
            risk_score += 1
        
        # Check humidity extremes
        humidity_analysis = self._analyze_humidity(room_data)
        if humidity_analysis["status"] in ["too_dry", "too_humid"]:
            risk_factors.append("extreme_humidity")
            risk_score += 2
        elif humidity_analysis["status"] in ["slightly_dry", "slightly_humid"]:
            risk_score += 1
        
        # Check for poor air circulation
        air_quality = self._analyze_air_quality_indicators(room_data)
        if air_quality.get("stale_air_detected"):
            risk_factors.append("poor_ventilation")
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 4:
            risk_level = "high"
        elif risk_score >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors
        }
    
    def _generate_recommendations(
        self,
        temp_analysis: Dict,
        humidity_analysis: Dict,
        motion_analysis: Dict,
        air_quality_analysis: Dict,
        fall_risk_analysis: Dict
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        priority = 1
        
        # Temperature recommendations
        if temp_analysis["status"] == "too_cold":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "temperature",
                "priority": "high",
                "title": "Room Temperature Too Low",
                "description": f"Current temperature ({temp_analysis['current']}°C) is below optimal range. Cold environments can increase fall risk.",
                "action": "Increase room temperature to 20-24°C using heating system",
                "impact": "Reduces fall risk and improves comfort",
                "icon": "thermostat"
            })
            priority += 1
        elif temp_analysis["status"] == "too_hot":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "temperature",
                "priority": "high",
                "title": "Room Temperature Too High",
                "description": f"Current temperature ({temp_analysis['current']}°C) is above optimal range. High temperatures can cause fatigue.",
                "action": "Reduce room temperature to 20-24°C using air conditioning or ventilation",
                "impact": "Prevents heat-related fatigue and improves alertness",
                "icon": "ac_unit"
            })
            priority += 1
        elif temp_analysis["status"] == "slightly_cold":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "temperature",
                "priority": "medium",
                "title": "Room Temperature Slightly Low",
                "description": f"Temperature ({temp_analysis['current']}°C) is below optimal range (20-24°C).",
                "action": "Consider increasing temperature slightly for better comfort",
                "impact": "Improves comfort and reduces cold-related stiffness",
                "icon": "thermostat"
            })
            priority += 1
        
        # Humidity recommendations
        if humidity_analysis["status"] == "too_dry":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "humidity",
                "priority": "high",
                "title": "Low Humidity Detected",
                "description": f"Humidity ({humidity_analysis['current']}%) is below optimal range. Dry air can cause discomfort and increase fall risk.",
                "action": "Use a humidifier to increase humidity to 40-60%",
                "impact": "Improves comfort and reduces respiratory issues",
                "icon": "water_drop"
            })
            priority += 1
        elif humidity_analysis["status"] == "too_humid":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "humidity",
                "priority": "high",
                "title": "High Humidity Detected",
                "description": f"Humidity ({humidity_analysis['current']}%) is above optimal range. High humidity can cause slippery surfaces.",
                "action": "Use dehumidifier or improve ventilation to reduce humidity to 40-60%",
                "impact": "Prevents slippery surfaces and mold growth",
                "icon": "dehumidify"
            })
            priority += 1
        elif humidity_analysis["status"] == "slightly_dry":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "humidity",
                "priority": "medium",
                "title": "Humidity Slightly Low",
                "description": f"Humidity ({humidity_analysis['current']}%) is below optimal range (40-60%).",
                "action": "Consider using a small humidifier or placing water containers",
                "impact": "Improves air quality and comfort",
                "icon": "water_drop"
            })
            priority += 1
        
        # Air quality recommendations
        if air_quality_analysis.get("stale_air_detected"):
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "air_quality",
                "priority": "medium",
                "title": "Poor Air Circulation Detected",
                "description": "Little variation in temperature/humidity suggests stale air.",
                "action": "Open windows or use ventilation system to improve air circulation",
                "impact": "Improves air quality and reduces risk of respiratory issues",
                "icon": "air"
            })
            priority += 1
        
        # Motion-based recommendations
        if motion_analysis.get("activity_level") == "low":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "activity",
                "priority": "low",
                "title": "Low Activity Detected",
                "description": "Minimal motion detected in the room. This may indicate extended periods of inactivity.",
                "action": "Encourage regular movement and activity checks",
                "impact": "Helps maintain mobility and reduces fall risk from inactivity",
                "icon": "directions_walk"
            })
            priority += 1
        
        # Fall risk summary recommendation
        if fall_risk_analysis["risk_level"] == "high":
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "fall_prevention",
                "priority": "high",
                "title": "High Fall Risk Environment",
                "description": f"Multiple environmental risk factors detected: {', '.join(fall_risk_analysis['risk_factors'])}",
                "action": "Address temperature, humidity, and ventilation issues immediately",
                "impact": "Significantly reduces fall risk",
                "icon": "warning"
            })
            priority += 1
        
        # Optimal conditions message
        if (temp_analysis["status"] == "optimal" and 
            humidity_analysis["status"] == "optimal" and 
            fall_risk_analysis["risk_level"] == "low"):
            recommendations.append({
                "id": f"rec_{priority}",
                "category": "status",
                "priority": "low",
                "title": "Environment Optimal",
                "description": "Room conditions are within optimal ranges for fall prevention.",
                "action": "Maintain current settings",
                "impact": "Current environment supports safe mobility",
                "icon": "check_circle"
            })
        
        return recommendations
    
    def _calculate_environment_score(
        self,
        temp_analysis: Dict,
        humidity_analysis: Dict,
        motion_analysis: Dict,
        air_quality_analysis: Dict
    ) -> int:
        """Calculate overall environment score (0-100)"""
        score = 100
        
        # Temperature scoring
        if temp_analysis["status"] == "optimal":
            temp_score = 25
        elif temp_analysis["status"] in ["slightly_cold", "slightly_warm"]:
            temp_score = 20
        elif temp_analysis["status"] in ["too_cold", "too_hot"]:
            temp_score = 10
        else:
            temp_score = 0
        
        # Humidity scoring
        if humidity_analysis["status"] == "optimal":
            humidity_score = 25
        elif humidity_analysis["status"] in ["slightly_dry", "slightly_humid"]:
            humidity_score = 20
        elif humidity_analysis["status"] in ["too_dry", "too_humid"]:
            humidity_score = 10
        else:
            humidity_score = 0
        
        # Air quality scoring
        if not air_quality_analysis.get("stale_air_detected"):
            air_score = 25
        else:
            air_score = 15
        
        # Motion/activity scoring (less critical, but contributes)
        if motion_analysis.get("activity_level") in ["moderate", "high"]:
            activity_score = 25
        elif motion_analysis.get("activity_level") == "low":
            activity_score = 15
        else:
            activity_score = 0
        
        total_score = temp_score + humidity_score + air_score + activity_score
        return min(100, max(0, total_score))

