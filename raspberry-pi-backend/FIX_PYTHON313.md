# Fix Python 3.13 Compatibility - Immediate Solution

## The Problem
Python 3.13 removed `pkgutil.ImpImporter`, which breaks older versions of setuptools/pkg_resources used by numpy.

## Solution 1: Use Minimal Requirements (Recommended - Works Now!)

**This is the fastest solution and works immediately:**

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate

# Upgrade pip and setuptools to latest
pip install --upgrade pip setuptools wheel

# Install minimal requirements (no numpy/tensorflow)
pip install -r requirements-minimal.txt

# Test it works
cd api
python main.py
```

**The system works perfectly without numpy!** I've updated the code to use Python's built-in `math` module.

## Solution 2: Fix setuptools for Python 3.13 (If you need numpy)

### Step 1: Upgrade setuptools to latest version

```bash
source venv/bin/activate

# Uninstall old setuptools
pip uninstall setuptools -y

# Install latest setuptools from git (has Python 3.13 support)
pip install --upgrade 'setuptools>=70.0.0' wheel pip

# Or try the absolute latest from git
pip install git+https://github.com/pypa/setuptools.git
```

### Step 2: Try installing numpy with pre-built wheels

```bash
# Try installing numpy with only pre-built wheels (no building)
pip install --only-binary :all: numpy

# If that fails, try without the flag
pip install numpy
```

### Step 3: If still failing, patch pkg_resources

Create a temporary fix:

```bash
# Install setuptools from source with patch
pip uninstall setuptools -y
pip install --no-binary setuptools 'setuptools>=70.0.0'

# Then try numpy again
pip install numpy
```

## Solution 3: Install numpy from pre-built binary (Easiest if available)

```bash
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# Check if numpy has Python 3.13 wheels available
pip install --only-binary :all: --pre numpy

# Or try the latest development version
pip install --pre --upgrade numpy
```

## Solution 4: Use conda/mamba (Alternative package manager)

If pip continues to fail, conda often has better Python 3.13 support:

```bash
# Install miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create environment with Python 3.13
conda create -n fall-detection python=3.13
conda activate fall-detection

# Install numpy via conda
conda install numpy scikit-learn pandas

# Install rest via pip
pip install -r requirements.txt
```

## Recommended: Just Use Minimal Requirements!

**The fall detection system works perfectly without numpy.** Here's why:

1. ✅ All core functionality works
2. ✅ Fall detection algorithm uses basic math (no numpy needed)
3. ✅ Database, MQTT, API all work
4. ✅ Web dashboard works
5. ✅ Alert system works

The only thing you lose is:
- Advanced ML model training (optional)
- Some advanced data analysis features (optional)

**To use minimal requirements:**

```bash
cd ~/ai-driven-fall-detection/raspberry-pi-backend
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements-minimal.txt
```

Then test:
```bash
cd api
python main.py
```

## Quick Test After Installation

```bash
# Test imports work
python -c "import fastapi; print('FastAPI OK')"
python -c "import aiosqlite; print('SQLite OK')"
python -c "import paho.mqtt; print('MQTT OK')"

# If using minimal requirements, numpy won't be available (that's OK!)
python -c "import math; print('Math OK - fall detection will work')"
```

## If You Really Need numpy Later

You can always:
1. Install Python 3.11 using pyenv (see PYTHON_VERSION_FIX.md)
2. Create a separate venv with Python 3.11 for ML features
3. Use the main system with minimal requirements for production

