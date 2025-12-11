#!/bin/bash
# Automated setup script for fall-detection systemd service
# Run this script with sudo to install the service

set -e  # Exit on error

echo "=========================================="
echo "Fall Detection Systemd Service Setup"
echo "=========================================="
echo ""

# Get the current directory (should be raspberry-pi-backend)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="fall-detection"
SERVICE_FILE="$SCRIPT_DIR/$SERVICE_NAME.service"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_NAME.service"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Error: This script must be run with sudo"
    echo "Usage: sudo ./setup_systemd_service.sh"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Error: Service file not found at $SERVICE_FILE"
    exit 1
fi

# Get the actual user (the one who ran sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo "📋 Configuration:"
echo "   Service name: $SERVICE_NAME"
echo "   Service file: $SERVICE_FILE"
echo "   Systemd path: $SYSTEMD_PATH"
echo "   User: $ACTUAL_USER"
echo "   Home: $ACTUAL_HOME"
echo ""

# Update service file with actual paths
echo "🔧 Updating service file with actual paths..."

# Create a temporary service file with updated paths
TEMP_SERVICE=$(mktemp)
sed "s|/home/uel|$ACTUAL_HOME|g" "$SERVICE_FILE" > "$TEMP_SERVICE"
sed -i "s|User=uel|User=$ACTUAL_USER|g" "$TEMP_SERVICE"
sed -i "s|Group=uel|Group=$ACTUAL_USER|g" "$TEMP_SERVICE"

# Verify paths exist
BACKEND_DIR="$ACTUAL_HOME/ai-driven-fall-detection/raspberry-pi-backend"
VENV_PYTHON="$BACKEND_DIR/venv/bin/python"
MAIN_PY="$BACKEND_DIR/api/main.py"

echo "🔍 Verifying paths..."
if [ ! -d "$BACKEND_DIR" ]; then
    echo "⚠️  Warning: Backend directory not found at $BACKEND_DIR"
    echo "   Using script directory instead: $SCRIPT_DIR"
    BACKEND_DIR="$SCRIPT_DIR"
    VENV_PYTHON="$BACKEND_DIR/venv/bin/python"
    MAIN_PY="$BACKEND_DIR/api/main.py"
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "⚠️  Warning: Virtual environment Python not found at $VENV_PYTHON"
    echo "   Will use system Python instead"
    VENV_PYTHON=$(which python3)
fi

if [ ! -f "$MAIN_PY" ]; then
    echo "❌ Error: main.py not found at $MAIN_PY"
    exit 1
fi

# Update paths in temp service file
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$BACKEND_DIR|g" "$TEMP_SERVICE"
sed -i "s|ExecStart=.*|ExecStart=$VENV_PYTHON $MAIN_PY|g" "$TEMP_SERVICE"
sed -i "s|Environment=\"PATH=.*|Environment=\"PATH=$BACKEND_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin\"|g" "$TEMP_SERVICE"

echo "✅ Paths verified"
echo ""

# Copy service file to systemd directory
echo "📦 Installing service file..."
cp "$TEMP_SERVICE" "$SYSTEMD_PATH"
chmod 644 "$SYSTEMD_PATH"
rm "$TEMP_SERVICE"
echo "✅ Service file installed to $SYSTEMD_PATH"
echo ""

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload
echo "✅ Systemd daemon reloaded"
echo ""

# Enable service
echo "🔌 Enabling service (start on boot)..."
systemctl enable "$SERVICE_NAME.service"
echo "✅ Service enabled"
echo ""

# Check if service is already running
if systemctl is-active --quiet "$SERVICE_NAME.service"; then
    echo "⚠️  Service is already running. Restarting..."
    systemctl restart "$SERVICE_NAME.service"
else
    echo "🚀 Starting service..."
    systemctl start "$SERVICE_NAME.service"
fi

# Wait a moment for service to start
sleep 2

# Check status
echo ""
echo "📊 Service Status:"
echo "=========================================="
systemctl status "$SERVICE_NAME.service" --no-pager -l || true
echo ""

# Show useful commands
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  Status:    sudo systemctl status $SERVICE_NAME"
echo "  Start:     sudo systemctl start $SERVICE_NAME"
echo "  Stop:      sudo systemctl stop $SERVICE_NAME"
echo "  Restart:   sudo systemctl restart $SERVICE_NAME"
echo "  Logs:      sudo journalctl -u $SERVICE_NAME -f"
echo "  Disable:   sudo systemctl disable $SERVICE_NAME"
echo ""
echo "Test API:"
echo "  curl http://localhost:8000/health"
echo ""




