#!/bin/bash
# Quick TLS Setup Script for Mosquitto

set -e

echo "=========================================="
echo "Quick MQTT TLS Setup"
echo "=========================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CERT_DIR="$SCRIPT_DIR/mqtt_broker/certs"
MOSQUITTO_CERT_DIR="/etc/mosquitto/certs"
MOSQUITTO_CONF_DIR="/etc/mosquitto/conf.d"

# Step 1: Generate certificates if they don't exist
echo "[1/4] Checking certificates..."
if [ ! -f "$CERT_DIR/ca.crt" ] || [ ! -f "$CERT_DIR/server.crt" ] || [ ! -f "$CERT_DIR/server.key" ]; then
    echo "   Certificates not found. Generating..."
    cd "$SCRIPT_DIR/mqtt_broker"
    
    if [ ! -f "generate_certificates.sh" ]; then
        echo "   ✗ Error: generate_certificates.sh not found!"
        exit 1
    fi
    
    chmod +x generate_certificates.sh
    
    # Get broker IP
    BROKER_IP="${MQTT_BROKER_HOST:-10.162.131.191}"
    read -p "   Enter broker IP address [$BROKER_IP]: " input
    BROKER_IP="${input:-$BROKER_IP}"
    
    # Generate certificates (non-interactive)
    export MQTT_BROKER_HOST="$BROKER_IP"
    echo "$BROKER_IP" | ./generate_certificates.sh 2>/dev/null || {
        # Manual generation if script fails
        echo "   Generating certificates manually..."
        mkdir -p certs
        cd certs
        
        openssl genrsa -out ca.key 2048
        openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=MQTT-CA"
        openssl genrsa -out server.key 2048
        openssl req -new -key server.key -out server.csr \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$BROKER_IP"
        
        # Create extension file
        cat > server_ext.conf <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = $BROKER_IP
IP.1 = $BROKER_IP
EOF
        
        openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
            -CAcreateserial -out server.crt -days 365 \
            -extensions v3_req -extfile server_ext.conf
        
        rm -f server.csr server_ext.conf
        chmod 600 *.key
        chmod 644 *.crt
    }
    echo "   ✓ Certificates generated"
else
    echo "   ✓ Certificates already exist"
fi

# Step 2: Copy certificates to Mosquitto
echo ""
echo "[2/4] Copying certificates to Mosquitto..."
sudo mkdir -p "$MOSQUITTO_CERT_DIR"
sudo cp "$CERT_DIR/ca.crt" "$MOSQUITTO_CERT_DIR/" 2>/dev/null || echo "   ⚠️  CA cert copy failed"
sudo cp "$CERT_DIR/server.crt" "$MOSQUITTO_CERT_DIR/" 2>/dev/null || echo "   ⚠️  Server cert copy failed"
sudo cp "$CERT_DIR/server.key" "$MOSQUITTO_CERT_DIR/" 2>/dev/null || echo "   ⚠️  Server key copy failed"

sudo chmod 644 "$MOSQUITTO_CERT_DIR"/*.crt 2>/dev/null || true
sudo chmod 600 "$MOSQUITTO_CERT_DIR"/*.key 2>/dev/null || true
sudo chown mosquitto:mosquitto "$MOSQUITTO_CERT_DIR"/* 2>/dev/null || true

echo "   ✓ Certificates copied to $MOSQUITTO_CERT_DIR"

# Step 3: Configure Mosquitto
echo ""
echo "[3/4] Configuring Mosquitto..."
sudo mkdir -p "$MOSQUITTO_CONF_DIR"

if [ -f "$SCRIPT_DIR/mqtt_broker/mosquitto_tls.conf" ]; then
    sudo cp "$SCRIPT_DIR/mqtt_broker/mosquitto_tls.conf" "$MOSQUITTO_CONF_DIR/mqtt_tls.conf"
    echo "   ✓ TLS configuration copied"
else
    echo "   Creating TLS configuration..."
    sudo tee "$MOSQUITTO_CONF_DIR/mqtt_tls.conf" > /dev/null <<EOF
# MQTT TLS Configuration
listener 8883
protocol mqtt

# TLS/SSL Configuration
cafile $MOSQUITTO_CERT_DIR/ca.crt
certfile $MOSQUITTO_CERT_DIR/server.crt
keyfile $MOSQUITTO_CERT_DIR/server.key

# TLS Version
tls_version tlsv1.2

# Require client certificates (false = server-only TLS)
require_certificate false

# Also listen on port 1883 (non-TLS) for backward compatibility
listener 1883
protocol mqtt
EOF
    echo "   ✓ TLS configuration created"
fi

# Step 4: Restart Mosquitto
echo ""
echo "[4/4] Restarting Mosquitto..."
sudo systemctl restart mosquitto
sleep 2

if systemctl is-active --quiet mosquitto; then
    echo "   ✓ Mosquitto restarted successfully"
else
    echo "   ✗ Mosquitto failed to start!"
    echo "   Check logs: sudo journalctl -u mosquitto -n 50"
    exit 1
fi

# Verify port 8883 is listening
echo ""
echo "Verifying TLS is working..."
sleep 1
if sudo netstat -tlnp 2>/dev/null | grep -q ":8883" || sudo ss -tlnp 2>/dev/null | grep -q ":8883"; then
    echo "   ✓ Port 8883 (TLS) is now listening!"
else
    echo "   ⚠️  Port 8883 not detected (may take a moment)"
    echo "   Check manually: sudo netstat -tlnp | grep 8883"
fi

echo ""
echo "=========================================="
echo "✓ TLS Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test connection: python check_mqtt_connection.py"
echo "2. Check logs if issues: sudo journalctl -u mosquitto -f"
echo ""

