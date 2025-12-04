# NumPy Version Guide for Fall Detection System

## Recommended NumPy Versions by Python Version

### Python 3.11 (Recommended for Raspberry Pi)
**Best Choice: `numpy==1.26.4`** or `numpy>=1.24.0,<1.27.0`

```bash
pip install numpy==1.26.4
```

**Why:**
- ✅ Fully compatible with Python 3.11
- ✅ Works with scikit-learn 1.3.x and pandas 2.0.x
- ✅ Stable and well-tested
- ✅ Pre-built wheels available for ARM (Raspberry Pi)
- ✅ No build issues

### Python 3.12
**Best Choice: `numpy==1.26.4`** or `numpy>=1.24.0,<1.27.0`

```bash
pip install numpy==1.26.4
```

### Python 3.13
**Best Choice: `numpy>=2.1.0`** (Latest: `numpy==2.1.2`)

```bash
pip install numpy>=2.1.0
# Or specific version
pip install numpy==2.1.2
```

**Important Notes for Python 3.13:**
- ⚠️ NumPy 2.x has breaking changes from 1.x
- ⚠️ Requires scikit-learn 1.5.0+ for compatibility
- ⚠️ Requires pandas 2.2.0+ for compatibility
- ⚠️ May have limited pre-built wheels for ARM (Raspberry Pi)
- ✅ Officially supports Python 3.13

## Compatibility Matrix

| Python Version | NumPy Version | scikit-learn | pandas | Status |
|---------------|---------------|--------------|---------|--------|
| 3.11 | 1.26.4 | 1.3.x - 1.5.x | 2.0.x - 2.2.x | ✅ Best |
| 3.12 | 1.26.4 | 1.3.x - 1.5.x | 2.0.x - 2.2.x | ✅ Good |
| 3.13 | 2.1.0+ | 1.5.0+ | 2.2.0+ | ⚠️ New |

## Updated Requirements for Your Project

### For Python 3.11 (Recommended)

```txt
numpy==1.26.4
scikit-learn>=1.3.0,<1.6.0
pandas>=2.0.0,<2.3.0
```

### For Python 3.13

```txt
numpy>=2.1.0
scikit-learn>=1.5.0
pandas>=2.2.0
```

## Installation Commands

### Python 3.11 Setup

```bash
# Install in order for best compatibility
pip install --upgrade pip setuptools wheel
pip install numpy==1.26.4
pip install scikit-learn==1.3.2
pip install pandas==2.1.4
pip install -r requirements.txt
```

### Python 3.13 Setup

```bash
# Install in order for best compatibility
pip install --upgrade pip setuptools wheel
pip install numpy>=2.1.0
pip install scikit-learn>=1.5.0
pip install pandas>=2.2.0
pip install -r requirements.txt
```

## Raspberry Pi Specific Considerations

### ARM Architecture (Raspberry Pi)

**For Python 3.11:**
- NumPy 1.26.4 has pre-built wheels for ARM
- Fast installation, no compilation needed

**For Python 3.13:**
- NumPy 2.1.0+ may need compilation on ARM
- Installation takes longer
- May require build tools: `sudo apt-get install build-essential python3-dev`

### Recommended Approach for Raspberry Pi

1. **Use Python 3.11** (easiest)
   ```bash
   pip install numpy==1.26.4
   ```

2. **If stuck with Python 3.13:**
   ```bash
   # Try pre-built wheels first
   pip install --only-binary :all: numpy>=2.1.0
   
   # If that fails, install build dependencies
   sudo apt-get install build-essential python3-dev
   pip install numpy>=2.1.0
   ```

## Testing NumPy Installation

```bash
# Test import
python -c "import numpy as np; print(f'NumPy version: {np.__version__}')"

# Test basic functionality
python -c "import numpy as np; arr = np.array([1,2,3]); print(f'NumPy works: {arr.sum()}')"

# Test with scikit-learn
python -c "import numpy as np; from sklearn.ensemble import RandomForestClassifier; print('All OK')"
```

## Troubleshooting

### Issue: NumPy installation fails

**Solution:**
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install build dependencies (Raspberry Pi)
sudo apt-get install build-essential python3-dev

# Try again
pip install numpy==1.26.4  # For Python 3.11
# OR
pip install numpy>=2.1.0  # For Python 3.13
```

### Issue: Version conflicts with scikit-learn

**Solution:**
```bash
# Install compatible versions together
pip install numpy==1.26.4 scikit-learn==1.3.2 pandas==2.1.4
```

### Issue: NumPy 2.x breaking changes

If you upgrade to NumPy 2.x, you may need to update code:
- Some deprecated functions removed
- Type system changes
- See: https://numpy.org/devdocs/numpy_2_0_migration_guide.html

## Current Project Status

Your project is **already compatible** with both approaches:

1. **Without NumPy** (current minimal setup)
   - Fall detection works using Python's `math` module
   - No ML training features
   - ✅ Works on Python 3.13

2. **With NumPy** (full features)
   - ML model training
   - Advanced data analysis
   - ✅ Best with Python 3.11 + NumPy 1.26.4

## Recommendation Summary

**For Raspberry Pi:**
- ✅ **Best**: Python 3.11 + NumPy 1.26.4
- ⚠️ **Alternative**: Python 3.13 + NumPy 2.1.0+ (if you must use 3.13)
- ✅ **Simplest**: Use minimal requirements (no NumPy needed)

**For Development/Testing:**
- Python 3.11 + NumPy 1.26.4 (most stable)
- Python 3.12 + NumPy 1.26.4 (also good)



