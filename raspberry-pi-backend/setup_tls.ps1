# Setup TLS/SSL for MQTT - Windows Helper Script
# Note: Certificates should be generated on the Raspberry Pi where Mosquitto runs

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "MQTT TLS/SSL Setup Helper" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ENV_FILE = ".env"
$BROKER_IP = "10.162.131.191"

# Check if .env exists
if (-not (Test-Path $ENV_FILE)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" $ENV_FILE -ErrorAction SilentlyContinue
    if (-not (Test-Path $ENV_FILE)) {
        # Create basic .env if no example exists
        @"
# MQTT Broker Configuration
MQTT_BROKER_HOST=$BROKER_IP
MQTT_BROKER_PORT=8883
MQTT_USERNAME=
MQTT_PASSWORD=

# TLS/SSL Configuration
MQTT_USE_TLS=true
MQTT_CA_CERT=mqtt_broker/certs/ca.crt
# MQTT_CLIENT_CERT=mqtt_broker/certs/client.crt
# MQTT_CLIENT_KEY=mqtt_broker/certs/client.key
MQTT_TLS_INSECURE=false

# JWT Secret Key (generate using generate_jwt_secret.py)
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"@ | Out-File -FilePath $ENV_FILE -Encoding UTF8
    }
}

Write-Host "Updating .env file with TLS configuration..." -ForegroundColor Green

# Read .env file
$content = Get-Content $ENV_FILE -Raw

# Update or add TLS settings
$updates = @{
    "MQTT_BROKER_PORT" = "8883"
    "MQTT_USE_TLS" = "true"
    "MQTT_CA_CERT" = "mqtt_broker/certs/ca.crt"
    "MQTT_TLS_INSECURE" = "false"
}

$lines = Get-Content $ENV_FILE
$updated = $false
$newContent = @()

foreach ($line in $lines) {
    $updatedLine = $line
    foreach ($key in $updates.Keys) {
        if ($line -match "^$key\s*=") {
            $updatedLine = "$key=$($updates[$key])"
            $updated = $true
            break
        }
    }
    $newContent += $updatedLine
}

# Add missing keys
foreach ($key in $updates.Keys) {
    if (-not ($newContent -match "^$key\s*=")) {
        $newContent += "$key=$($updates[$key])"
        $updated = $true
    }
}

if ($updated) {
    $newContent | Out-File -FilePath $ENV_FILE -Encoding UTF8
    Write-Host "✓ .env file updated with TLS configuration" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already has TLS configuration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Generate certificates on Raspberry Pi:" -ForegroundColor White
Write-Host "   cd raspberry-pi-backend/mqtt_broker" -ForegroundColor Gray
Write-Host "   ./generate_certificates.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Copy certificates to Mosquitto:" -ForegroundColor White
Write-Host "   sudo mkdir -p /etc/mosquitto/certs" -ForegroundColor Gray
Write-Host "   sudo cp certs/*.crt /etc/mosquitto/certs/" -ForegroundColor Gray
Write-Host "   sudo cp certs/*.key /etc/mosquitto/certs/" -ForegroundColor Gray
Write-Host "   sudo chmod 644 /etc/mosquitto/certs/*.crt" -ForegroundColor Gray
Write-Host "   sudo chmod 600 /etc/mosquitto/certs/*.key" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Configure Mosquitto:" -ForegroundColor White
Write-Host "   sudo cp mqtt_broker/mosquitto_tls.conf /etc/mosquitto/conf.d/" -ForegroundColor Gray
Write-Host "   sudo systemctl restart mosquitto" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Copy ca.crt to this Windows machine:" -ForegroundColor White
Write-Host "   Place ca.crt in: raspberry-pi-backend/mqtt_broker/certs/" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Test connection:" -ForegroundColor White
Write-Host "   python check_mqtt_connection.py" -ForegroundColor Gray
Write-Host ""

