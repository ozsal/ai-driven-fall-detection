# Authentication System Setup Guide

## Overview

The Fall Detection System now includes a complete authentication and authorization system with:
- User login with username and password
- JWT-based access tokens
- Role-based access control (admin, viewer, sensor_manager)
- Admin user management
- Protected API endpoints

## User Roles

1. **admin** - Full access:
   - Manage users (create, update, delete)
   - Manage user roles
   - View all data
   - Update sensor status

2. **sensor_manager** - Sensor management:
   - View all data
   - Manage sensors and devices
   - Cannot manage users

3. **viewer** - Read-only access:
   - View sensor readings
   - View fall events
   - View statistics
   - Cannot modify anything

## Default Admin User

On first run, a default admin user is automatically created:
- **Username:** `admin` (or set via `DEFAULT_ADMIN_USERNAME` env var)
- **Password:** `admin123` (or set via `DEFAULT_ADMIN_PASSWORD` env var)
- **Email:** `admin@fall-detection.local` (or set via `DEFAULT_ADMIN_EMAIL` env var)

⚠️ **IMPORTANT:** Change the default password immediately after first login!

## Installation

### 1. Install Dependencies

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate
pip install PyJWT==2.8.0 bcrypt==4.1.2
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Set JWT Secret Key (Optional)

For production, set a secure JWT secret key:

```bash
# In .env file or environment
export JWT_SECRET_KEY="your-very-secure-secret-key-here"
```

If not set, a default key is used (not recommended for production).

### 3. Restart Backend

The database will automatically create the `auth_users` table and default admin user on first run.

```bash
# If using systemd service
sudo systemctl restart fall-detection

# Or manually
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate
cd api
python main.py
```

## API Endpoints

### Authentication Endpoints

#### Login
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```bash
GET /auth/me
Authorization: Bearer <access_token>
```

#### Register New User (Admin Only)
```bash
POST /auth/register
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword",
  "role": "viewer"
}
```

#### List All Users (Admin Only)
```bash
GET /auth/users
Authorization: Bearer <admin_token>
```

#### Update User (Admin Only)
```bash
PUT /auth/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "role": "sensor_manager",
  "is_active": true
}
```

#### Delete User (Admin Only)
```bash
DELETE /auth/users/{user_id}
Authorization: Bearer <admin_token>
```

### Protected API Endpoints

All API endpoints now require authentication. Include the access token in the Authorization header:

```bash
Authorization: Bearer <access_token>
```

**Protected Endpoints:**
- `GET /api/sensor-readings` - Requires viewer or above
- `GET /api/devices` - Requires viewer or above
- `GET /api/fall-events` - Requires viewer or above
- `GET /api/statistics` - Requires viewer or above
- `GET /api/sensors/pir` - Requires viewer or above
- `GET /api/sensors/ultrasonic` - Requires viewer or above
- `GET /api/sensors/dht22` - Requires viewer or above
- `PUT /api/sensors/{device_id}/{sensor_type}/status` - Requires admin

## Usage Examples

### 1. Login and Get Token

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Save token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')
```

### 2. Access Protected Endpoint

```bash
# Get sensor readings
curl -X GET "http://localhost:8000/api/sensor-readings" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Create New User (Admin)

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

### 4. Update User Role (Admin)

```bash
curl -X PUT "http://localhost:8000/auth/users/2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "sensor_manager"
  }'
```

## Frontend Integration

### Login Flow

1. User submits login form with username and password
2. Frontend sends POST to `/auth/login` with form data
3. Backend returns access token
4. Frontend stores token (localStorage, sessionStorage, or httpOnly cookie)
5. Frontend includes token in all API requests: `Authorization: Bearer <token>`

### Example Frontend Code

```javascript
// Login
async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
}

// Make authenticated request
async function getSensorReadings() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/sensor-readings', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

## Token Expiration

Access tokens expire after **24 hours** by default. After expiration:
1. User must login again to get a new token
2. Frontend should handle 401 errors and redirect to login

## Security Notes

1. **JWT Secret Key**: Change the default secret key in production
2. **HTTPS**: Use HTTPS in production to protect tokens in transit
3. **Token Storage**: Store tokens securely (httpOnly cookies recommended)
4. **Password Policy**: Enforce strong passwords (currently minimum 6 characters)
5. **Default Admin**: Change default admin password immediately

## Troubleshooting

### "Could not validate credentials"
- Token expired or invalid
- Token not included in request
- Token format incorrect

**Solution:** Login again to get a new token

### "User account is inactive"
- User account has been deactivated by admin

**Solution:** Admin must reactivate the account

### "Access denied"
- User doesn't have required role for the endpoint

**Solution:** Admin must update user role

### "User not found"
- Token references a user that no longer exists

**Solution:** Login again

## Database Schema

The `auth_users` table structure:

```sql
CREATE TABLE auth_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Environment Variables

Optional environment variables:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here

# Default Admin User (only used on first run)
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_EMAIL=admin@fall-detection.local
```

## Next Steps

1. **Change Default Admin Password:**
   ```bash
   # Login as admin, then update password via API
   curl -X PUT "http://localhost:8000/auth/users/1" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"password": "new-secure-password"}'
   ```

2. **Create Additional Users:**
   - Use the `/auth/register` endpoint (admin only)
   - Or use the admin interface (if implemented)

3. **Update Frontend:**
   - Add login page
   - Store and send access tokens
   - Handle authentication errors
   - Redirect to login on 401 errors

