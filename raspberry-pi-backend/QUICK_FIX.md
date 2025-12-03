# Quick Fix for Python 3.13 Compatibility Issue

## Problem
Python 3.13 has compatibility issues with numpy and other packages.

## ⚡ FASTEST SOLUTION (Recommended)

**Just use minimal requirements - works with Python 3.13:**

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements-minimal.txt
```

The system works perfectly without numpy! See `PYTHON_VERSION_FIX.md` for details on installing Python 3.11 if you need ML features.

## Solution Options

### Option 1: Check Available Python Versions (Easiest)

```bash
# Check what Python versions are available
apt-cache search python3 | grep -E "^python3\.[0-9]"

# Or check installed versions
ls /usr/bin/python3*

# Use the highest available version (usually 3.9, 3.10, or 3.11)
python3.10 --version  # Try this
python3.9 --version  # Or this
```

### Option 2: Use System Python (Recommended if 3.9-3.11 available)

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend

# Remove old venv
rm -rf venv

# Create venv with available Python version
# Try these in order:
python3.10 -m venv venv  # If 3.10 available
# OR
python3.9 -m venv venv   # If 3.9 available
# OR
python3 -m venv venv     # Use system default

source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
```

### Option 3: Use Minimal Requirements (No ML Libraries)

If you can't get a compatible Python version, use minimal requirements:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install minimal requirements (no numpy/tensorflow)
pip install -r requirements-minimal.txt
```

**Note**: The fall detection system will work without numpy/tensorflow. The ML features are optional.

### Option 4: Install Python 3.11 from Source (Advanced)

Only if you really need Python 3.11:

```bash
# Install build dependencies
sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
    libsqlite3-dev wget libbz2-dev

# Download Python 3.11
cd /tmp
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar -xf Python-3.11.9.tgz
cd Python-3.11.9

# Configure and build
./configure --enable-optimizations --prefix=/usr/local
make -j$(nproc)
sudo make altinstall

# Use it
python3.11 -m venv ~/ai-driven-fall-detection/raspberry-pi-backend/venv
```

## Recommended: Check Your System First

```bash
# 1. Check current Python version
python3 --version

# 2. Check available Python versions
ls /usr/bin/python3*

# 3. If you have 3.9 or 3.10, use that:
python3.10 -m venv venv  # or python3.9
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## If All Else Fails: Use Minimal Requirements

The system will work fine without numpy/tensorflow:

```bash
pip install -r requirements-minimal.txt
```

The fall detection algorithm uses basic calculations that don't require ML libraries.

