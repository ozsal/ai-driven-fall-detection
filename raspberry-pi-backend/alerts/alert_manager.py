"""
Alert Manager
Handles push notifications, email alerts, and dashboard notifications
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
try:
    import aiohttp
except ImportError:
    aiohttp = None

load_dotenv()

class AlertManager:
    """Manages all alert channels"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.alert_email_from = os.getenv("ALERT_EMAIL_FROM", "")
        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", "")
        self.fcm_server_key = os.getenv("FCM_SERVER_KEY", "")
    
    async def send_fall_alert(self, fall_event: Dict, event_id: str):
        """Send fall alert through all channels"""
        try:
            # Get user preferences
            user_prefs = await self._get_user_preferences(fall_event.get("user_id", "default"))
            
            alert_channels = []
            
            # Send email alert
            if user_prefs.get("email_enabled", True):
                email_sent = await self._send_email_alert(fall_event, event_id)
                if email_sent:
                    alert_channels.append("email")
            
            # Send push notification
            if user_prefs.get("push_enabled", True):
                push_sent = await self._send_push_notification(fall_event, event_id)
                if push_sent:
                    alert_channels.append("push")
            
            # Dashboard notification (always sent)
            alert_channels.append("dashboard")
            
            # Log alert status
            await self._log_alert_status(event_id, alert_channels)
            
            return {
                "alert_id": event_id,
                "channels": alert_channels,
                "sent_at": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error sending fall alert: {e}")
            return None
    
    async def _send_email_alert(self, fall_event: Dict, event_id: str) -> bool:
        """Send email alert"""
        try:
            if not self.smtp_username or not self.smtp_password:
                print("Email credentials not configured")
                return False
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["From"] = self.alert_email_from
            message["To"] = self.alert_email_to
            message["Subject"] = f"🚨 FALL DETECTED - Severity: {fall_event['severity_score']}/10"
            
            # Email body
            severity = fall_event["severity_score"]
            severity_level = "LOW" if severity < 4 else "MEDIUM" if severity < 7 else "HIGH"
            
            text = f"""
FALL DETECTION ALERT

A fall has been detected for user: {fall_event['user_id']}

Severity Score: {severity}/10 ({severity_level})
Location: {fall_event.get('location', 'Unknown')}
Time: {fall_event['timestamp']}
Verified: {'Yes' if fall_event['verified'] else 'No'}

Event ID: {event_id}

Please check on the person immediately.

---
Fall Detection System
"""
            
            html = f"""
<html>
<body>
<h2 style="color: red;">🚨 FALL DETECTION ALERT</h2>
<p><strong>A fall has been detected for user:</strong> {fall_event['user_id']}</p>
<table border="1" cellpadding="10">
<tr><td><strong>Severity Score</strong></td><td>{severity}/10 ({severity_level})</td></tr>
<tr><td><strong>Location</strong></td><td>{fall_event.get('location', 'Unknown')}</td></tr>
<tr><td><strong>Time</strong></td><td>{fall_event['timestamp']}</td></tr>
<tr><td><strong>Verified</strong></td><td>{'Yes' if fall_event['verified'] else 'No'}</td></tr>
<tr><td><strong>Event ID</strong></td><td>{event_id}</td></tr>
</table>
<p><strong style="color: red;">Please check on the person immediately.</strong></p>
<hr>
<p><small>Fall Detection System</small></p>
</body>
</html>
"""
            
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=True
            )
            
            print(f"Email alert sent for event {event_id}")
            return True
            
        except Exception as e:
            print(f"Error sending email alert: {e}")
            return False
    
    async def _send_push_notification(self, fall_event: Dict, event_id: str) -> bool:
        """Send push notification via FCM"""
        try:
            if not self.fcm_server_key:
                print("FCM server key not configured")
                return False
            
            if aiohttp is None:
                print("aiohttp not installed. Install with: pip install aiohttp")
                return False
            
            # FCM API endpoint
            
            url = "https://fcm.googleapis.com/fcm/send"
            headers = {
                "Authorization": f"key={self.fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            severity = fall_event["severity_score"]
            severity_level = "LOW" if severity < 4 else "MEDIUM" if severity < 7 else "HIGH"
            
            payload = {
                "to": "/topics/fall_alerts",  # Or specific device token
                "notification": {
                    "title": "🚨 Fall Detected",
                    "body": f"Severity: {severity}/10 ({severity_level}) - {fall_event.get('location', 'Unknown')}",
                    "sound": "default",
                    "priority": "high"
                },
                "data": {
                    "event_id": event_id,
                    "severity": str(severity),
                    "location": fall_event.get("location", "unknown"),
                    "timestamp": fall_event["timestamp"].isoformat()
                },
                "priority": "high"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        print(f"Push notification sent for event {event_id}")
                        return True
                    else:
                        print(f"FCM error: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"Error sending push notification: {e}")
            return False
    
    async def _get_user_preferences(self, user_id: str) -> Dict:
        """Get user notification preferences"""
        # In production, fetch from database
        # For now, return defaults
        return {
            "email_enabled": True,
            "push_enabled": True,
            "alert_threshold": 5.0
        }
    
    async def _log_alert_status(self, event_id: str, channels: List[str]):
        """Log alert status to database"""
        try:
            from database.sqlite_db import insert_alert_log
            await insert_alert_log(event_id, channels, "sent")
        except Exception as e:
            print(f"Error logging alert status: {e}")

