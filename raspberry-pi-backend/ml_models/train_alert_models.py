"""
Train ML Models for Alert Generation
Trains models for temperature anomaly, fire risk, and motion anomaly detection
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import json
from pathlib import Path

def generate_temperature_anomaly_data(n_samples=5000):
    """Generate synthetic temperature anomaly data"""
    np.random.seed(42)
    
    data = []
    labels = []
    
    # Normal temperature readings
    for _ in range(n_samples // 2):
        temp = np.random.normal(22.0, 3.0)  # Normal: 19-25°C
        humidity = np.random.normal(45.0, 10.0)  # Normal: 35-55%
        temp_mean = np.random.normal(22.0, 2.0)
        temp_std = np.random.uniform(0.5, 2.0)
        temp_trend = np.random.normal(0, 0.5)
        hum_mean = np.random.normal(45.0, 8.0)
        hum_std = np.random.uniform(2.0, 8.0)
        
        data.append([temp, humidity, temp_mean, temp_std, temp_trend, hum_mean, hum_std])
        labels.append(0)  # Normal
    
    # Anomalous temperature readings
    for _ in range(n_samples // 2):
        # High temperature anomalies
        if np.random.random() > 0.5:
            temp = np.random.normal(35.0, 5.0)  # High temp
            temp_trend = np.random.normal(3.0, 1.0)  # Rising trend
        else:
            temp = np.random.normal(10.0, 3.0)  # Low temp
            temp_trend = np.random.normal(-2.0, 1.0)  # Falling trend
        
        humidity = np.random.normal(45.0, 15.0)
        temp_mean = np.random.normal(22.0, 2.0)
        temp_std = np.random.uniform(2.0, 5.0)  # Higher variance
        hum_mean = np.random.normal(45.0, 10.0)
        hum_std = np.random.uniform(5.0, 15.0)
        
        data.append([temp, humidity, temp_mean, temp_std, temp_trend, hum_mean, hum_std])
        labels.append(1)  # Anomaly
    
    return np.array(data), np.array(labels)

def generate_fire_risk_data(n_samples=3000):
    """Generate synthetic fire risk data"""
    np.random.seed(42)
    
    data = []
    labels = []
    
    # Normal conditions (no fire risk)
    for _ in range(n_samples // 2):
        temp = np.random.normal(22.0, 3.0)
        humidity = np.random.normal(45.0, 10.0)
        temp_rate = np.random.normal(0, 0.2)  # Slow change
        hum_rate = np.random.normal(0, 1.0)
        
        data.append([temp, humidity, temp_rate, hum_rate])
        labels.append(0)  # No fire risk
    
    # Fire risk conditions
    for _ in range(n_samples // 2):
        temp = np.random.normal(38.0, 5.0)  # High temperature
        humidity = np.random.normal(25.0, 10.0)  # Low humidity (fire consumes moisture)
        temp_rate = np.random.normal(2.0, 1.0)  # Rapid temperature increase
        hum_rate = np.random.normal(-3.0, 1.5)  # Rapid humidity decrease
        
        data.append([temp, humidity, temp_rate, hum_rate])
        labels.append(1)  # Fire risk
    
    return np.array(data), np.array(labels)

def generate_motion_anomaly_data(n_samples=4000):
    """Generate synthetic motion anomaly data"""
    np.random.seed(42)
    
    data = []
    labels = []
    
    # Normal motion patterns
    for _ in range(n_samples // 2):
        motion = np.random.choice([0, 1], p=[0.6, 0.4])  # Mostly no motion
        distance = np.random.normal(150.0, 50.0)  # Normal distance
        motion_count = np.random.poisson(2)  # Few motion events
        avg_distance = np.random.normal(150.0, 40.0)
        
        data.append([motion, distance, motion_count, avg_distance])
        labels.append(0)  # Normal
    
    # Anomalous motion patterns
    for _ in range(n_samples // 2):
        # Extended motion or unusual patterns
        motion = np.random.choice([0, 1], p=[0.2, 0.8])  # Mostly motion
        distance = np.random.normal(80.0, 30.0)  # Closer than normal
        motion_count = np.random.poisson(8)  # Many motion events
        avg_distance = np.random.normal(100.0, 35.0)
        
        data.append([motion, distance, motion_count, avg_distance])
        labels.append(1)  # Anomaly
    
    return np.array(data), np.array(labels)

def train_temperature_anomaly_model():
    """Train temperature anomaly detection model"""
    print("\n=== Training Temperature Anomaly Model ===")
    
    X, y = generate_temperature_anomaly_data(n_samples=5000)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Anomaly samples: {np.sum(y == 1)}")
    print(f"Normal samples: {np.sum(y == 0)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("\nTraining Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    
    print("\n=== Model Evaluation ===")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "temperature_anomaly.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save scaler
    scaler_path = model_dir / "temperature_anomaly_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    
    # Save metadata
    metadata = {
        "model_type": "RandomForestClassifier",
        "features": ["temp", "humidity", "temp_mean", "temp_std", "temp_trend", "hum_mean", "hum_std"],
        "scaler_required": True,
        "scaler_path": "temperature_anomaly_scaler.pkl"
    }
    
    metadata_path = model_dir / "temperature_anomaly.pkl.metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return model, scaler

def train_fire_risk_model():
    """Train fire risk detection model"""
    print("\n=== Training Fire Risk Model ===")
    
    X, y = generate_fire_risk_data(n_samples=3000)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Fire risk samples: {np.sum(y == 1)}")
    print(f"Normal samples: {np.sum(y == 0)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("\nTraining Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    
    print("\n=== Model Evaluation ===")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "fire_risk_model.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save scaler
    scaler_path = model_dir / "fire_risk_model_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    
    # Save metadata
    metadata = {
        "model_type": "RandomForestClassifier",
        "features": ["temp", "humidity", "temp_rate", "hum_rate"],
        "scaler_required": True,
        "scaler_path": "fire_risk_model_scaler.pkl"
    }
    
    metadata_path = model_dir / "fire_risk_model.pkl.metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return model, scaler

def train_motion_anomaly_model():
    """Train motion anomaly detection model"""
    print("\n=== Training Motion Anomaly Model ===")
    
    X, y = generate_motion_anomaly_data(n_samples=4000)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Anomaly samples: {np.sum(y == 1)}")
    print(f"Normal samples: {np.sum(y == 0)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("\nTraining Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    
    print("\n=== Model Evaluation ===")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "motion_anomaly.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save scaler
    scaler_path = model_dir / "motion_anomaly_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    
    # Save metadata
    metadata = {
        "model_type": "RandomForestClassifier",
        "features": ["motion", "distance", "motion_count", "avg_distance"],
        "scaler_required": True,
        "scaler_path": "motion_anomaly_scaler.pkl"
    }
    
    metadata_path = model_dir / "motion_anomaly.pkl.metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return model, scaler

if __name__ == "__main__":
    print("=" * 60)
    print("ML Alert Models Training Script")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # Train all models
        train_temperature_anomaly_model()
        train_fire_risk_model()
        train_motion_anomaly_model()
        
        print("\n" + "=" * 60)
        print("✓ All models trained successfully!")
        print("=" * 60)
        print("\nModels saved in: ml_models/models/")
        print("\nTo use these models:")
        print("1. Ensure models are in: raspberry-pi-backend/ml_models/models/")
        print("2. The AlertEngine will automatically load and use them")
        print("3. ML predictions will be combined with rule-based alerts")
        
    except Exception as e:
        print(f"\n❌ Error training models: {e}")
        import traceback
        traceback.print_exc()

