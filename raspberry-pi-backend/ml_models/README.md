# ML Models for Alert Generation

This directory contains machine learning models for intelligent alert generation based on sensor data patterns.

## Overview

The ML-based alert system uses trained models to detect anomalies and predict alerts that may not be caught by simple rule-based thresholds. ML models can identify complex patterns and trends in sensor data.

## Models

### 1. Temperature Anomaly Detection (`temperature_anomaly.pkl`)
- **Purpose**: Detects unusual temperature patterns that may indicate problems
- **Features**: Temperature, humidity, mean, std deviation, trends
- **Output**: Binary classification (normal/anomaly)

### 2. Fire Risk Detection (`fire_risk_model.pkl`)
- **Purpose**: Predicts fire risk based on temperature and humidity patterns
- **Features**: Temperature, humidity, rate of change
- **Output**: Binary classification (no risk/fire risk)

### 3. Motion Anomaly Detection (`motion_anomaly.pkl`)
- **Purpose**: Detects unusual motion patterns
- **Features**: Motion state, distance, motion count, average distance
- **Output**: Binary classification (normal/anomaly)

## Training Models

To train the ML models:

```bash
cd raspberry-pi-backend/ml_models
python train_alert_models.py
```

This will:
1. Generate synthetic training data
2. Train Random Forest classifiers for each model type
3. Save models to `ml_models/models/` directory
4. Save feature scalers for preprocessing
5. Save metadata files

## Model Files Structure

```
ml_models/
├── models/
│   ├── temperature_anomaly.pkl
│   ├── temperature_anomaly_scaler.pkl
│   ├── temperature_anomaly.pkl.metadata.json
│   ├── fire_risk_model.pkl
│   ├── fire_risk_model_scaler.pkl
│   ├── fire_risk_model.pkl.metadata.json
│   ├── motion_anomaly.pkl
│   ├── motion_anomaly_scaler.pkl
│   └── motion_anomaly.pkl.metadata.json
├── model_loader.py
├── ml_alert_predictor.py
└── train_alert_models.py
```

## Integration

The ML models are automatically integrated into the `AlertEngine`:

1. **Model Loading**: Models are loaded on startup if available
2. **Prediction**: ML predictions run alongside rule-based checks
3. **Fallback**: If ML models are unavailable, system falls back to rule-based alerts
4. **Combined Alerts**: Both ML and rule-based alerts are generated and stored

## Usage

The alert system automatically uses ML models when:
- Models are present in `ml_models/models/` directory
- `AlertEngine` is initialized with `use_ml=True` (default)

ML predictions are indicated in alerts with:
- `"ml_based": true` in alert data
- ML confidence scores in `sensor_values`
- Messages prefixed with "🤖 ML DETECTED"

## Training with Real Data

For production use, replace synthetic data generation with real sensor data:

1. Collect historical sensor readings from your database
2. Label data (normal vs. anomaly)
3. Modify `train_alert_models.py` to load real data
4. Retrain models with your data
5. Evaluate model performance
6. Deploy updated models

## Model Performance

Models are evaluated using:
- Classification report (precision, recall, F1-score)
- Confusion matrix
- Feature importance (for Random Forest)

## Dependencies

Required packages (already in `requirements.txt`):
- `scikit-learn>=1.3.0`
- `numpy>=1.26.4`
- `pandas>=2.0.0`
- `joblib` (included with scikit-learn)

Optional:
- `tensorflow` (for TensorFlow models, not currently used)

## Notes

- Models use scikit-learn Random Forest classifiers
- Feature scaling is applied using StandardScaler
- Models are saved using joblib
- Metadata files contain model information and feature names
- System gracefully handles missing models (falls back to rule-based)

## Troubleshooting

### Models Not Loading
- Check that models are in `ml_models/models/` directory
- Verify model files are not corrupted
- Check file permissions

### Low Prediction Accuracy
- Retrain models with more/better data
- Adjust model hyperparameters
- Check feature engineering

### Performance Issues
- Models are loaded once on startup
- Predictions are fast (Random Forest is efficient)
- Consider model optimization if needed

