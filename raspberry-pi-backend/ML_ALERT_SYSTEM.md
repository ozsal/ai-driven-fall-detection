# ML-Based Alert System Integration

## Overview

The alert system now supports **machine learning-based alert generation** alongside rule-based alerts. ML models can detect complex patterns and anomalies that simple thresholds might miss.

## Architecture

```
Sensor Data → AlertEngine → [ML Predictor + Rule-Based] → Alerts → Database → Frontend
```

### Components

1. **ModelLoader** (`ml_models/model_loader.py`)
   - Loads trained ML models (scikit-learn, TensorFlow)
   - Manages model metadata
   - Handles model caching

2. **MLAlertPredictor** (`ml_models/ml_alert_predictor.py`)
   - Predicts alerts using trained models
   - Extracts features from sensor data
   - Handles feature scaling
   - Falls back to statistical/rule-based if models unavailable

3. **AlertEngine** (`alerts/alert_engine.py`)
   - Integrates ML predictions with rule-based checks
   - Combines both types of alerts
   - Manages alert severity and types

## Setup

### 1. Train ML Models

```bash
cd raspberry-pi-backend/ml_models
python train_alert_models.py
```

This creates:
- `models/temperature_anomaly.pkl` - Temperature anomaly detection
- `models/fire_risk_model.pkl` - Fire risk prediction
- `models/motion_anomaly.pkl` - Motion pattern anomaly detection
- Feature scalers for each model
- Metadata files

### 2. Verify Models

Models should be in: `raspberry-pi-backend/ml_models/models/`

```bash
ls -la raspberry-pi-backend/ml_models/models/
```

### 3. Start Backend

The `AlertEngine` automatically:
- Detects available ML models on startup
- Loads models into memory
- Uses ML predictions alongside rule-based alerts

```bash
cd raspberry-pi-backend
python api/main.py
```

Look for: `✓ ML Alert Predictor initialized with X models`

## How It Works

### ML Prediction Flow

1. **Sensor Reading Received**
   - MQTT message arrives with sensor data
   - Data stored in database

2. **Alert Evaluation**
   - `AlertEngine.evaluate_sensor_reading()` called
   - ML predictor extracts features from current + recent readings
   - ML models predict anomalies/risks
   - Rule-based checks also run

3. **Alert Generation**
   - ML alerts marked with `"ml_based": true`
   - Includes ML confidence scores
   - Combined with rule-based alerts
   - All alerts stored in database

4. **Frontend Display**
   - Alerts retrieved via `/api/alerts` endpoints
   - ML-based alerts shown with ML indicators
   - Real-time updates via WebSocket

### ML vs Rule-Based

**ML-Based Alerts:**
- Detect complex patterns
- Learn from historical data
- Can identify subtle anomalies
- Include confidence scores
- Marked with `"ml_based": true`

**Rule-Based Alerts:**
- Simple threshold checks
- Fast and reliable
- Easy to understand
- Always available (no model dependency)
- Marked with `"ml_based": false` or absent

**Both are used together** - ML predictions complement rule-based checks.

## Alert Types with ML Support

### 1. Temperature Anomaly
- **Model**: `temperature_anomaly.pkl`
- **Features**: Temperature, humidity, trends, statistics
- **Detects**: Unusual temperature patterns
- **Severity**: Based on ML confidence + temperature value

### 2. Fire Risk
- **Model**: `fire_risk_model.pkl`
- **Features**: Temperature, humidity, rate of change
- **Detects**: Fire risk conditions
- **Severity**: EXTREME (high confidence) or HIGH (medium confidence)

### 3. Motion Anomaly
- **Model**: `motion_anomaly.pkl`
- **Features**: Motion state, distance, patterns
- **Detects**: Unusual motion patterns
- **Severity**: MEDIUM (based on confidence)

## API Response Format

ML-based alerts include additional fields:

```json
{
  "id": 123,
  "device_id": "ESP8266_NODE_01",
  "alert_type": "unsafe_temperature",
  "severity": "high",
  "message": "🤖 ML DETECTED: Temperature anomaly detected (35.2°C, confidence: 87.3%)",
  "sensor_values": {
    "temperature_c": 35.2,
    "humidity_percent": 45.0,
    "ml_confidence": 0.873,
    "ml_prediction": 1
  },
  "triggered_at": "2024-01-15T10:30:00",
  "ml_based": true
}
```

