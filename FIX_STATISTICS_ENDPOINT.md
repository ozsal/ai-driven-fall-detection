# Fix for /api/statistics Internal Server Error

## Problem
The `/api/statistics` endpoint was returning an Internal Server Error.

## Root Cause
The database count functions (`count_fall_events`, `count_sensor_readings`, `count_active_devices`) were not consistently setting the `row_factory` to `dict_factory`, which caused issues when accessing the results.

## Fixes Applied

### 1. Added Error Handling to `/api/statistics`
- Wrapped the function in try-except block
- Added detailed error logging with traceback
- Returns proper HTTP 500 error with details

### 2. Fixed Database Count Functions
All three count functions now:
- Set `db.row_factory = dict_factory` for consistent results
- Handle both tuple and dict return types
- Safely extract count values

### 3. Improved `count_fall_events` Function
- Better handling of datetime filters
- Proper string conversion for timestamps
- Handles both dict and tuple results

## Changes Made

### `raspberry-pi-backend/api/main.py`
```python
@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    try:
        total_events = await count_fall_events()
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_events = await count_fall_events({
            "timestamp_gte": seven_days_ago
        })
        total_readings = await count_sensor_readings()
        active_devices = await count_active_devices()
        
        return {
            "total_fall_events": total_events,
            "recent_events_7d": recent_events,
            "total_sensor_readings": total_readings,
            "active_devices": active_devices
        }
    except Exception as e:
        print(f"Error in get_statistics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
```

### `raspberry-pi-backend/database/sqlite_db.py`
All count functions now:
- Set `db.row_factory = dict_factory`
- Handle both tuple and dict results safely

## Testing

After restarting the backend, test the endpoint:

```bash
curl http://localhost:8000/api/statistics
```

Expected response:
```json
{
  "total_fall_events": 0,
  "recent_events_7d": 0,
  "total_sensor_readings": 0,
  "active_devices": 0
}
```

## Next Steps

1. **Restart the backend API** to apply the fixes
2. **Test the endpoint** using curl or browser
3. **Check dashboard** - it should now load statistics correctly

## If Still Getting Errors

1. Check backend logs for detailed error messages
2. Verify database is initialized: Tables should exist
3. Check database file exists: `raspberry-pi-backend/fall_detection.db`
4. Verify database permissions

The endpoint should now work correctly!

