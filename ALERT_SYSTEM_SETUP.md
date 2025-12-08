# Real-Time Alert System Setup Guide

## 🎯 Overview

A comprehensive real-time alert system that analyzes sensor data and triggers alerts based on AI logic and thresholds. Alerts are automatically generated, stored in the database, and displayed in real-time on the React dashboard.

## 🔥 Alert Types

### 1. Fire Risk Alerts
- **Temperature exceeds 40°C** (Extreme severity)
- **Rapid temperature spike** (+5°C in short time) (High severity)
- **Unexpected humidity drop** with high temperature (Medium severity)

### 2. Unsafe Temperature Alerts
- **Critical**: <10°C or >35°C (Extreme severity)
- **Warning**: <15°C or >30°C (High severity)
- **Alert**: Outside normal range 18-26°C (Medium severity)

### 3. Unsafe Humidity Alerts
- **Critical**: <10% or >80% (Extreme severity)
- **Warning**: <20% or >70% (High severity)
- **Alert**: Outside normal range 30-60% (Medium severity)

### 4. Rapid Fluctuation Alerts
- **Temperature fluctuation** >3°C in 5 minutes (High severity)
- **Humidity fluctuation** >10% in 5 minutes (Medium severity)

### 5. Sensor Failure Alerts
- **Invalid ultrasonic readings** (Medium severity)

## 📊 Database Schema

### alerts Table

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT NOT NULL,
    sensor_values TEXT NOT NULL,  -- JSON
    triggered_at TIMESTAMP NOT NULL,
    acknowledged BOOLEAN DEFAULT 0,
    acknowledged_at TIMESTAMP,
    acknowledged_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Backend Components

### 1. Alert Engine (`alerts/alert_engine.py`)
- Evaluates sensor readings against thresholds
- Detects trends and anomalies
- Returns list of triggered alerts

### 2. Alert Database (`database/alert_db.py`)
- `insert_alert()` - Store alert in database
- `get_alerts()` - Get alerts with filters
- `get_latest_alerts()` - Get latest alerts for dashboard
- `acknowledge_alert()` - Mark alert as acknowledged
- `count_alerts()` - Count alerts by filters

### 3. Alert API (`api/alerts.py`)
- `POST /api/alerts` - Create alert (admin only)
- `GET /api/alerts` - Get alerts with filters
- `GET /api/alerts/latest` - Get latest alerts
- `GET /api/alerts/{id}` - Get specific alert
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
- `GET /api/alerts/stats/summary` - Get alert statistics

### 4. Integration (`api/main.py`)
- Alert evaluation integrated into MQTT message handler
- Alerts automatically triggered when sensor data arrives
- WebSocket broadcasting for real-time updates

## 🚀 Installation

### Backend

1. **Database will auto-create** the `alerts` table on first run

2. **No additional dependencies** - uses existing packages

3. **Restart backend** to activate alert system:
   ```bash
   sudo systemctl restart fall-detection
   # Or manually
   cd ~/ai-driven-fall-detection/raspberry-pi-backend
   source venv/bin/activate
   cd api
   python main.py
   ```

### Frontend

1. **Copy React components** to your dashboard:
   ```bash
   # Components are in:
   web-dashboard/react-app/src/components/
     - AlertBanner.js
     - AlertBanner.css
     - AlertCard.js
     - AlertCard.css
     - AlertsPage.js
     - AlertsPage.css
     - DashboardWithAlerts.js
   
   # Hooks:
   web-dashboard/react-app/src/hooks/
     - useAlerts.js
   
   # Services:
   web-dashboard/react-app/src/services/
     - alertService.js
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   cd web-dashboard/react-app
   npm install
   ```

3. **Integrate into your Dashboard**:
   ```javascript
   import AlertBanner from './components/AlertBanner';
   import useAlerts from './hooks/useAlerts';
   
   function Dashboard() {
     const { alerts, acknowledgeAlert } = useAlerts(apiClient);
     
     return (
       <div>
         <AlertBanner alerts={alerts} onDismiss={acknowledgeAlert} />
         {/* Your existing dashboard content */}
       </div>
     );
   }
   ```

## 📡 API Usage

### Get Latest Alerts

```bash
# Get latest 10 unacknowledged alerts
curl -X GET "http://localhost:8000/api/alerts/latest?limit=10&unacknowledged_only=true" \
  -H "Authorization: Bearer $TOKEN"
```

### Get All Alerts with Filters

```bash
# Filter by severity
curl -X GET "http://localhost:8000/api/alerts?severity=extreme&limit=50" \
  -H "Authorization: Bearer $TOKEN"

# Filter by device
curl -X GET "http://localhost:8000/api/alerts?device_id=ESP8266_NODE_01" \
  -H "Authorization: Bearer $TOKEN"

# Filter by type
curl -X GET "http://localhost:8000/api/alerts?alert_type=fire_risk" \
  -H "Authorization: Bearer $TOKEN"
```

### Acknowledge Alert

