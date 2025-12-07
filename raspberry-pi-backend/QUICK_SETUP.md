# Quick Systemd Service Setup

## One-Command Setup

On your Raspberry Pi, run:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
chmod +x setup_systemd_service.sh
sudo ./setup_systemd_service.sh
```

That's it! The script will:
- ✅ Detect your user and paths automatically
- ✅ Install the service file
- ✅ Enable it to start on boot
- ✅ Start the service
- ✅ Show you the status

## Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Copy service file
sudo cp ~/ai-driven-fall-detection/raspberry-pi-backend/fall-detection.service /etc/systemd/system/

# 2. Edit paths if needed (replace 'uel' with your username)
sudo nano /etc/systemd/system/fall-detection.service

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable and start
sudo systemctl enable fall-detection
sudo systemctl start fall-detection

# 5. Check status
sudo systemctl status fall-detection
```

## Verify It's Working

```bash
# Check service status
sudo systemctl status fall-detection

# Test API
curl http://localhost:8000/health

# View logs
sudo journalctl -u fall-detection -f
```

## Service Commands

```bash
sudo systemctl start fall-detection    # Start
sudo systemctl stop fall-detection     # Stop
sudo systemctl restart fall-detection  # Restart
sudo systemctl status fall-detection   # Status
sudo journalctl -u fall-detection -f   # View logs
```

