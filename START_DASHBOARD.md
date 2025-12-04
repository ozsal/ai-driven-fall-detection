# Starting the Dashboard

## Quick Start

### 1. Start Backend API (Terminal 1)

```bash
cd raspberry-pi-backend/api
python main.py
```

Or if using virtual environment:
```bash
cd raspberry-pi-backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd api
python main.py
```

The API will start on http://localhost:8000

### 2. Start Dashboard (Terminal 2)

```bash
cd web-dashboard/react-app
npm install  # First time only
npm start
```

The dashboard will automatically open at http://localhost:3000

## Verify Connection

1. Check backend is running: http://localhost:8000/docs (FastAPI docs)
2. Check dashboard: http://localhost:3000
3. Verify data flow:
   - Dashboard should show statistics
   - Environment recommendations should appear
   - Real-time sensor data updates via WebSocket

## Troubleshooting

- **CORS errors**: Backend CORS is configured to allow all origins
- **Connection refused**: Make sure backend is running on port 8000
- **No data**: Check that ESP8266 sensors are sending data to MQTT broker

