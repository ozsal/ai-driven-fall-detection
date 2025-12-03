# Fixing Python 3.13 Compatibility Issues

## Option 1: Install Python 3.11 (Recommended)

### Method A: Install from deadsnakes PPA (Ubuntu/Debian)

```bash
# Add deadsnakes PPA (has older Python versions)
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

# Install Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify installation
python3.11 --version
```

### Method B: Build Python 3.11 from Source

```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev \
    libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
    libsqlite3-dev wget libbz2-dev liblzma-dev

# Download Python 3.11.9 (latest 3.11.x)
cd /tmp
wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
tar -xf Python-3.11.9.tgz
cd Python-3.11.9

# Configure (optimized build)
./configure --enable-optimizations --prefix=/usr/local \
    --with-ensurepip=install

# Build (this takes 10-30 minutes)
make -j$(nproc)

# Install (don't use make install, use altinstall to keep system Python)
sudo make altinstall

# Verify
python3.11 --version
/usr/local/bin/python3.11 --version

# Install pip if not included
python3.11 -m ensurepip --upgrade
```

### Method C: Use pyenv (Easiest for managing multiple versions)

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to shell profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Install Python 3.11.9
pyenv install 3.11.9

# Set as local version for project
cd ~/ai-driven-fall-detection/raspberry-pi-backend
pyenv local 3.11.9

# Verify
python --version  # Should show 3.11.9
```

## Option 2: Fix Python 3.13 Compatibility

### Method A: Upgrade setuptools and use compatible packages

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate

# Upgrade build tools to latest versions
pip install --upgrade pip setuptools wheel

# Install numpy from pre-built wheels (if available)
pip install --only-binary :all: numpy

# If that fails, try installing numpy from source with newer setuptools
pip install --no-binary :all: --upgrade setuptools numpy

# Then install rest of requirements
pip install -r requirements.txt
```

### Method B: Use development versions of packages

```bash
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# Try installing latest development versions
pip install --pre numpy
pip install --pre scikit-learn

# Or install from git (if available)
# pip install git+https://github.com/numpy/numpy.git
```

### Method C: Patch setuptools/pkg_resources (Temporary Fix)

This is a workaround for the `pkgutil.ImpImporter` error:

```bash
source venv/bin/activate

# Install patched setuptools
pip install --upgrade 'setuptools>=70.0.0'

# Or use setuptools from git
pip install git+https://github.com/pypa/setuptools.git
```

## Option 3: Use Minimal Requirements (Easiest - No Downgrade Needed)

This works with Python 3.13 and doesn't require numpy:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install minimal requirements (no numpy/tensorflow)
pip install -r requirements-minimal.txt

# Test the system
cd api
python main.py
```

**Note**: The fall detection system works perfectly without numpy. I've updated the code to use Python's built-in `math` module instead.

## Recommended Approach

**For Raspberry Pi**: Use **Option 3 (Minimal Requirements)** - it's the fastest and works with Python 3.13.

**If you need ML features later**: Use **Option 1 Method C (pyenv)** to install Python 3.11 alongside 3.13.

## After Installing Python 3.11

If you successfully install Python 3.11:

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend

# Remove old venv
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
```

## Verify Installation

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Test imports
python -c "import numpy; print('numpy OK')"
python -c "import fastapi; print('fastapi OK')"
python -c "import aiosqlite; print('sqlite OK')"
```

## Troubleshooting

### If deadsnakes PPA doesn't work:
- Your distribution might not support it
- Try building from source (Method B) or use pyenv (Method C)

### If build from source fails:
- Check you have all build dependencies installed
- Try without `--enable-optimizations` flag (faster build)
- Use pyenv instead (easier)

### If pyenv installation fails:
- Make sure you have git installed: `sudo apt-get install git`
- Check your shell (bash/zsh) is properly configured

## Quick Decision Guide

- **Want fastest solution?** → Use Option 3 (Minimal Requirements)
- **Need full ML features?** → Use Option 1 Method C (pyenv)
- **Have time to build?** → Use Option 1 Method B (Build from source)
- **Using Ubuntu/Debian?** → Try Option 1 Method A (deadsnakes PPA)

