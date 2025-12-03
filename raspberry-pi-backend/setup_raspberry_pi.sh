#!/bin/bash

# Raspberry Pi Setup Script for Fall Detection System
# Run this script on your Raspberry Pi

set -e  # Exit on error

echo "=========================================="
echo "Fall Detection System - Raspberry Pi Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}Warning: This script is designed for Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Update system
echo -e "${GREEN}[1/8] Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Step 2: Check Python version
echo -e "${GREEN}[2/8] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python version: $PYTHON_VERSION"

# Check if Python 3.13 (not recommended)
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>/dev/null; then
    echo -e "${YELLOW}Warning: Python 3.13 detected. Some packages may not work.${NC}"
    echo -e "${YELLOW}Consider using Python 3.11 or earlier, or use minimal requirements.${NC}"
    USE_MINIMAL=true
else
    USE_MINIMAL=false
fi

# Step 3: Install system dependencies
echo -e "${GREEN}[3/8] Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    mosquitto \
    mosquitto-clients \
    git \
    build-essential \
    sqlite3

# Step 4: Start Mosquitto
echo -e "${GREEN}[4/8] Starting Mosquitto MQTT broker...${NC}"
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
sudo systemctl status mosquitto --no-pager | head -3

# Step 5: Navigate to project directory
echo -e "${GREEN}[5/8] Setting up project directory...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR/raspberry-pi-backend" || exit 1

echo "Project directory: $(pwd)"

# Step 6: Create virtual environment
echo -e "${GREEN}[6/8] Creating Python virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Step 7: Upgrade pip and install dependencies
echo -e "${GREEN}[7/8] Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel

if [ "$USE_MINIMAL" = true ]; then
    echo -e "${YELLOW}Using minimal requirements (no numpy/tensorflow)${NC}"
    pip install -r requirements-minimal.txt
else
    echo "Installing full requirements..."
    if ! pip install -r requirements.txt; then
        echo -e "${YELLOW}Full requirements failed. Trying minimal requirements...${NC}"
        pip install -r requirements-minimal.txt
    fi
fi

# Step 8: Setup environment file
echo -e "${GREEN}[8/8] Setting up configuration...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file from .env.example${NC}"
        echo -e "${YELLOW}Please edit .env file with your settings!${NC}"
    else
        echo -e "${YELLOW}.env.example not found. Creating basic .env...${NC}"
        cat > .env << EOF
# SQLite Database Configuration
DB_DIR=.
DB_NAME=fall_detection.db

# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=admin_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=$(openssl rand -hex 32)

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
ALERT_EMAIL_FROM=
ALERT_EMAIL_TO=

# Fall Detection Thresholds
FALL_SEVERITY_THRESHOLD=5.0
PIR_INACTIVITY_THRESHOLD=10
ULTRASONIC_GROUND_THRESHOLD=50
TEMP_CHANGE_THRESHOLD=2.0
HUMIDITY_CHANGE_THRESHOLD=5.0
EOF
    fi
else
    echo ".env file already exists"
fi

# Initialize database
echo -e "${GREEN}Initializing database...${NC}"
cd api
python3 -c "from database.sqlite_db import init_database; import asyncio; asyncio.run(init_database())" || echo "Database will be created on first run"

# Summary
echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your settings:"
echo "   nano $PROJECT_DIR/raspberry-pi-backend/.env"
echo ""
echo "2. Start the API server:"
echo "   cd $PROJECT_DIR/raspberry-pi-backend/api"
echo "   source ../venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Or use the start script:"
echo "   cd $PROJECT_DIR/raspberry-pi-backend"
echo "   chmod +x start.sh"
echo "   ./start.sh"
echo ""
echo "4. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo -e "${GREEN}Setup completed successfully!${NC}"

