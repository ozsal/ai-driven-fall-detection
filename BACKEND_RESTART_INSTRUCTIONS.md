# Backend Restart Instructions

## Current Status
The backend code has been fixed, but the **backend server on the Raspberry Pi needs to be restarted** to apply the changes.

## What Was Fixed

1. **Count Functions**: Fixed to use `row["count"]` instead of `row[0]`
2. **Error Handling**: Added comprehensive error handling to all database functions
3. **Database Initialization**: All functions now check if database exists and initialize if needed

## How to Restart the Backend

### Option 1: If running in terminal (recommended)
```bash
# On Raspberry Pi, find the running backend process
# Press Ctrl+C in the terminal where backend is running
# Then restart:
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python api/main.py
```

### Option 2: If running as a service
```bash
# Stop the service
sudo systemctl stop fall-detection-backend

# Start the service
sudo systemctl start fall-detection-backend

# Check status
sudo systemctl status fall-detection-backend
```

### Option 3: Kill and restart
```bash
# Find the process
ps aux | grep "python.*main.py"

# Kill it (replace PID with actual process ID)
kill <PID>

# Restart
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python api/main.py
```

## Verify the Fix

After restarting, test the endpoints:

```bash
# Test statistics
curl http://10.162.131.191:8000/api/statistics

# Test devices
curl http://10.162.131.191:8000/api/devices

# Test sensor readings
curl http://10.162.131.191:8000/api/sensor-readings?limit=5

# Test fall events
curl http://10.162.131.191:8000/api/fall-events?limit=5
```

## Expected Results After Restart

All endpoints should return **200 OK** with data (or empty arrays if no data):

- `/api/statistics` → `{"total_fall_events": 0, "recent_events_7d": 0, "total_sensor_readings": X, "active_devices": Y}`
- `/api/devices` → `[]` or array of device objects
- `/api/sensor-readings` → `[]` or array of sensor reading objects
- `/api/fall-events` → `[]` or array of fall event objects

## If Still Getting Errors

1. **Check backend logs** for error messages
2. **Verify database file exists**: `ls -la ~/ai-driven-fall-detection/raspberry-pi-backend/fall_detection.db`
3. **Check database permissions**: The user running the backend needs read/write access
4. **Verify code was updated**: Check that the fixes are in the code on the Raspberry Pi

## Files Modified

- `raspberry-pi-backend/database/sqlite_db.py` - All database functions
- `raspberry-pi-backend/api/main.py` - Parameter fix

Make sure these files are updated on the Raspberry Pi before restarting!



