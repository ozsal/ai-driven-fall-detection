"""
Alert Evaluation Engine
Analyzes sensor data and triggers alerts based on thresholds and ML logic
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import os

# Import ML predictor (optional - will work without ML models)
try:
    from ml_models.ml_alert_predictor import MLAlertPredictor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    MLAlertPredictor = None

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class AlertType(str, Enum):
    """Alert types"""
    FIRE_RISK = "fire_risk"
    UNSAFE_TEMPERATURE = "unsafe_temperature"
    UNSAFE_HUMIDITY = "unsafe_humidity"
    RAPID_FLUCTUATION = "rapid_fluctuation"
    MOTION_ANOMALY = "motion_anomaly"
    SENSOR_FAILURE = "sensor_failure"

class AlertEngine:
    """Engine for evaluating sensor data and triggering alerts"""
    
    def __init__(self, use_ml: bool = True):
        # Temperature thresholds (Celsius)
        self.temp_normal_min = 18.0
        self.temp_normal_max = 26.0
        self.temp_warning_min = 15.0
        self.temp_warning_max = 30.0
        self.temp_critical_min = 10.0
        self.temp_critical_max = 35.0
        self.temp_fire_risk = 40.0  # Fire risk threshold
        self.temp_spike_threshold = 5.0  # Temperature spike in short time (Celsius)
        
        # Humidity thresholds (Percentage)
        self.humidity_normal_min = 30.0
        self.humidity_normal_max = 60.0
        self.humidity_warning_min = 20.0
        self.humidity_warning_max = 70.0
        self.humidity_critical_min = 10.0
        self.humidity_critical_max = 80.0
        self.humidity_drop_threshold = 15.0  # Rapid humidity drop (indicates fire risk)
        
        # Fluctuation thresholds
        self.temp_fluctuation_threshold = 3.0  # Rapid temp change in 5 minutes
        self.humidity_fluctuation_threshold = 10.0  # Rapid humidity change in 5 minutes
        
        # Time windows for trend analysis
        self.trend_window_minutes = 5
        self.spike_window_minutes = 2
        
        # ML-based alert prediction
        self.use_ml = use_ml and ML_AVAILABLE
        self.ml_predictor = None
        
        if self.use_ml:
            try:
                # Determine models directory path
                models_dir = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "ml_models", "models"
                )
                self.ml_predictor = MLAlertPredictor(models_dir=models_dir)
                self.ml_predictor.load_models()
                print("✓ ML Alert Predictor initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize ML Alert Predictor: {e}")
                self.use_ml = False
                self.ml_predictor = None
        
    def evaluate_sensor_reading(
        self, 
        device_id: str,
        sensor_type: str,
        sensor_data: Dict[str, Any],
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate sensor reading and return list of alerts if any
        
        Args:
            device_id: Device identifier
            sensor_type: Type of sensor (dht22, pir, ultrasonic)
            sensor_data: Sensor reading data
            timestamp: Unix timestamp
            recent_readings: Recent readings for trend analysis
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if sensor_type == "dht22":
            alerts.extend(self._evaluate_dht22(device_id, sensor_data, timestamp, recent_readings))
        elif sensor_type == "pir":
            alerts.extend(self._evaluate_pir(device_id, sensor_data, timestamp, recent_readings))
        elif sensor_type == "ultrasonic":
            alerts.extend(self._evaluate_ultrasonic(device_id, sensor_data, timestamp, recent_readings))
        
        return alerts
    
    def _evaluate_dht22(
        self,
        device_id: str,
        sensor_data: Dict[str, Any],
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Evaluate DHT22 temperature and humidity data"""
        alerts = []
        
        temperature = sensor_data.get("temperature_c")
        humidity = sensor_data.get("humidity_percent")
        
        if temperature is None or humidity is None:
            return alerts
        
        # ML-based predictions (if available)
        if self.use_ml and self.ml_predictor:
            try:
                # ML fire risk prediction
                ml_fire_alert = self.ml_predictor.predict_fire_risk(
                    temperature, humidity, recent_readings
                )
                if ml_fire_alert:
                    ml_fire_alert["device_id"] = device_id
                    ml_fire_alert["triggered_at"] = datetime.utcnow().isoformat()
                    alerts.append(ml_fire_alert)
                
                # ML temperature anomaly prediction
                ml_temp_alert = self.ml_predictor.predict_temperature_anomaly(
                    temperature, humidity, recent_readings
                )
                if ml_temp_alert:
                    ml_temp_alert["device_id"] = device_id
                    ml_temp_alert["triggered_at"] = datetime.utcnow().isoformat()
                    alerts.append(ml_temp_alert)
            except Exception as e:
                print(f"⚠️ ML prediction error: {e}")
                # Continue with rule-based evaluation
        
        # Rule-based checks (always run as fallback/verification)
        # Check for fire risk conditions
        fire_alerts = self._check_fire_risk(device_id, temperature, humidity, timestamp, recent_readings)
        alerts.extend(fire_alerts)
        
        # Check for unsafe temperature
        temp_alerts = self._check_temperature(device_id, temperature, timestamp, recent_readings)
        alerts.extend(temp_alerts)
        
        # Check for unsafe humidity
        humidity_alerts = self._check_humidity(device_id, humidity, timestamp, recent_readings)
        alerts.extend(humidity_alerts)
        
        # Check for rapid fluctuations
        fluctuation_alerts = self._check_fluctuations(device_id, temperature, humidity, timestamp, recent_readings)
        alerts.extend(fluctuation_alerts)
        
        return alerts
    
    def _check_fire_risk(
        self,
        device_id: str,
        temperature: float,
        humidity: float,
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Check for fire risk conditions"""
        alerts = []
        
        # Condition 1: Temperature exceeds fire risk threshold
        if temperature >= self.temp_fire_risk:
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.FIRE_RISK.value,
                "severity": AlertSeverity.EXTREME.value,
                "message": f"🔥 EXTREME FIRE RISK: Temperature reached {temperature:.1f}°C (threshold: {self.temp_fire_risk}°C)",
                "sensor_values": {
                    "temperature_c": temperature,
                    "humidity_percent": humidity
                },
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        # Condition 2: Rapid temperature spike (indicates fire)
        if recent_readings:
            recent_temps = [
                r.get("data", {}).get("temperature_c") 
                for r in recent_readings 
                if r.get("sensor_type") == "dht22" and r.get("data", {}).get("temperature_c") is not None
            ]
            if recent_temps:
                max_recent_temp = max(recent_temps)
                temp_increase = temperature - max_recent_temp
                
                if temp_increase >= self.temp_spike_threshold:
                    alerts.append({
                        "device_id": device_id,
                        "alert_type": AlertType.FIRE_RISK.value,
                        "severity": AlertSeverity.HIGH.value,
                        "message": f"🔥 FIRE RISK: Rapid temperature spike detected (+{temp_increase:.1f}°C in short time)",
                        "sensor_values": {
                            "temperature_c": temperature,
                            "humidity_percent": humidity,
                            "temperature_increase": temp_increase
                        },
                        "triggered_at": datetime.utcnow().isoformat()
                    })
        
        # Condition 3: Unexpected humidity drop (fire consumes moisture)
        if recent_readings:
            recent_humidities = [
                r.get("data", {}).get("humidity_percent")
                for r in recent_readings
                if r.get("sensor_type") == "dht22" and r.get("data", {}).get("humidity_percent") is not None
            ]
            if recent_humidities:
                max_recent_humidity = max(recent_humidities)
                humidity_drop = max_recent_humidity - humidity
                
                if humidity_drop >= self.humidity_drop_threshold and temperature > 25.0:
                    alerts.append({
                        "device_id": device_id,
                        "alert_type": AlertType.FIRE_RISK.value,
                        "severity": AlertSeverity.MEDIUM.value,
                        "message": f"🔥 FIRE RISK: Unexpected humidity drop detected (-{humidity_drop:.1f}% with high temperature)",
                        "sensor_values": {
                            "temperature_c": temperature,
                            "humidity_percent": humidity,
                            "humidity_drop": humidity_drop
                        },
                        "triggered_at": datetime.utcnow().isoformat()
                    })
        
        return alerts
    
    def _check_temperature(
        self,
        device_id: str,
        temperature: float,
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Check for unsafe temperature conditions"""
        alerts = []
        
        # Critical temperature (extreme)
        if temperature <= self.temp_critical_min or temperature >= self.temp_critical_max:
            severity = AlertSeverity.EXTREME.value
            if temperature <= self.temp_critical_min:
                message = f"❄️ EXTREME: Temperature critically low ({temperature:.1f}°C)"
            else:
                message = f"🌡️ EXTREME: Temperature critically high ({temperature:.1f}°C)"
            
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.UNSAFE_TEMPERATURE.value,
                "severity": severity,
                "message": message,
                "sensor_values": {"temperature_c": temperature},
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        # Warning temperature (high)
        elif temperature <= self.temp_warning_min or temperature >= self.temp_warning_max:
            severity = AlertSeverity.HIGH.value
            if temperature <= self.temp_warning_min:
                message = f"❄️ WARNING: Temperature too low ({temperature:.1f}°C, normal: {self.temp_normal_min}-{self.temp_normal_max}°C)"
            else:
                message = f"🌡️ WARNING: Temperature too high ({temperature:.1f}°C, normal: {self.temp_normal_min}-{self.temp_normal_max}°C)"
            
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.UNSAFE_TEMPERATURE.value,
                "severity": severity,
                "message": message,
                "sensor_values": {"temperature_c": temperature},
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        # Outside normal range (medium)
        elif temperature < self.temp_normal_min or temperature > self.temp_normal_max:
            severity = AlertSeverity.MEDIUM.value
            if temperature < self.temp_normal_min:
                message = f"❄️ ALERT: Temperature below normal ({temperature:.1f}°C, normal: {self.temp_normal_min}-{self.temp_normal_max}°C)"
            else:
                message = f"🌡️ ALERT: Temperature above normal ({temperature:.1f}°C, normal: {self.temp_normal_min}-{self.temp_normal_max}°C)"
            
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.UNSAFE_TEMPERATURE.value,
                "severity": severity,
                "message": message,
                "sensor_values": {"temperature_c": temperature},
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _check_humidity(
        self,
        device_id: str,
        humidity: float,
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Check for unsafe humidity conditions"""
        alerts = []
        
        # Critical humidity (extreme)
        if humidity <= self.humidity_critical_min or humidity >= self.humidity_critical_max:
            severity = AlertSeverity.EXTREME.value
            if humidity <= self.humidity_critical_min:
                message = f"💨 EXTREME: Humidity critically low ({humidity:.1f}%, normal: {self.humidity_normal_min}-{self.humidity_normal_max}%)"
            else:
                message = f"💧 EXTREME: Humidity critically high ({humidity:.1f}%, normal: {self.humidity_normal_min}-{self.humidity_normal_max}%)"
            
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.UNSAFE_HUMIDITY.value,
                "severity": severity,
                "message": message,
                "sensor_values": {"humidity_percent": humidity},
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        # Warning humidity (high)
        elif humidity <= self.humidity_warning_min or humidity >= self.humidity_warning_max:
            severity = AlertSeverity.HIGH.value
            if humidity <= self.humidity_warning_min:
                message = f"💨 WARNING: Humidity too low ({humidity:.1f}%, normal: {self.humidity_normal_min}-{self.humidity_normal_max}%)"
            else:
                message = f"💧 WARNING: Humidity too high ({humidity:.1f}%, normal: {self.humidity_normal_min}-{self.humidity_normal_max}%)"
            
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.UNSAFE_HUMIDITY.value,
                "severity": severity,
                "message": message,
                "sensor_values": {"humidity_percent": humidity},
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        # Outside normal range (medium)
        elif humidity < self.humidity_normal_min or humidity > self.humidity_normal_max:
            severity = AlertSeverity.MEDIUM.value
            if humidity < self.humidity_normal_min:
                message = f"💨 ALERT: Humidity below normal ({humidity:.1f}%, normal: {self.humidity_normal_min}-{self.humidity_normal_max}%)"
            else:
                message = f"💧 ALERT: Humidity above normal ({humidity:.1f}%, normal: {self.humidity_normal_min}-{self.humidity_normal_max}%)"
            
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.UNSAFE_HUMIDITY.value,
                "severity": severity,
                "message": message,
                "sensor_values": {"humidity_percent": humidity},
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _check_fluctuations(
        self,
        device_id: str,
        temperature: float,
        humidity: float,
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Check for rapid fluctuations indicating danger"""
        alerts = []
        
        if not recent_readings or len(recent_readings) < 2:
            return alerts
        
        # Get recent DHT22 readings within time window
        window_start = timestamp - (self.trend_window_minutes * 60)
        recent_dht22 = [
            r for r in recent_readings
            if r.get("sensor_type") == "dht22" 
            and r.get("timestamp", 0) >= window_start
            and r.get("data", {}).get("temperature_c") is not None
            and r.get("data", {}).get("humidity_percent") is not None
        ]
        
        if len(recent_dht22) < 2:
            return alerts
        
        # Calculate temperature fluctuation
        temps = [r.get("data", {}).get("temperature_c") for r in recent_dht22]
        temps.append(temperature)
        temp_range = max(temps) - min(temps)
        
        if temp_range >= self.temp_fluctuation_threshold:
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.RAPID_FLUCTUATION.value,
                "severity": AlertSeverity.HIGH.value,
                "message": f"⚠️ RAPID FLUCTUATION: Temperature fluctuated {temp_range:.1f}°C in {self.trend_window_minutes} minutes (range: {min(temps):.1f}°C - {max(temps):.1f}°C)",
                "sensor_values": {
                    "temperature_c": temperature,
                    "humidity_percent": humidity,
                    "temperature_range": temp_range,
                    "min_temperature": min(temps),
                    "max_temperature": max(temps)
                },
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        # Calculate humidity fluctuation
        humidities = [r.get("data", {}).get("humidity_percent") for r in recent_dht22]
        humidities.append(humidity)
        humidity_range = max(humidities) - min(humidities)
        
        if humidity_range >= self.humidity_fluctuation_threshold:
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.RAPID_FLUCTUATION.value,
                "severity": AlertSeverity.MEDIUM.value,
                "message": f"⚠️ RAPID FLUCTUATION: Humidity fluctuated {humidity_range:.1f}% in {self.trend_window_minutes} minutes (range: {min(humidities):.1f}% - {max(humidities):.1f}%)",
                "sensor_values": {
                    "temperature_c": temperature,
                    "humidity_percent": humidity,
                    "humidity_range": humidity_range,
                    "min_humidity": min(humidities),
                    "max_humidity": max(humidities)
                },
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _evaluate_pir(
        self,
        device_id: str,
        sensor_data: Dict[str, Any],
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Evaluate PIR motion sensor data"""
        alerts = []
        
        motion_detected = sensor_data.get("motion_detected", False)
        
        # ML-based motion anomaly detection (if available)
        if self.use_ml and self.ml_predictor:
            try:
                # Get distance from recent readings if available
                distance = None
                if recent_readings:
                    for r in recent_readings:
                        if r.get("sensor_type") == "ultrasonic":
                            distance = r.get("data", {}).get("distance_cm")
                            break
                
                ml_motion_alert = self.ml_predictor.predict_motion_anomaly(
                    motion_detected, distance, recent_readings
                )
                if ml_motion_alert:
                    ml_motion_alert["device_id"] = device_id
                    ml_motion_alert["triggered_at"] = datetime.utcnow().isoformat()
                    alerts.append(ml_motion_alert)
            except Exception as e:
                print(f"⚠️ ML motion prediction error: {e}")
        
        # Rule-based motion anomaly detection
        # Detect extended motion (potential issue)
        if recent_readings and len(recent_readings) >= 5:
            motion_count = sum(1 for r in recent_readings[-10:]
                              if r.get("sensor_type") == "pir" 
                              and r.get("data", {}).get("motion_detected", False))
            
            # If motion detected for extended period, might indicate issue
            if motion_count >= 8 and motion_detected:
                alerts.append({
                    "device_id": device_id,
                    "alert_type": AlertType.MOTION_ANOMALY.value,
                    "severity": AlertSeverity.LOW.value,
                    "message": f"⚠️ Extended motion detected ({motion_count}/10 recent readings)",
                    "sensor_values": {
                        "motion_detected": motion_detected,
                        "motion_count": motion_count
                    },
                    "triggered_at": datetime.utcnow().isoformat()
                })
        
        return alerts
    
    def _evaluate_ultrasonic(
        self,
        device_id: str,
        sensor_data: Dict[str, Any],
        timestamp: int,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Evaluate ultrasonic distance sensor data"""
        alerts = []
        
        distance = sensor_data.get("distance_cm")
        
        if distance is None:
            return alerts
        
        # Check for sensor failure (invalid readings)
        if distance < 0 or distance > 400:  # HC-SR04 range is 2-400cm
            alerts.append({
                "device_id": device_id,
                "alert_type": AlertType.SENSOR_FAILURE.value,
                "severity": AlertSeverity.MEDIUM.value,
                "message": f"⚠️ SENSOR FAILURE: Ultrasonic sensor reading invalid ({distance:.1f}cm, expected: 2-400cm)",
                "sensor_values": {"distance_cm": distance},
                "triggered_at": datetime.utcnow().isoformat()
            })
        
        # Optional: Add distance-based alerts (e.g., object too close, sudden changes)
        
        return alerts


