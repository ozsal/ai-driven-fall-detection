# JWT Secret Key Setup Guide

## Quick Setup

Run the automated script to generate and configure your JWT secret key:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
python generate_jwt_secret.py
```

This will:
- ✅ Generate a secure random JWT secret key
- ✅ Create or update `.env` file with the key
- ✅ Keep your existing `.env` settings intact

## Manual Setup

### Option 1: Generate Key Using Python

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and add it to your `.env` file:

```bash
echo "JWT_SECRET_KEY=your-generated-key-here" >> .env
```

### Option 2: Create .env File from Template

```bash
cp .env.example .env
# Then edit .env and replace the placeholder with a secure key
nano .env
```

## Verify Setup

Check that your `.env` file contains the JWT secret key:

```bash
grep JWT_SECRET_KEY .env
```

You should see:
```
JWT_SECRET_KEY=some-long-random-string-here
```

## Security Notes

1. **Never commit `.env` to git** - It's already in `.gitignore`
2. **Use a strong random key** - At least 32 characters
3. **Keep it secret** - Don't share the key with anyone
4. **Change it if compromised** - Generate a new key if you suspect it's been exposed

## What Happens Without a Key?

If `JWT_SECRET_KEY` is not set, the system uses a default key:
```
"your-secret-key-change-this-in-production"
```

⚠️ **This is insecure!** Always set a proper secret key in production.

## After Setup

1. **Restart the backend** to load the new secret key:
   ```bash
   # If using systemd
   sudo systemctl restart fall-detection
   
   # Or manually
   cd ~/ai-driven-fall-detection/raspberry-pi-backend
   source venv/bin/activate
   cd api
   python main.py
   ```

2. **Test authentication**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

## Regenerating the Key

If you need to regenerate the key (e.g., after a security incident):

1. **Run the generator script again**:
   ```bash
   python generate_jwt_secret.py
   ```

2. **Important**: All existing JWT tokens will become invalid!
   - Users will need to login again
   - Any stored tokens in frontend will stop working

3. **Restart the backend** to apply the new key

## Environment Variables

The JWT secret key is loaded from:
- `.env` file (if present)
- Environment variable `JWT_SECRET_KEY`
- Default value (not recommended)

Priority: `.env` file > Environment variable > Default