```bash
curl -X POST "http://localhost:8000/api/alerts/123/acknowledge" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Alert Statistics

```bash
curl -X GET "http://localhost:8000/api/alerts/stats/summary" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "total": 45,
  "unacknowledged": 12,
  "acknowledged": 33,
  "by_severity": {
    "low": 5,
    "medium": 20,
    "high": 15,
    "extreme": 5
  },
  "by_type": {
    "fire_risk": 3,
    "unsafe_temperature": 25,
    "unsafe_humidity": 12,
    "rapid_fluctuation": 5
  }
}
```

## 🔌 WebSocket Integration

Alerts are automatically broadcast via WebSocket when triggered:

```javascript
// WebSocket message format
{
  "type": "alert",
  "alert": {
    "id": 123,
    "device_id": "ESP8266_NODE_01",
    "alert_type": "fire_risk",
    "message": "🔥 EXTREME FIRE RISK: Temperature reached 42.5°C",
    "severity": "extreme",
    "sensor_values": {
      "temperature_c": 42.5,
      "humidity_percent": 35.0
    },
    "triggered_at": "2024-12-06T18:30:00",
    "acknowledged": false
  }
}
```

### React WebSocket Example

```javascript
useEffect(() => {
  if (!websocket) return;

  const handleMessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'alert') {
      // Handle new alert
      setAlerts(prev => [data.alert, ...prev]);
    }
  };

  websocket.addEventListener('message', handleMessage);
  return () => websocket.removeEventListener('message', handleMessage);
}, [websocket]);
```

## 🎨 React Components

### AlertBanner
- Fixed position at top of page
- Shows up to 3 most critical unacknowledged alerts
- Auto-dismisses when acknowledged
- Color-coded by severity
- Animated icons for critical alerts

### AlertCard
- Individual alert display
- Shows all alert details
- Acknowledge button
- View details button
- Severity badges

### AlertsPage
- Full page listing all alerts
- Filtering by device, type, severity, status
- Statistics summary
- Auto-refresh every 5 seconds

## ⚙️ Configuration

### Alert Thresholds

Edit `alerts/alert_engine.py` to customize thresholds:

```python
# Temperature thresholds
self.temp_normal_min = 18.0
self.temp_normal_max = 26.0
self.temp_fire_risk = 40.0
self.temp_spike_threshold = 5.0

# Humidity thresholds
self.humidity_normal_min = 30.0
self.humidity_normal_max = 60.0
self.humidity_drop_threshold = 15.0

# Fluctuation thresholds
self.temp_fluctuation_threshold = 3.0
self.humidity_fluctuation_threshold = 10.0
```

## 📊 Alert Flow

```
MQTT Message → Store in DB → Evaluate Alerts → Store Alerts → Broadcast WebSocket → React Dashboard
```

1. **Sensor data arrives** via MQTT
2. **Data stored** in `sensor_readings` table
3. **Alert engine evaluates** data against thresholds
4. **Alerts created** and stored in `alerts` table
5. **WebSocket broadcast** to all connected clients
6. **React dashboard** displays alerts in real-time

## 🧪 Testing

### Test Alert Generation

1. **Send test sensor data** that triggers alerts:
   ```bash
   # High temperature (fire risk)
   mosquitto_pub -h localhost -p 1883 -t "sensors/dht22/ESP8266_NODE_01" \
     -m '{"device_id":"ESP8266_NODE_01","temperature_c":42.5,"humidity_percent":35.0,"timestamp":1234567890}'
   
   # Low temperature
   mosquitto_pub -h localhost -p 1883 -t "sensors/dht22/ESP8266_NODE_01" \
     -m '{"device_id":"ESP8266_NODE_01","temperature_c":8.0,"humidity_percent":45.0,"timestamp":1234567890}'
   ```

2. **Check backend logs** for alert generation:
   ```
   🚨 ALERT #1: 🔥 EXTREME FIRE RISK: Temperature reached 42.5°C (Severity: extreme)
   ```

3. **Query alerts API**:
   ```bash
   curl http://localhost:8000/api/alerts/latest?limit=5
   ```

## 📝 Example Alert Data

```json
{
  "id": 1,
  "device_id": "ESP8266_NODE_01",
  "alert_type": "fire_risk",
  "message": "🔥 EXTREME FIRE RISK: Temperature reached 42.5°C (threshold: 40.0°C)",
  "severity": "extreme",
  "sensor_values": {
    "temperature_c": 42.5,
    "humidity_percent": 35.0
  },
  "triggered_at": "2024-12-06T18:30:00",
  "acknowledged": false,
  "acknowledged_at": null,
  "acknowledged_by": null,
  "created_at": "2024-12-06T18:30:00"
}
```

## 🎯 Next Steps

1. **Customize thresholds** in `alert_engine.py` for your environment
2. **Integrate AlertBanner** into your existing Dashboard component
3. **Add AlertsPage** to your navigation/routing
4. **Configure WebSocket** connection in your React app
5. **Test with real sensor data** to verify alert generation

## 🔍 Troubleshooting

### Alerts Not Being Generated

1. **Check backend logs** for alert evaluation errors
2. **Verify sensor data** is being stored correctly
3. **Check thresholds** - data might be within normal range
4. **Verify alert engine** is initialized (check startup logs)

### Alerts Not Appearing in Dashboard

1. **Check API authentication** - alerts endpoint requires auth
2. **Verify WebSocket connection** is established
3. **Check browser console** for errors
4. **Verify polling** is working (check network tab)

### Too Many Alerts

1. **Adjust thresholds** in `alert_engine.py`
2. **Add deduplication logic** (prevent duplicate alerts)
3. **Implement alert cooldown** (don't alert if similar alert recently)

## 📚 Files Created

### Backend
- `alerts/alert_engine.py` - Alert evaluation logic
- `database/alert_db.py` - Alert database functions
- `api/alerts.py` - Alert API endpoints
- `database/sqlite_db.py` - Updated with alerts table

### Frontend
- `components/AlertBanner.js` - Top banner component
- `components/AlertCard.js` - Individual alert card
- `components/AlertsPage.js` - Full alerts page
- `hooks/useAlerts.js` - React hook for alerts
- `services/alertService.js` - Alert API service

All components are production-ready and fully functional!

