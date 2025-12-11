"""
Alert API endpoints
"""

import sys
import os
# Add parent directory to path so imports work when running as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from auth.dependencies import require_viewer_or_above, require_admin
from database.alert_db import (
    get_alerts, get_latest_alerts, get_alert_by_id,
    acknowledge_alert, count_alerts, insert_alert
)
from alerts.alert_engine import AlertType, AlertSeverity
from pydantic import BaseModel

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

class AlertCreate(BaseModel):
    """Model for creating an alert"""
    device_id: str
    alert_type: str
    message: str
    severity: str
    sensor_values: dict

class AlertResponse(BaseModel):
    """Alert response model"""
    id: int
    device_id: str
    alert_type: str
    message: str
    severity: str
    sensor_values: dict
    triggered_at: str
    acknowledged: bool
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    created_at: str

@router.post("", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_data: AlertCreate,
    current_user: dict = Depends(require_admin)
):
    """Create a new alert (admin only)"""
    try:
        alert_dict = {
            "device_id": alert_data.device_id,
            "alert_type": alert_data.alert_type,
            "message": alert_data.message,
            "severity": alert_data.severity,
            "sensor_values": alert_data.sensor_values,
            "triggered_at": None  # Will be set by insert_alert
        }
        
        alert_id = await insert_alert(alert_dict)
        alert = await get_alert_by_id(alert_id)
        
        if not alert:
            raise HTTPException(status_code=500, detail="Failed to retrieve created alert")
        
        return AlertResponse(**alert)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

@router.get("", response_model=List[AlertResponse])
async def get_alerts_endpoint(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_viewer_or_above)
):
    """Get alerts with optional filters (requires authentication)"""
    try:
        alerts = await get_alerts(
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            acknowledged=acknowledged,
            limit=limit,
            offset=offset
        )
        return [AlertResponse(**alert) for alert in alerts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.get("/latest", response_model=List[AlertResponse])
async def get_latest_alerts_endpoint(
    limit: int = Query(10, ge=1, le=100),
    unacknowledged_only: bool = Query(False, description="Only return unacknowledged alerts"),
    current_user: dict = Depends(require_viewer_or_above)
):
    """Get latest alerts for real-time dashboard (requires authentication)"""
    try:
        alerts = await get_latest_alerts(limit=limit, unacknowledged_only=unacknowledged_only)
        return [AlertResponse(**alert) for alert in alerts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching latest alerts: {str(e)}")

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert_endpoint(
    alert_id: int,
    current_user: dict = Depends(require_viewer_or_above)
):
    """Get a specific alert by ID (requires authentication)"""
    alert = await get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse(**alert)

@router.post("/{alert_id}/acknowledge", status_code=200)
async def acknowledge_alert_endpoint(
    alert_id: int,
    current_user: dict = Depends(require_viewer_or_above)
):
    """Acknowledge an alert (requires authentication)"""
    try:
        # Check if alert exists
        alert = await get_alert_by_id(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found")
        
        # Check if already acknowledged
        if alert.get("acknowledged"):
            return {"message": "Alert already acknowledged", "alert_id": alert_id, "already_acknowledged": True}
        
        # Get username from current_user (could be "username" or "sub" depending on token structure)
        username = current_user.get("username") or current_user.get("sub") or "unknown"
        
        # Acknowledge alert
        success = await acknowledge_alert(alert_id, acknowledged_by=username)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert {alert_id}. The alert may not exist or may have already been acknowledged.")
        
        return {"message": "Alert acknowledged successfully", "alert_id": alert_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")

@router.get("/stats/summary")
async def get_alert_stats(
    current_user: dict = Depends(require_viewer_or_above)
):
    """Get alert statistics summary (requires authentication)"""
    try:
        total = await count_alerts()
        unacknowledged = await count_alerts(acknowledged=False)
        
        # Count by severity
        low = await count_alerts(severity="low")
        medium = await count_alerts(severity="medium")
        high = await count_alerts(severity="high")
        extreme = await count_alerts(severity="extreme")
        
        # Count by type
        fire_risk = await count_alerts(alert_type="fire_risk")
        unsafe_temp = await count_alerts(alert_type="unsafe_temperature")
        unsafe_humidity = await count_alerts(alert_type="unsafe_humidity")
        fluctuation = await count_alerts(alert_type="rapid_fluctuation")
        
        return {
            "total": total,
            "unacknowledged": unacknowledged,
            "acknowledged": total - unacknowledged,
            "by_severity": {
                "low": low,
                "medium": medium,
                "high": high,
                "extreme": extreme
            },
            "by_type": {
                "fire_risk": fire_risk,
                "unsafe_temperature": unsafe_temp,
                "unsafe_humidity": unsafe_humidity,
                "rapid_fluctuation": fluctuation
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alert stats: {str(e)}")


