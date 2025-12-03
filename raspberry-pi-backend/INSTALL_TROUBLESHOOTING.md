# Installation Troubleshooting Guide

## Python Version Issues

### Problem: Error installing numpy/tensorflow on Python 3.13

**Error**: `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`

**Solution**: 
1. **Use Python 3.11 or earlier** (recommended for Raspberry Pi)
   ```bash
   # Check Python version
   python3 --version
   
   # If Python 3.13, install Python 3.11:
   sudo apt-get install python3.11 python3.11-venv python3.11-pip
   
   # Create venv with Python 3.11
   python3.11 -m venv venv
   source venv/bin/activate
   ```

2. **Upgrade pip, setuptools, and wheel first**:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. **Install numpy separately before other packages**:
   ```bash
   pip install numpy==1.24.3
   pip install -r requirements.txt
   ```

### Problem: TensorFlow installation fails on Raspberry Pi

**Solution**: 
- TensorFlow is optional for basic fall detection
- Use minimal requirements instead:
  ```bash
  pip install -r requirements-minimal.txt
  ```
- The fall detection algorithm will work without TensorFlow
- For advanced ML, consider TensorFlow Lite:
  ```bash
  pip install tflite-runtime
  ```

## Package Installation Issues

### Problem: `pip` command not found

**Solution**:
```bash
sudo apt-get update
sudo apt-get install python3-pip
```

### Problem: Permission denied errors

**Solution**: Use virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Out of memory during installation

**Solution**: 
- Increase swap space temporarily
- Install packages one at a time
- Use minimal requirements

### Problem: SSL certificate errors

**Solution**:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

## System-Specific Issues

### Raspberry Pi 4 (32-bit)

- Use Python 3.9 or 3.10
- Some packages may need ARM-specific wheels
- Consider using 64-bit OS for better compatibility

### Raspberry Pi 4 (64-bit)

- Better package compatibility
- Can use Python 3.10 or 3.11
- TensorFlow may work better

## Alternative Installation Methods

### Method 1: Install packages individually

```bash
pip install fastapi uvicorn paho-mqtt aiosqlite python-dotenv
pip install pydantic pydantic-settings
pip install aiofiles python-multipart email-validator
pip install jinja2 aiosmtplib python-jose[cryptography]
pip install passlib[bcrypt] websockets
# Skip numpy/tensorflow if not needed
```

### Method 2: Use pre-built wheels

```bash
pip install --only-binary :all: numpy pandas scikit-learn
```

### Method 3: Build from source (slow but works)

```bash
pip install --no-binary :all: numpy
```

## Verification

After installation, verify everything works:

```bash
# Test imports
python3 -c "import fastapi; import aiosqlite; import paho.mqtt; print('OK')"

# Test database
python3 -c "import aiosqlite; print('SQLite OK')"

# Test API (if installed)
python3 -c "from fastapi import FastAPI; print('FastAPI OK')"
```

## Getting Help

If issues persist:
1. Check Python version: `python3 --version`
2. Check pip version: `pip --version`
3. Check system architecture: `uname -m`
4. Review full error messages
5. Try minimal requirements first

## Recommended Setup for Raspberry Pi

```bash
# 1. Use Python 3.11 (or 3.10)
sudo apt-get install python3.11 python3.11-venv python3.11-pip

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install minimal requirements first
pip install -r requirements-minimal.txt

# 5. Test basic functionality
cd api
python main.py

# 6. If needed, add ML libraries later
pip install numpy scikit-learn pandas
```

