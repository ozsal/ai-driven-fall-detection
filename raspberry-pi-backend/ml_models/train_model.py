"""
Fall Detection Model Training Script
Trains a machine learning model for fall detection using accelerometer data
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def generate_synthetic_data(n_samples=10000):
    """
    Generate synthetic training data
    In production, use real collected data
    """
    np.random.seed(42)
    
    data = []
    labels = []
    
    # Normal activities (walking, sitting, standing)
    for _ in range(n_samples // 2):
        # Normal movement: moderate acceleration
        x = np.random.normal(0, 500)
        y = np.random.normal(0, 500)
        z = np.random.normal(1000, 200)  # Gravity component
        
        magnitude = np.sqrt(x**2 + y**2 + z**2)
        jerk = np.random.normal(0, 300)  # Rate of change
        
        data.append([x, y, z, magnitude, jerk])
        labels.append(0)  # No fall
    
    # Fall activities
    for _ in range(n_samples // 2):
        # Fall: high impact acceleration
        x = np.random.normal(0, 1500)
        y = np.random.normal(0, 1500)
        z = np.random.normal(-2000, 1000)  # Downward impact
        
        magnitude = np.sqrt(x**2 + y**2 + z**2)
        jerk = np.random.normal(2000, 500)  # High rate of change
        
        data.append([x, y, z, magnitude, jerk])
        labels.append(1)  # Fall
    
    return np.array(data), np.array(labels)

def train_fall_detection_model():
    """Train fall detection model"""
    print("Generating training data...")
    X, y = generate_synthetic_data(n_samples=10000)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Fall samples: {np.sum(y == 1)}")
    print(f"Normal samples: {np.sum(y == 0)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\nTraining Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    print("\n=== Model Evaluation ===")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "fall_detection_model.pkl")
    
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Feature importance
    print("\n=== Feature Importance ===")
    feature_names = ['accel_x', 'accel_y', 'accel_z', 'magnitude', 'jerk']
    importances = model.feature_importances_
    for name, importance in zip(feature_names, importances):
        print(f"{name}: {importance:.4f}")
    
    return model

if __name__ == "__main__":
    print("=== Fall Detection Model Training ===")
    model = train_fall_detection_model()
    print("\nTraining complete!")

