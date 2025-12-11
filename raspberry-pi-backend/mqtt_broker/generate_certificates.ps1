# Generate SSL/TLS certificates for MQTT broker (Windows PowerShell)
# This script creates a Certificate Authority (CA), server certificate, and client certificates

$ErrorActionPreference = "Stop"

# Configuration
$CERT_DIR = "certs"
$CA_KEY = "$CERT_DIR\ca.key"
$CA_CRT = "$CERT_DIR\ca.crt"
$SERVER_KEY = "$CERT_DIR\server.key"
$SERVER_CRT = "$CERT_DIR\server.crt"
$SERVER_CSR = "$CERT_DIR\server.csr"
$CLIENT_KEY = "$CERT_DIR\client.key"
$CLIENT_CRT = "$CERT_DIR\client.crt"
$CLIENT_CSR = "$CERT_DIR\client.csr"

# Certificate validity (365 days = 1 year)
$VALIDITY_DAYS = 365

# Create certificates directory
New-Item -ItemType Directory -Force -Path $CERT_DIR | Out-Null

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MQTT TLS Certificate Generation" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Get broker hostname/IP from environment or prompt
$BROKER_HOST = $env:MQTT_BROKER_HOST
if (-not $BROKER_HOST) {
    $BROKER_HOST = "10.162.131.191"
}
$input = Read-Host "Enter broker hostname/IP [$BROKER_HOST]"
if ($input) {
    $BROKER_HOST = $input
}

# Check if OpenSSL is available
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
    Write-Host "ERROR: OpenSSL not found!" -ForegroundColor Red
    Write-Host "Please install OpenSSL:" -ForegroundColor Yellow
    Write-Host "  - Download from: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Yellow
    Write-Host "  - Or install via Chocolatey: choco install openssl" -ForegroundColor Yellow
    exit 1
}

# Step 1: Generate CA private key
Write-Host "[1/6] Generating CA private key..." -ForegroundColor Green
& openssl genrsa -out $CA_KEY 2048

# Step 2: Generate CA certificate
Write-Host "[2/6] Generating CA certificate..." -ForegroundColor Green
& openssl req -new -x509 -days $VALIDITY_DAYS -key $CA_KEY -out $CA_CRT `
    -subj "/C=US/ST=State/L=City/O=Organization/CN=MQTT-CA"

# Step 3: Generate server private key
Write-Host "[3/6] Generating server private key..." -ForegroundColor Green
& openssl genrsa -out $SERVER_KEY 2048

# Step 4: Generate server certificate signing request
Write-Host "[4/6] Generating server certificate signing request..." -ForegroundColor Green
& openssl req -new -key $SERVER_KEY -out $SERVER_CSR `
    -subj "/C=US/ST=State/L=City/O=Organization/CN=$BROKER_HOST"

# Step 5: Sign server certificate with CA
Write-Host "[5/6] Signing server certificate with CA..." -ForegroundColor Green
# Create temporary config file for extensions
$EXT_CONFIG = "$CERT_DIR\server_ext.conf"
@"
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = $BROKER_HOST
IP.1 = $BROKER_HOST
"@ | Out-File -FilePath $EXT_CONFIG -Encoding ASCII

& openssl x509 -req -in $SERVER_CSR -CA $CA_CRT -CAkey $CA_KEY `
    -CAcreateserial -out $SERVER_CRT -days $VALIDITY_DAYS `
    -extensions v3_req -extfile $EXT_CONFIG

# Step 6: Generate client certificate (optional, for mutual TLS)
Write-Host "[6/6] Generating client certificate..." -ForegroundColor Green
& openssl genrsa -out $CLIENT_KEY 2048
& openssl req -new -key $CLIENT_KEY -out $CLIENT_CSR `
    -subj "/C=US/ST=State/L=City/O=Organization/CN=mqtt-client"

$CLIENT_EXT_CONFIG = "$CERT_DIR\client_ext.conf"
@"
[v3_req]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
"@ | Out-File -FilePath $CLIENT_EXT_CONFIG -Encoding ASCII

& openssl x509 -req -in $CLIENT_CSR -CA $CA_CRT -CAkey $CA_KEY `
    -CAcreateserial -out $CLIENT_CRT -days $VALIDITY_DAYS `
    -extensions v3_req -extfile $CLIENT_EXT_CONFIG

# Clean up CSR and config files
Remove-Item -Force $SERVER_CSR, $CLIENT_CSR, $EXT_CONFIG, $CLIENT_EXT_CONFIG -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Certificate generation complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Generated files in $CERT_DIR\:" -ForegroundColor Yellow
Write-Host "  - ca.crt          (CA certificate)"
Write-Host "  - ca.key          (CA private key - KEEP SECRET!)"
Write-Host "  - server.crt      (Server certificate)"
Write-Host "  - server.key      (Server private key - KEEP SECRET!)"
Write-Host "  - client.crt      (Client certificate - optional)"
Write-Host "  - client.key      (Client private key - KEEP SECRET!)"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy certificates to appropriate locations"
Write-Host "2. Configure Mosquitto to use TLS (see mosquitto_tls.conf)"
Write-Host "3. Update MQTT client configuration to use TLS"
Write-Host ""
Write-Host "⚠️  IMPORTANT: Keep private keys (.key files) secure!" -ForegroundColor Red
Write-Host ""

