# Authentication Quick Start Guide

## Installation

```bash
cd raspberry-pi-backend
pip install PyJWT==2.8.0 bcrypt==4.1.2 python-multipart==0.0.6
```

## Default Admin Credentials

After starting the backend, a default admin user is automatically created:

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

⚠️ **Change this password immediately in production!**

## Quick Test

### 1. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Use Token
```bash
TOKEN="your_token_here"
curl -X GET "http://localhost:8000/api/devices" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Current User
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

## All Endpoints Now Require Authentication

All `/api/*` endpoints now require a valid JWT token in the Authorization header.

See `AUTHENTICATION_SETUP.md` for complete documentation.

