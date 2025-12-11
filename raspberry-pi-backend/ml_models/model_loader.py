"""
ML Model Loader
Loads and manages trained ML models for alert generation
Supports scikit-learn (joblib/pickle) and TensorFlow models
"""

import os
import joblib
import numpy as np
from typing import Optional, Dict, Any, List
import json
from pathlib import Path

# Optional TensorFlow import (may not be available on all systems)
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None

class ModelLoader:
    """Loads and manages ML models for alert prediction"""
    
    def __init__(self, models_dir: str = "ml_models/models"):
        """
        Initialize model loader
        
        Args:
            models_dir: Directory containing trained models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict] = {}
        
    def load_model(self, model_name: str, model_type: str = "auto") -> Optional[Any]:
        """
        Load a trained ML model
        
        Args:
            model_name: Name of the model file (e.g., "temperature_anomaly.pkl")
            model_type: Type of model ("sklearn", "tensorflow", "auto")
            
        Returns:
            Loaded model object or None if loading fails
        """
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        model_path = self.models_dir / model_name
        
        if not model_path.exists():
            print(f"⚠️ Model file not found: {model_path}")
            return None
        
        try:
            # Auto-detect model type from extension
            if model_type == "auto":
                if model_name.endswith(('.pkl', '.joblib')):
                    model_type = "sklearn"
                elif model_name.endswith(('.h5', '.pb', '.savedmodel')):
                    model_type = "tensorflow"
                else:
                    # Try sklearn first (most common)
                    model_type = "sklearn"
            
            # Load model based on type
            if model_type == "sklearn":
                model = joblib.load(model_path)
                print(f"✓ Loaded sklearn model: {model_name}")
            elif model_type == "tensorflow" and TENSORFLOW_AVAILABLE:
                if model_name.endswith('.h5'):
                    model = tf.keras.models.load_model(str(model_path))
                else:
                    model = tf.saved_model.load(str(model_path))
                print(f"✓ Loaded TensorFlow model: {model_name}")
            else:
                print(f"⚠️ Unsupported model type or TensorFlow not available: {model_type}")
                return None
            
            # Load metadata if available
            metadata_path = self.models_dir / f"{model_name}.metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.model_metadata[model_name] = json.load(f)
            
            self.loaded_models[model_name] = model
            return model
            
        except Exception as e:
            print(f"❌ Error loading model {model_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a loaded model (loads if not already loaded)"""
        if model_name not in self.loaded_models:
            return self.load_model(model_name)
        return self.loaded_models[model_name]
    
    def get_model_metadata(self, model_name: str) -> Optional[Dict]:
        """Get metadata for a model"""
        return self.model_metadata.get(model_name)
    
    def list_available_models(self) -> List[str]:
        """List all available model files"""
        models = []
        if self.models_dir.exists():
            for file in self.models_dir.iterdir():
                if file.suffix in ['.pkl', '.joblib', '.h5', '.pb']:
                    models.append(file.name)
        return models
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is currently loaded"""
        return model_name in self.loaded_models


