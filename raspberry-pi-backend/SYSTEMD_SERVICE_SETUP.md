# Systemd Service Setup for Fall Detection Backend

## Overview

This guide explains how to set up the fall detection backend as a systemd service on your Raspberry Pi, so it starts automatically on boot and can be managed with systemctl.

## Prerequisites

- Backend is installed at: `/home/uel/ai-driven-fall-detection/raspberry-pi-backend`
- Virtual environment exists at: `/home/uel/ai-driven-fall-detection/raspberry-pi-backend/venv`
- User running the service: `uel`
- Mosquitto MQTT broker is installed and configured

## Installation Steps

### 1. Copy Service File

Copy the service file to systemd directory:

```bash
sudo cp /home/uel/ai-driven-fall-detection/raspberry-pi-backend/fall-detection.service /etc/systemd/system/
```

### 2. Update Service File (if needed)

If your paths are different, edit the service file:

```bash
sudo nano /etc/systemd/system/fall-detection.service
```

Update these paths if needed:
- `WorkingDirectory`: Path to `raspberry-pi-backend` directory
- `ExecStart`: Path to Python in venv and path to `main.py`
- `User` and `Group`: Your username

### 3. Reload Systemd

Reload systemd to recognize the new service:

```bash
sudo systemctl daemon-reload
```

### 4. Enable Service (Start on Boot)

Enable the service to start automatically on boot:

```bash
sudo systemctl enable fall-detection.service
```

### 5. Start the Service

Start the service:

```bash
sudo systemctl start fall-detection.service
```

### 6. Check Status

Verify the service is running:

```bash
sudo systemctl status fall-detection.service
```

You should see:
```
● fall-detection.service - AI-Driven Fall Detection Backend Service
   Loaded: loaded (/etc/systemd/system/fall-detection.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

## Service Management Commands

### Start Service
```bash
sudo systemctl start fall-detection
```

### Stop Service
```bash
sudo systemctl stop fall-detection
```

### Restart Service
```bash
sudo systemctl restart fall-detection
```

### Check Status
```bash
sudo systemctl status fall-detection
```

### View Logs
```bash
# View recent logs
sudo journalctl -u fall-detection -n 50

# Follow logs in real-time
sudo journalctl -u fall-detection -f

# View logs since boot
sudo journalctl -u fall-detection -b
```

### Disable Auto-Start
```bash
sudo systemctl disable fall-detection
```

### Enable Auto-Start
```bash
sudo systemctl enable fall-detection
```

## Troubleshooting

### Service Fails to Start

1. **Check service status:**
   ```bash
   sudo systemctl status fall-detection
   ```

2. **View detailed logs:**
   ```bash
   sudo journalctl -u fall-detection -n 100 --no-pager
   ```

3. **Check if paths are correct:**
   ```bash
   # Verify Python path
   /home/uel/ai-driven-fall-detection/raspberry-pi-backend/venv/bin/python --version
   
   # Verify main.py exists
   ls -l /home/uel/ai-driven-fall-detection/raspberry-pi-backend/api/main.py
   ```

4. **Test manual start:**
   ```bash
   cd /home/uel/ai-driven-fall-detection/raspberry-pi-backend
   source venv/bin/activate
   cd api
   python main.py
   ```

### Service Keeps Restarting

If the service keeps restarting, check the logs for errors:

```bash
sudo journalctl -u fall-detection -n 100 --no-pager
```

Common issues:
- Missing dependencies
- Database permissions
- MQTT broker not running
- Port 8000 already in use

### Permission Issues

If you see permission errors:

1. **Check file ownership:**
   ```bash
   ls -la /home/uel/ai-driven-fall-detection/raspberry-pi-backend/
   ```

2. **Fix ownership if needed:**
   ```bash
   sudo chown -R uel:uel /home/uel/ai-driven-fall-detection/
   ```

3. **Check database permissions:**
   ```bash
   ls -la /home/uel/ai-driven-fall-detection/raspberry-pi-backend/fall_detection.db
   ```

### Port Already in Use

If port 8000 is already in use:

1. **Find process using port 8000:**
   ```bash
   sudo lsof -i :8000
   ```

2. **Kill the process:**
   ```bash
   sudo kill <PID>
   ```

3. **Or change port in service file:**
   Edit `/etc/systemd/system/fall-detection.service` and change:
   ```
   Environment="API_PORT=8001"
   ```
   Then restart the service.

## Service File Details

The service file includes:

- **After=mosquitto.service**: Ensures MQTT broker starts first
- **Restart=always**: Automatically restarts if service crashes
- **RestartSec=10**: Waits 10 seconds before restarting
- **StandardOutput=journal**: Logs to systemd journal
- **StandardError=journal**: Error logs to systemd journal

## Verification

After starting the service, verify it's working:

1. **Check service status:**
   ```bash
   sudo systemctl status fall-detection
   ```

2. **Test API endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check if MQTT is connected:**
   Look for "✓ MQTT client connected" in logs:
   ```bash
   sudo journalctl -u fall-detection | grep "MQTT"
   ```

4. **Check database:**
   ```bash
   curl http://localhost:8000/api/statistics
   ```

## Notes

- The service runs as user `uel` (not root) for security
- Logs are available via `journalctl`
- Service automatically restarts on failure
- Service starts after network and MQTT broker are ready

