#!/bin/bash
# MQTT TLS Connection Diagnostic Script

echo "=========================================="
echo "MQTT TLS Connection Diagnostics"
echo "=========================================="
echo ""

# Check if Mosquitto is running
echo "1. Checking Mosquitto service status..."
if systemctl is-active --quiet mosquitto 2>/dev/null; then
    echo "   ✓ Mosquitto service is running"
else
    echo "   ✗ Mosquitto service is NOT running"
    echo "   Start with: sudo systemctl start mosquitto"
    exit 1
fi

# Check what ports Mosquitto is listening on
echo ""
echo "2. Checking which ports Mosquitto is listening on..."
PORTS=$(sudo netstat -tlnp 2>/dev/null | grep mosquitto | awk '{print $4}' | cut -d: -f2 | sort -u)
if [ -z "$PORTS" ]; then
    # Try with ss instead
    PORTS=$(sudo ss -tlnp 2>/dev/null | grep mosquitto | awk '{print $4}' | cut -d: -f2 | sort -u)
fi

if [ -z "$PORTS" ]; then
    echo "   ⚠️  Could not detect listening ports (may need sudo)"
    echo "   Try manually: sudo netstat -tlnp | grep mosquitto"
else
    echo "   Mosquitto is listening on ports: $PORTS"
    if echo "$PORTS" | grep -q "8883"; then
        echo "   ✓ Port 8883 (TLS) is active"
    else
        echo "   ✗ Port 8883 (TLS) is NOT active"
    fi
    if echo "$PORTS" | grep -q "1883"; then
        echo "   ✓ Port 1883 (non-TLS) is active"
    fi
fi

# Check Mosquitto configuration
echo ""
echo "3. Checking Mosquitto configuration..."
if [ -f "/etc/mosquitto/mosquitto.conf" ]; then
    echo "   ✓ Main config file exists"
    if grep -q "listener 8883" /etc/mosquitto/mosquitto.conf; then
        echo "   ✓ TLS listener (8883) found in main config"
    fi
    if grep -q "listener 1883" /etc/mosquitto/mosquitto.conf; then
        echo "   ✓ Non-TLS listener (1883) found in main config"
    fi
else
    echo "   ⚠️  Main config file not found at /etc/mosquitto/mosquitto.conf"
fi

# Check for TLS config in conf.d
echo ""
echo "4. Checking for TLS configuration files..."
if [ -d "/etc/mosquitto/conf.d" ]; then
    TLS_CONFIG=$(find /etc/mosquitto/conf.d -name "*tls*" -o -name "*ssl*" 2>/dev/null | head -1)
    if [ -n "$TLS_CONFIG" ]; then
        echo "   ✓ Found TLS config: $TLS_CONFIG"
        if grep -q "listener 8883" "$TLS_CONFIG"; then
            echo "   ✓ TLS listener configured"
        fi
        if grep -q "cafile\|certfile\|keyfile" "$TLS_CONFIG"; then
            echo "   ✓ Certificate paths configured"
            # Check if cert files exist
            CA_FILE=$(grep "cafile" "$TLS_CONFIG" | awk '{print $2}' | head -1)
            if [ -n "$CA_FILE" ] && [ -f "$CA_FILE" ]; then
                echo "   ✓ CA certificate exists: $CA_FILE"
            elif [ -n "$CA_FILE" ]; then
                echo "   ✗ CA certificate missing: $CA_FILE"
            fi
        fi
    else
        echo "   ✗ No TLS configuration found in /etc/mosquitto/conf.d/"
    fi
else
    echo "   ⚠️  /etc/mosquitto/conf.d/ directory does not exist"
fi

# Check certificate files
echo ""
echo "5. Checking certificate files..."
CERT_DIR="/etc/mosquitto/certs"
if [ -d "$CERT_DIR" ]; then
    echo "   ✓ Certificate directory exists"
    if [ -f "$CERT_DIR/ca.crt" ]; then
        echo "   ✓ CA certificate exists"
    else
        echo "   ✗ CA certificate missing: $CERT_DIR/ca.crt"
    fi
    if [ -f "$CERT_DIR/server.crt" ]; then
        echo "   ✓ Server certificate exists"
    else
        echo "   ✗ Server certificate missing: $CERT_DIR/server.crt"
    fi
    if [ -f "$CERT_DIR/server.key" ]; then
        echo "   ✓ Server private key exists"
    else
        echo "   ✗ Server private key missing: $CERT_DIR/server.key"
    fi
else
    echo "   ✗ Certificate directory does not exist: $CERT_DIR"
fi

# Check Mosquitto logs for errors
echo ""
echo "6. Checking recent Mosquitto logs for errors..."
RECENT_ERRORS=$(sudo journalctl -u mosquitto -n 20 --no-pager 2>/dev/null | grep -i "error\|fail\|tls\|ssl" | tail -5)
if [ -n "$RECENT_ERRORS" ]; then
    echo "   Recent errors/warnings:"
    echo "$RECENT_ERRORS" | sed 's/^/     /'
else
    echo "   ✓ No recent errors in logs"
fi

echo ""
echo "=========================================="
echo "Recommendations:"
echo "=========================================="
echo ""

# Give recommendations based on findings
if ! echo "$PORTS" | grep -q "8883"; then
    echo "⚠️  Port 8883 is not active. Options:"
    echo ""
    echo "Option A: Set up TLS (recommended):"
    echo "  1. Generate certificates:"
    echo "     cd ~/ai-driven-fall-detection/raspberry-pi-backend/mqtt_broker"
    echo "     ./generate_certificates.sh"
    echo ""
    echo "  2. Copy certificates:"
    echo "     sudo mkdir -p /etc/mosquitto/certs"
    echo "     sudo cp certs/*.crt /etc/mosquitto/certs/"
    echo "     sudo cp certs/*.key /etc/mosquitto/certs/"
    echo "     sudo chmod 644 /etc/mosquitto/certs/*.crt"
    echo "     sudo chmod 600 /etc/mosquitto/certs/*.key"
    echo ""
    echo "  3. Configure TLS:"
    echo "     sudo cp mqtt_broker/mosquitto_tls.conf /etc/mosquitto/conf.d/"
    echo "     sudo systemctl restart mosquitto"
    echo ""
    echo "Option B: Use non-TLS temporarily (port 1883):"
    echo "  Update .env file:"
    echo "    MQTT_BROKER_PORT=1883"
    echo "    MQTT_USE_TLS=false"
    echo ""
fi

echo "To check Mosquitto logs:"
echo "  sudo journalctl -u mosquitto -f"
echo ""

