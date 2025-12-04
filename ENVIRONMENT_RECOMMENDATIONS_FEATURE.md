# Environment Recommendations Feature

## Overview

Added ML-based environment analysis and recommendations system that analyzes sensor data and provides actionable suggestions to optimize room conditions for fall prevention and comfort.

## Components Added

### 1. Backend ML Service
**File**: `raspberry-pi-backend/ml_models/environment_advisor.py`

- **EnvironmentAdvisor Class**: Analyzes sensor data and generates recommendations
- **Features**:
  - Temperature analysis (optimal: 20-24°C)
  - Humidity analysis (optimal: 40-60%)
  - Motion pattern analysis (activity levels)
  - Air quality indicators (stale air detection)
  - Fall risk factor analysis
  - Environment score calculation (0-100)

### 2. API Endpoint
**File**: `raspberry-pi-backend/api/main.py`

- **Endpoint**: `GET /api/environment/recommendations`
- **Parameters**:
  - `device_id` (optional): Filter by specific device
  - `hours` (default: 24): Hours of data to analyze
- **Returns**: JSON with analysis results and recommendations

### 3. React Dashboard Component
**File**: `web-dashboard/react-app/src/components/EnvironmentRecommendations.js`

- **Features**:
  - Environment score display (0-100) with color coding
  - Current conditions summary (temperature, humidity, activity, fall risk)
  - Expandable recommendation cards with:
    - Priority levels (high/medium/low)
    - Category icons
    - Actionable recommendations
    - Expected impact
  - Auto-refresh every 5 minutes

### 4. Dashboard Integration
**File**: `web-dashboard/react-app/src/components/Dashboard.js`

- Added EnvironmentRecommendations component to main dashboard
- Displays below charts, above recent events

## How It Works

1. **Data Collection**: Analyzes last 24 hours of sensor data from ESP8266 nodes
2. **Analysis**: 
   - Temperature patterns and deviations from optimal range
   - Humidity patterns and deviations
   - Motion activity levels
   - Air circulation indicators
   - Fall risk factors
3. **Scoring**: Calculates overall environment score (0-100)
4. **Recommendations**: Generates prioritized, actionable recommendations

## Recommendation Categories

1. **Temperature**:
   - Too cold/hot warnings
   - Slight adjustments needed
   - Optimal conditions confirmation

2. **Humidity**:
   - Too dry/humid warnings
   - Humidifier/dehumidifier suggestions
   - Optimal range confirmation

3. **Air Quality**:
   - Stale air detection
   - Ventilation recommendations

4. **Activity**:
   - Low activity warnings
   - Movement encouragement

5. **Fall Prevention**:
   - High-risk environment alerts
   - Combined risk factor warnings

## Optimal Ranges

- **Temperature**: 20-24°C (68-75°F)
- **Humidity**: 40-60%
- **Activity**: Moderate to high motion detection
- **Air Quality**: Regular temperature/humidity variations

## API Usage

```bash
# Get recommendations for all devices
GET /api/environment/recommendations?hours=24

# Get recommendations for specific device
GET /api/environment/recommendations?device_id=ESP8266_01&hours=24
```

## Response Format

```json
{
  "status": "success",
  "environment_score": 85,
  "analysis": {
    "temperature": {
      "status": "optimal",
      "current": 22.5,
      "average": 22.3,
      "optimal_range": [20.0, 24.0]
    },
    "humidity": {
      "status": "slightly_dry",
      "current": 35.0,
      "average": 36.2,
      "optimal_range": [40.0, 60.0]
    },
    "motion": {
      "activity_level": "moderate",
      "activity_ratio": 0.45
    },
    "fall_risk": {
      "risk_level": "low",
      "risk_score": 1
    }
  },
  "recommendations": [
    {
      "id": "rec_1",
      "category": "humidity",
      "priority": "medium",
      "title": "Humidity Slightly Low",
      "description": "Humidity (35.0%) is below optimal range (40-60%).",
      "action": "Consider using a small humidifier or placing water containers",
      "impact": "Improves air quality and comfort",
      "icon": "water_drop"
    }
  ],
  "timestamp": "2024-01-15T10:30:00",
  "data_points_analyzed": 432
}
```

## Benefits

1. **Proactive Fall Prevention**: Identifies environmental risk factors before falls occur
2. **Comfort Optimization**: Maintains optimal temperature and humidity
3. **Health Benefits**: Prevents respiratory issues from poor air quality
4. **Actionable Insights**: Clear, prioritized recommendations with expected impact
5. **Real-time Monitoring**: Continuous analysis of room conditions

## Future Enhancements

- Machine learning model training on historical data
- Personalized recommendations based on user preferences
- Integration with smart home devices (thermostats, humidifiers)
- Predictive alerts for environmental changes
- Historical trend analysis and reporting

