#!/bin/bash
# Generate SSL/TLS certificates for MQTT broker
# This script creates a Certificate Authority (CA), server certificate, and client certificates

set -e

# Configuration
CERT_DIR="certs"
CA_KEY="${CERT_DIR}/ca.key"
CA_CRT="${CERT_DIR}/ca.crt"
SERVER_KEY="${CERT_DIR}/server.key"
SERVER_CRT="${CERT_DIR}/server.crt"
SERVER_CSR="${CERT_DIR}/server.csr"
CLIENT_KEY="${CERT_DIR}/client.key"
CLIENT_CRT="${CERT_DIR}/client.crt"
CLIENT_CSR="${CERT_DIR}/client.csr"

# Certificate validity (365 days = 1 year)
VALIDITY_DAYS=365

# Create certificates directory
mkdir -p "${CERT_DIR}"

echo "========================================="
echo "MQTT TLS Certificate Generation"
echo "========================================="
echo ""

# Get broker hostname/IP from environment or prompt
BROKER_HOST="${MQTT_BROKER_HOST:-10.162.131.191}"
read -p "Enter broker hostname/IP [${BROKER_HOST}]: " input
BROKER_HOST="${input:-${BROKER_HOST}}"

# Step 1: Generate CA private key
echo "[1/6] Generating CA private key..."
openssl genrsa -out "${CA_KEY}" 2048

# Step 2: Generate CA certificate
echo "[2/6] Generating CA certificate..."
openssl req -new -x509 -days "${VALIDITY_DAYS}" -key "${CA_KEY}" -out "${CA_CRT}" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=MQTT-CA"

# Step 3: Generate server private key
echo "[3/6] Generating server private key..."
openssl genrsa -out "${SERVER_KEY}" 2048

# Step 4: Generate server certificate signing request
echo "[4/6] Generating server certificate signing request..."
openssl req -new -key "${SERVER_KEY}" -out "${SERVER_CSR}" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=${BROKER_HOST}"

# Step 5: Sign server certificate with CA
echo "[5/6] Signing server certificate with CA..."
openssl x509 -req -in "${SERVER_CSR}" -CA "${CA_CRT}" -CAkey "${CA_KEY}" \
    -CAcreateserial -out "${SERVER_CRT}" -days "${VALIDITY_DAYS}" \
    -extensions v3_req -extfile <(cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = ${BROKER_HOST}
IP.1 = ${BROKER_HOST}
EOF
)

# Step 6: Generate client certificate (optional, for mutual TLS)
echo "[6/6] Generating client certificate..."
openssl genrsa -out "${CLIENT_KEY}" 2048
openssl req -new -key "${CLIENT_KEY}" -out "${CLIENT_CSR}" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=mqtt-client"
openssl x509 -req -in "${CLIENT_CSR}" -CA "${CA_CRT}" -CAkey "${CA_KEY}" \
    -CAcreateserial -out "${CLIENT_CRT}" -days "${VALIDITY_DAYS}" \
    -extensions v3_req -extfile <(cat <<EOF
[v3_req]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
EOF
)

# Clean up CSR files
rm -f "${SERVER_CSR}" "${CLIENT_CSR}"

# Set proper permissions
chmod 600 "${CA_KEY}" "${SERVER_KEY}" "${CLIENT_KEY}"
chmod 644 "${CA_CRT}" "${SERVER_CRT}" "${CLIENT_CRT}"

echo ""
echo "========================================="
echo "Certificate generation complete!"
echo "========================================="
echo ""
echo "Generated files in ${CERT_DIR}/:"
echo "  - ca.crt          (CA certificate)"
echo "  - ca.key          (CA private key - KEEP SECRET!)"
echo "  - server.crt      (Server certificate)"
echo "  - server.key      (Server private key - KEEP SECRET!)"
echo "  - client.crt      (Client certificate - optional)"
echo "  - client.key      (Client private key - KEEP SECRET!)"
echo ""
echo "Next steps:"
echo "1. Copy certificates to appropriate locations"
echo "2. Configure Mosquitto to use TLS (see mosquitto_tls.conf)"
echo "3. Update MQTT client configuration to use TLS"
echo ""
echo "⚠️  IMPORTANT: Keep private keys (.key files) secure!"
echo ""

