# Raspberry Pi Setup Guide

Complete setup instructions for deploying the Fall Detection System on Raspberry Pi.

## Quick Setup (Automated)

### Option 1: Using the Setup Script (Recommended)

1. **Copy project to Raspberry Pi:**
   ```bash
   # On your computer, transfer files to Raspberry Pi
   scp -r "AI driven fall detection" pi@raspberrypi.local:~/
   
   # Or use git if you have it in a repository
   git clone <your-repo-url>
   ```

2. **SSH into Raspberry Pi:**
   ```bash
   ssh pi@raspberrypi.local
   # Or use your Raspberry Pi's IP address
   ssh pi@192.168.1.XXX
   ```

3. **Run the setup script:**
   ```bash
   cd ~/ai-driven-fall-detection/raspberry-pi-backend
   chmod +x setup_raspberry_pi.sh
   ./setup_raspberry_pi.sh
   ```

The script will:
- ✅ Update system packages
- ✅ Install Python and dependencies
- ✅ Install and start Mosquitto MQTT broker
- ✅ Create virtual environment
- ✅ Install Python packages
- ✅ Create configuration file
- ✅ Initialize database

## Manual Setup

If you prefer to set up manually:

### Step 1: Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install System Dependencies

```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    mosquitto \
    mosquitto-clients \
    git \
    sqlite3
```

### Step 3: Start Mosquitto MQTT Broker

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
sudo systemctl status mosquitto
```

### Step 4: Setup Python Environment

```bash
# Navigate to project
cd ~/ai-driven-fall-detection/raspberry-pi-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies (use minimal if Python 3.13)
pip install -r requirements-minimal.txt
# OR for full features (if Python 3.9-3.11):
# pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

**Important settings to configure:**
- `MQTT_BROKER_HOST`: Usually `localhost` or `127.0.0.1`
- `MQTT_USERNAME` and `MQTT_PASSWORD`: Set secure credentials
- `SMTP_*`: Email settings for alerts (optional)
- `API_HOST`: `0.0.0.0` to accept connections from network
- `API_PORT`: Default `8000`

### Step 6: Initialize Database

```bash
cd api
python3 -c "from database.sqlite_db import init_database; import asyncio; asyncio.run(init_database())"
```

### Step 7: Test Installation

```bash
# Start the API
python main.py

# In another terminal, test it
curl http://localhost:8000/health
```

## Configuration

### MQTT Broker Setup

1. **Set up MQTT authentication:**
   ```bash
   sudo mosquitto_passwd -c /etc/mosquitto/passwd admin
   # Enter password when prompted
   ```

2. **Edit Mosquitto config:**
   ```bash
   sudo nano /etc/mosquitto/mosquitto.conf
   ```
   
   Add these lines:
   ```
   listener 1883
   allow_anonymous false
   password_file /etc/mosquitto/passwd
   ```

3. **Restart Mosquitto:**
   ```bash
   sudo systemctl restart mosquitto
   ```

4. **Update .env file with MQTT credentials:**
   ```bash
   nano raspberry-pi-backend/.env
   ```

### Network Configuration

**Find your Raspberry Pi IP address:**
```bash
hostname -I
```

**Configure firewall (if needed):**
```bash
# Allow MQTT port
sudo ufw allow 1883/tcp

# Allow API port
sudo ufw allow 8000/tcp
```

## Running the System

### Option 1: Manual Start

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend/api
source ../venv/bin/activate
python main.py
```

### Option 2: Using Start Script

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
chmod +x start.sh
./start.sh
```

### Option 3: Systemd Service (Production)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/fall-detection.service
```

Add this content:
```ini
[Unit]
Description=Fall Detection System API
After=network.target mosquitto.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ai-driven-fall-detection/raspberry-pi-backend/api
Environment="PATH=/home/pi/ai-driven-fall-detection/raspberry-pi-backend/venv/bin"
ExecStart=/home/pi/ai-driven-fall-detection/raspberry-pi-backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fall-detection
sudo systemctl start fall-detection
sudo systemctl status fall-detection
```

## Testing

### Test MQTT

```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "#" -u admin -P your_password

# In another terminal, publish test message
mosquitto_pub -h localhost -t "test/topic" -m "Hello" -u admin -P your_password
```

### Test API

```bash
# Health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/api/statistics

# Get devices
curl http://localhost:8000/api/devices
```

### Test Database

```bash
# Check database file exists
ls -lh fall_detection.db

# View database (optional)
sqlite3 fall_detection.db ".tables"
```

## Troubleshooting

### Python Version Issues

If you have Python 3.13:
```bash
# Use minimal requirements
pip install -r requirements-minimal.txt
```

### MQTT Connection Failed

```bash
# Check Mosquitto is running
sudo systemctl status mosquitto

# Check port is open
netstat -tuln | grep 1883

# Check logs
sudo journalctl -u mosquitto -f
```

### API Not Starting

```bash
# Check if port is in use
sudo lsof -i :8000

# Check Python errors
python main.py  # Run directly to see errors

# Check database permissions
ls -la fall_detection.db
```

### Permission Denied

```bash
# Fix permissions
chmod +x setup_raspberry_pi.sh
chmod +x start.sh

# Fix database directory
chmod 755 ~/ai-driven-fall-detection/raspberry-pi-backend
```

## Next Steps

1. ✅ **Configure ESP8266 sensors** - See `esp8266-sensors/` directory
2. ✅ **Configure web dashboard** - See `web-dashboard/` directory
3. ✅ **Setup mobile app** - See `mobile-app/` directory

## Support

- Check logs: `sudo journalctl -u fall-detection -f`
- View API logs: Check console output when running manually
- Database location: `raspberry-pi-backend/fall_detection.db`
- Configuration: `raspberry-pi-backend/.env`

## Security Notes

1. **Change default passwords** in `.env`
2. **Use strong MQTT credentials**
3. **Enable firewall** if exposing to network
4. **Use HTTPS** in production (requires reverse proxy)
5. **Regular updates**: `sudo apt-get update && sudo apt-get upgrade`



