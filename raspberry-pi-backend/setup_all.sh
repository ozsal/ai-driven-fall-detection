#!/bin/bash
# Comprehensive setup script for AI-Driven Fall Detection System
# This script sets up the entire backend system

set -e

echo "=========================================="
echo "AI-Driven Fall Detection System Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Linux/Raspberry Pi${NC}"
    echo "For Windows, use setup_all.ps1 instead"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
echo ""

# Step 1: Check Python version
echo "[1/8] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed!${NC}"
    echo "Please install Python 3.11 or 3.12"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Step 2: Create virtual environment
echo ""
echo "[2/8] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists, skipping...${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet

# Step 3: Install dependencies
echo ""
echo "[3/8] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}ERROR: requirements.txt not found!${NC}"
    exit 1
fi

# Step 4: Setup environment variables
echo ""
echo "[4/8] Setting up environment variables..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    
    # Get broker IP (default or from user)
    read -p "Enter MQTT broker IP address [10.162.131.191]: " BROKER_IP
    BROKER_IP=${BROKER_IP:-10.162.131.191}
    
    read -p "Enter MQTT broker port [1883]: " BROKER_PORT
    BROKER_PORT=${BROKER_PORT:-1883}
    
    read -p "Enter MQTT username (leave empty for no auth): " MQTT_USER
    read -p "Enter MQTT password (leave empty for no auth): " MQTT_PASS
    
    # Generate JWT secret
    echo "Generating JWT secret..."
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Create .env file
    cat > .env <<EOF
# MQTT Broker Configuration
MQTT_BROKER_HOST=$BROKER_IP
MQTT_BROKER_PORT=$BROKER_PORT
MQTT_USERNAME=$MQTT_USER
MQTT_PASSWORD=$MQTT_PASS

# JWT Secret Key (for authentication)
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./fall_detection.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF
    
    echo -e "${GREEN}✓ .env file created${NC}"
    echo "  - MQTT Broker: $BROKER_IP:$BROKER_PORT"
    if [ -n "$MQTT_USER" ]; then
        echo "  - MQTT Auth: Enabled ($MQTT_USER)"
    else
        echo "  - MQTT Auth: Disabled"
    fi
else
    echo -e "${YELLOW}.env file already exists, skipping...${NC}"
    echo "If you need to update it, edit .env manually"
fi

# Step 5: Initialize database
echo ""
echo "[5/8] Initializing database..."
if [ -f "setup_database.py" ]; then
    python3 setup_database.py
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${YELLOW}setup_database.py not found, database will be created on first run${NC}"
fi

# Step 6: Check Mosquitto
echo ""
echo "[6/8] Checking MQTT broker (Mosquitto)..."
if command -v mosquitto &> /dev/null || command -v mosquitto_pub &> /dev/null; then
    echo -e "${GREEN}✓ Mosquitto is installed${NC}"
    
    # Check if Mosquitto is running
    if systemctl is-active --quiet mosquitto 2>/dev/null; then
        echo -e "${GREEN}✓ Mosquitto service is running${NC}"
    else
        echo -e "${YELLOW}⚠ Mosquitto service is not running${NC}"
        read -p "Do you want to start Mosquitto? (y/n): " START_MOSQUITTO
        if [[ "$START_MOSQUITTO" =~ ^[Yy]$ ]]; then
            sudo systemctl start mosquitto
            sudo systemctl enable mosquitto
            echo -e "${GREEN}✓ Mosquitto started and enabled${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Mosquitto not found${NC}"
    echo "To install: sudo apt install mosquitto mosquitto-clients"
fi

# Step 7: Test MQTT connection
echo ""
echo "[7/8] Testing MQTT connection..."
if command -v mosquitto_pub &> /dev/null; then
    # Load .env variables
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    BROKER_IP=${MQTT_BROKER_HOST:-localhost}
    BROKER_PORT=${MQTT_BROKER_PORT:-1883}
    
    # Test connection
    if timeout 2 mosquitto_pub -h "$BROKER_IP" -p "$BROKER_PORT" -t "test/connection" -m "test" &>/dev/null; then
        echo -e "${GREEN}✓ MQTT broker is accessible at $BROKER_IP:$BROKER_PORT${NC}"
    else
        echo -e "${YELLOW}⚠ Could not connect to MQTT broker at $BROKER_IP:$BROKER_PORT${NC}"
        echo "  Make sure Mosquitto is running and accessible"
    fi
else
    echo -e "${YELLOW}⚠ mosquitto_pub not available, skipping connection test${NC}"
fi

# Step 8: Create admin user (optional)
echo ""
echo "[8/8] Creating admin user..."
if [ -f "setup_database.py" ]; then
    read -p "Do you want to create an admin user now? (y/n): " CREATE_USER
    if [[ "$CREATE_USER" =~ ^[Yy]$ ]]; then
        read -p "Enter admin username: " ADMIN_USER
        read -sp "Enter admin password: " ADMIN_PASS
        echo ""
        
        python3 <<EOF
import asyncio
import sys
from auth.database import create_user, hash_password, get_user_by_username

async def create_admin():
    username = "$ADMIN_USER"
    password = "$ADMIN_PASS"
    
    # Check if user exists
    existing = await get_user_by_username(username)
    if existing:
        print(f"User '{username}' already exists!")
        return
    
    # Create user
    hashed = hash_password(password)
    user = await create_user(
        username=username,
        email=f"{username}@example.com",
        hashed_password=hashed,
        role="admin"
    )
    print(f"✓ Admin user '{username}' created successfully!")

asyncio.run(create_admin())
EOF
    else
        echo "Skipping admin user creation"
        echo "You can create users later or on first API start"
    fi
fi

# Final summary
echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start the backend: python api/main.py"
echo "3. Or use start script: ./start_backend.sh"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "To test MQTT connection:"
echo "  python check_mqtt_connection.py"
echo ""


