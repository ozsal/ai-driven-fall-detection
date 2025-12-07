# Authentication Quick Start Guide

## Installation

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate
pip install PyJWT==2.8.0 bcrypt==4.1.2
```

## Default Login

On first run, a default admin user is created:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Change this password immediately!**

## Quick Test

### 1. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 2. Save Token
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 3. Access Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/sensor-readings" \
  -H "Authorization: Bearer $TOKEN"
```

## User Roles

- **admin** - Full access (manage users, view all data)
- **sensor_manager** - Manage sensors, view data
- **viewer** - Read-only access

## Create New User (Admin Only)

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "viewer1",
    "email": "viewer1@example.com",
    "password": "viewer123",
    "role": "viewer"
  }'
```

## Change Default Admin Password

```bash
# First, get your user ID
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# Then update password (replace USER_ID with your ID, usually 1)
curl -X PUT "http://localhost:8000/auth/users/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "new-secure-password"}'
```

## Protected Endpoints

All `/api/*` endpoints now require authentication. Include token in header:
```
Authorization: Bearer <your-token>
```

## See Full Documentation

See `AUTHENTICATION_SETUP.md` for complete documentation.

