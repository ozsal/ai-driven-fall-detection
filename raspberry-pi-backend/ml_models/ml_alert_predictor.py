"""
ML-Based Alert Predictor
Uses trained ML models to predict alerts from sensor data
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from ml_models.model_loader import ModelLoader

# Use string literals to avoid circular import
# Alert types and severities are defined in alerts.alert_engine
# but we use string values here to avoid circular dependency

class MLAlertPredictor:
    """Predicts alerts using trained ML models"""
    
    def __init__(self, models_dir: str = "ml_models/models"):
        """
        Initialize ML alert predictor
        
        Args:
            models_dir: Directory containing trained models
        """
        self.model_loader = ModelLoader(models_dir)
        self.models_loaded = False
        
    def load_models(self):
        """Load all available ML models"""
        if self.models_loaded:
            return
        
        # Try to load common models
        model_files = self.model_loader.list_available_models()
        
        for model_file in model_files:
            self.model_loader.load_model(model_file)
        
        self.models_loaded = True
        print(f"✓ ML Alert Predictor initialized with {len(model_files)} models")
    
    def predict_temperature_anomaly(
        self,
        temperature: float,
        humidity: float,
        recent_readings: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Predict temperature anomaly using ML model
        
        Args:
            temperature: Current temperature
            humidity: Current humidity
            recent_readings: Recent sensor readings for context
            
        Returns:
            Alert dictionary if anomaly detected, None otherwise
        """
        # Try to load temperature anomaly model
        model = self.model_loader.get_model("temperature_anomaly.pkl")
        
        if model is None:
            # Fallback: Use statistical anomaly detection
            return self._statistical_temperature_anomaly(
                temperature, humidity, recent_readings
            )
        
        # Extract features for ML model
        features = self._extract_temperature_features(
            temperature, humidity, recent_readings
        )
        
        if features is None:
            return None
        
        try:
            # Load scaler if available
            scaler = self.model_loader.get_model("temperature_anomaly_scaler.pkl")
            if scaler:
                features = scaler.transform(features)
            
            # Predict using ML model
            prediction = model.predict(features)[0]
            probability = None
            
            # Get prediction probability if available
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features)[0]
                probability = float(max(proba))
            
            # If anomaly detected (prediction == 1 or probability > threshold)
            is_anomaly = prediction == 1 or (probability and probability > 0.7)
            
            if is_anomaly:
                severity = self._determine_severity_from_probability(probability, temperature)
                
                return {
                    "alert_type": "unsafe_temperature",
                    "severity": severity,
                    "message": f"🤖 ML DETECTED: Temperature anomaly detected ({temperature:.1f}°C, confidence: {probability*100:.1f}%)",
                    "sensor_values": {
                        "temperature_c": temperature,
                        "humidity_percent": humidity,
                        "ml_confidence": probability,
                        "ml_prediction": int(prediction)
                    },
                    "ml_based": True
                }
        except Exception as e:
            print(f"⚠️ Error in ML temperature prediction: {e}")
            # Fallback to statistical method
            return self._statistical_temperature_anomaly(
                temperature, humidity, recent_readings
            )
        
        return None
    
    def predict_fire_risk(
        self,
        temperature: float,
        humidity: float,
        recent_readings: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Predict fire risk using ML model
        
        Args:
            temperature: Current temperature
            humidity: Current humidity
            recent_readings: Recent sensor readings for trend analysis
            
        Returns:
            Alert dictionary if fire risk detected, None otherwise
        """
        # Try to load fire risk model
        model = self.model_loader.get_model("fire_risk_model.pkl")
        
        if model is None:
            # Fallback: Use rule-based fire risk detection
            return self._rule_based_fire_risk(temperature, humidity, recent_readings)
        
        # Extract features
        features = self._extract_fire_risk_features(
            temperature, humidity, recent_readings
        )
        
        if features is None:
            return None
        
        try:
            # Load scaler if available
            scaler = self.model_loader.get_model("fire_risk_model_scaler.pkl")
            if scaler:
                features = scaler.transform(features)
            
            # Predict fire risk
            prediction = model.predict(features)[0]
            probability = None
            
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features)[0]
                probability = float(max(proba))
            
            # Fire risk detected
            is_fire_risk = prediction == 1 or (probability and probability > 0.6)
            
            if is_fire_risk:
                severity = "extreme" if probability and probability > 0.8 else "high"
                
                return {
                    "alert_type": "fire_risk",
                    "severity": severity,
                    "message": f"🔥 ML DETECTED: Fire risk predicted (temp: {temperature:.1f}°C, confidence: {probability*100:.1f}%)",
                    "sensor_values": {
                        "temperature_c": temperature,
                        "humidity_percent": humidity,
                        "ml_confidence": probability,
                        "ml_prediction": int(prediction)
                    },
                    "ml_based": True
                }
        except Exception as e:
            print(f"⚠️ Error in ML fire risk prediction: {e}")
            return self._rule_based_fire_risk(temperature, humidity, recent_readings)
        
        return None
    
    def predict_motion_anomaly(
        self,
        motion_detected: bool,
        distance: Optional[float],
        recent_readings: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Predict motion anomaly using ML model
        
        Args:
            motion_detected: Current motion state
            distance: Current distance reading
            recent_readings: Recent sensor readings
            
        Returns:
            Alert dictionary if anomaly detected, None otherwise
        """
        # Try to load motion anomaly model
        model = self.model_loader.get_model("motion_anomaly.pkl")
        
        if model is None:
            # No ML model available, return None (rule-based will handle it)
            return None
        
        # Extract features
        features = self._extract_motion_features(
            motion_detected, distance, recent_readings
        )
        
        if features is None:
            return None
        
        try:
            # Load scaler if available
            scaler = self.model_loader.get_model("motion_anomaly_scaler.pkl")
            if scaler:
                features = scaler.transform(features)
            
            prediction = model.predict(features)[0]
            probability = None
            
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features)[0]
                probability = float(max(proba))
            
            is_anomaly = prediction == 1 or (probability and probability > 0.7)
            
            if is_anomaly:
                return {
                    "alert_type": "motion_anomaly",
                    "severity": "medium",
                    "message": f"🤖 ML DETECTED: Unusual motion pattern detected (confidence: {probability*100:.1f}%)",
                    "sensor_values": {
                        "motion_detected": motion_detected,
                        "distance_cm": distance,
                        "ml_confidence": probability,
                        "ml_prediction": int(prediction)
                    },
                    "ml_based": True
                }
        except Exception as e:
            print(f"⚠️ Error in ML motion prediction: {e}")
        
        return None
    
    def _extract_temperature_features(
        self,
        temperature: float,
        humidity: float,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> Optional[np.ndarray]:
        """Extract features for temperature anomaly detection"""
        if recent_readings is None or len(recent_readings) < 2:
            # Minimal features: just current values (will need padding for full feature set)
            # Use default values for missing features
            return np.array([[temperature, humidity, temperature, 1.0, 0.0, humidity, 5.0]])
        
        # Extract temperature and humidity history
        temps = [r.get("data", {}).get("temperature_c") for r in recent_readings[-10:] 
                if r.get("data", {}).get("temperature_c") is not None]
        hums = [r.get("data", {}).get("humidity_percent") for r in recent_readings[-10:]
                if r.get("data", {}).get("humidity_percent") is not None]
        
        if not temps:
            temps = [temperature]
        if not hums:
            hums = [humidity]
        
        # Calculate features
        temp_mean = np.mean(temps)
        temp_std = np.std(temps) if len(temps) > 1 else 1.0
        temp_trend = (temperature - temps[0]) / max(abs(temps[0]), 1) if temps else 0.0
        
        hum_mean = np.mean(hums)
        hum_std = np.std(hums) if len(hums) > 1 else 5.0
        
        # Feature vector: [temp, humidity, temp_mean, temp_std, temp_trend, hum_mean, hum_std]
        features = np.array([[
            temperature,
            humidity,
            temp_mean,
            temp_std,
            temp_trend,
            hum_mean,
            hum_std
        ]])
        
        return features
    
    def _extract_fire_risk_features(
        self,
        temperature: float,
        humidity: float,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> Optional[np.ndarray]:
        """Extract features for fire risk detection"""
        if recent_readings is None or len(recent_readings) < 2:
            return np.array([[temperature, humidity, 0, 0]])  # No trend data
        
        # Get recent temperatures
        temps = [r.get("data", {}).get("temperature_c") for r in recent_readings[-5:]
                if r.get("data", {}).get("temperature_c") is not None]
        hums = [r.get("data", {}).get("humidity_percent") for r in recent_readings[-5:]
                if r.get("data", {}).get("humidity_percent") is not None]
        
        if not temps:
            return np.array([[temperature, humidity, 0, 0]])
        
        # Calculate rate of change
        temp_rate = (temperature - temps[0]) / max(len(temps), 1)
        hum_rate = (humidity - hums[0]) / max(len(hums), 1) if hums else 0
        
        # Feature vector: [temp, humidity, temp_rate, hum_rate]
        return np.array([[temperature, humidity, temp_rate, hum_rate]])
    
    def _extract_motion_features(
        self,
        motion_detected: bool,
        distance: Optional[float],
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> Optional[np.ndarray]:
        """Extract features for motion anomaly detection"""
        motion_binary = 1 if motion_detected else 0
        distance_val = distance if distance is not None else 0
        
        if recent_readings is None or len(recent_readings) < 2:
            return np.array([[motion_binary, distance_val]])
        
        # Count motion events in recent readings
        motion_count = sum(1 for r in recent_readings[-10:]
                          if r.get("data", {}).get("motion_detected", False))
        
        # Average distance
        distances = [r.get("data", {}).get("distance_cm") for r in recent_readings[-10:]
                    if r.get("data", {}).get("distance_cm") is not None]
        avg_distance = np.mean(distances) if distances else distance_val
        
        return np.array([[motion_binary, distance_val, motion_count, avg_distance]])
    
    def _statistical_temperature_anomaly(
        self,
        temperature: float,
        humidity: float,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        """Fallback: Statistical anomaly detection for temperature"""
        if recent_readings is None or len(recent_readings) < 5:
            return None
        
        temps = [r.get("data", {}).get("temperature_c") for r in recent_readings[-20:]
                if r.get("data", {}).get("temperature_c") is not None]
        
        if len(temps) < 5:
            return None
        
        mean_temp = np.mean(temps)
        std_temp = np.std(temps)
        
        # Z-score anomaly detection
        z_score = abs((temperature - mean_temp) / max(std_temp, 0.1))
        
        if z_score > 3.0:  # 3-sigma rule
            severity = "high" if z_score > 4.0 else "medium"
            
            return {
                "alert_type": "unsafe_temperature",
                "severity": severity,
                "message": f"📊 STATISTICAL: Temperature anomaly detected ({temperature:.1f}°C, z-score: {z_score:.2f})",
                "sensor_values": {
                    "temperature_c": temperature,
                    "humidity_percent": humidity,
                    "z_score": z_score,
                    "mean_temperature": mean_temp,
                    "std_temperature": std_temp
                },
                "ml_based": False
            }
        
        return None
    
    def _rule_based_fire_risk(
        self,
        temperature: float,
        humidity: float,
        recent_readings: Optional[List[Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        """Fallback: Rule-based fire risk detection"""
        if temperature > 40.0:
            return {
                "alert_type": "fire_risk",
                "severity": "extreme",
                "message": f"🔥 RULE-BASED: High temperature fire risk ({temperature:.1f}°C)",
                "sensor_values": {
                    "temperature_c": temperature,
                    "humidity_percent": humidity
                },
                "ml_based": False
            }
        return None
    
    def _determine_severity_from_probability(
        self,
        probability: Optional[float],
        temperature: float
    ) -> str:
        """Determine alert severity from ML prediction probability"""
        if probability is None:
            # Fallback to temperature-based severity
            if temperature > 35.0:
                return "extreme"
            elif temperature > 30.0:
                return "high"
            else:
                return "medium"
        
        if probability > 0.9:
            return "extreme"
        elif probability > 0.75:
            return "high"
        elif probability > 0.6:
            return "medium"
        else:
            return "low"

