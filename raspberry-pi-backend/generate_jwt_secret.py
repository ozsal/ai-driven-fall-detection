#!/usr/bin/env python3
"""
Generate a secure JWT secret key for authentication
"""

import secrets
import os

def generate_jwt_secret():
    """Generate a secure random JWT secret key"""
    secret_key = secrets.token_urlsafe(32)
    return secret_key

def create_env_file(secret_key):
    """Create or update .env file with JWT secret key"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env_example_path = os.path.join(os.path.dirname(__file__), ".env.example")
    
    # Check if .env already exists
    env_exists = os.path.exists(env_path)
    
    if env_exists:
        # Read existing .env file
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Check if JWT_SECRET_KEY already exists
        if 'JWT_SECRET_KEY=' in content:
            # Update existing key
            lines = content.split('\n')
            updated_lines = []
            for line in lines:
                if line.startswith('JWT_SECRET_KEY='):
                    updated_lines.append(f'JWT_SECRET_KEY={secret_key}')
                else:
                    updated_lines.append(line)
            content = '\n'.join(updated_lines)
        else:
            # Add JWT_SECRET_KEY at the beginning
            content = f'JWT_SECRET_KEY={secret_key}\n' + content
        
        # Write updated content
        with open(env_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated existing .env file with new JWT secret key")
    else:
        # Create new .env file from .env.example if it exists
        if os.path.exists(env_example_path):
            with open(env_example_path, 'r') as f:
                content = f.read()
            # Replace placeholder with actual key
            content = content.replace('your-secret-key-here-change-this-in-production', secret_key)
        else:
            # Create basic .env file
            content = f"""# JWT Authentication Configuration
JWT_SECRET_KEY={secret_key}

# Default Admin User (only used on first run if no users exist)
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_EMAIL=admin@fall-detection.local

# MQTT Broker Configuration
MQTT_BROKER_HOST=10.162.131.191
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
        
        with open(env_path, 'w') as f:
            f.write(content)
        print(f"✅ Created new .env file with JWT secret key")
    
    print(f"\n🔑 JWT Secret Key: {secret_key}")
    print(f"📁 Saved to: {env_path}")
    print(f"\n⚠️  IMPORTANT: Keep this key secret! Do not commit .env to git.")
    print(f"   The .env file is already in .gitignore for security.")

if __name__ == "__main__":
    print("=" * 60)
    print("JWT Secret Key Generator")
    print("=" * 60)
    print()
    
    secret_key = generate_jwt_secret()
    create_env_file(secret_key)
    
    print()
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the .env file and update other settings if needed")
    print("2. Restart the backend server to use the new secret key")
    print("3. The JWT secret key will be used for all authentication tokens")