## Training with Real Data

For production, train models with your actual sensor data:

1. **Collect Data**
   ```python
   # Query historical sensor readings
   readings = await get_sensor_readings(
       sensor_type="dht22",
       limit=10000,
       start_date="2024-01-01"
   )
   ```

2. **Label Data**
   - Mark normal vs. anomaly readings
   - Use historical alerts as labels
   - Manual labeling for critical cases

3. **Train Models**
   - Modify `train_alert_models.py`
   - Replace synthetic data with real data
   - Adjust features as needed
   - Retrain and evaluate

4. **Deploy**
   - Save models to `ml_models/models/`
   - Restart backend
   - Monitor performance

## Configuration

### Enable/Disable ML

In `alerts/alert_engine.py`:

```python
# Enable ML (default)
alert_engine = AlertEngine(use_ml=True)

# Disable ML (rule-based only)
alert_engine = AlertEngine(use_ml=False)
```

### Model Directory

Default: `raspberry-pi-backend/ml_models/models/`

Can be changed in `MLAlertPredictor` initialization.

## Monitoring

### Check ML Model Status

Look for these log messages on startup:
- `✓ ML Alert Predictor initialized with X models` - Models loaded
- `⚠️ Failed to initialize ML Alert Predictor` - Models unavailable (falls back to rule-based)

### Alert Statistics

Check alert types via API:
```bash
GET /api/alerts/stats/summary
```

Count ML-based alerts:
```sql
SELECT COUNT(*) FROM alerts 
WHERE json_extract(sensor_values, '$.ml_based') = 1;
```

## Troubleshooting

### Models Not Loading

1. **Check model files exist**
   ```bash
   ls -la raspberry-pi-backend/ml_models/models/*.pkl
   ```

2. **Check file permissions**
   ```bash
   chmod 644 raspberry-pi-backend/ml_models/models/*.pkl
   ```

3. **Verify model format**
   - Models should be joblib/pickle files
   - Check for corruption

### Low ML Prediction Accuracy

1. **Retrain with more data**
   - Collect more historical readings
   - Include diverse scenarios

2. **Adjust features**
   - Add/remove features in `_extract_*_features()`
   - Retrain models

3. **Tune hyperparameters**
   - Adjust Random Forest parameters
   - Try different algorithms

### Performance Issues

- Models are loaded once on startup (fast)
- Predictions are efficient (Random Forest)
- Feature extraction is lightweight
- If slow, consider model optimization

## Best Practices

1. **Start with Rule-Based**
   - Ensure rule-based alerts work first
   - ML is enhancement, not replacement

2. **Train with Real Data**
   - Synthetic data is for testing
   - Production needs real sensor data

3. **Monitor Both Types**
   - Track ML vs. rule-based alerts
   - Compare detection rates

4. **Regular Retraining**
   - Retrain models periodically
   - Adapt to changing patterns

5. **Fallback Strategy**
   - System works without ML models
   - Rule-based always available

## Example: Training with Database Data

```python
import asyncio
from database.sqlite_db import get_sensor_readings
from ml_models.train_alert_models import train_temperature_anomaly_model

async def train_with_real_data():
    # Get historical readings
    readings = await get_sensor_readings(
        sensor_type="dht22",
        limit=10000
    )
    
    # Extract features and labels
    # (label based on whether alerts were generated)
    
    # Train model
    train_temperature_anomaly_model()
```

## Next Steps

1. ✅ ML models integrated into alert system
2. ✅ Automatic model loading on startup
3. ✅ ML predictions combined with rule-based
4. 🔄 Train models with real sensor data
5. 🔄 Monitor ML prediction performance
6. 🔄 Fine-tune models based on results

## Support

- ML models: `raspberry-pi-backend/ml_models/`
- Alert engine: `raspberry-pi-backend/alerts/alert_engine.py`
- API endpoints: `raspberry-pi-backend/api/alerts.py`
- Documentation: `raspberry-pi-backend/ml_models/README.md`

