# Micro:bit Fall Detection Wearable

This code implements fall detection on the Micro:bit v2 using the built-in accelerometer.

## Features

- Real-time accelerometer monitoring (50Hz)
- Impact detection using magnitude and jerk analysis
- Orientation-based fall verification
- Fall severity scoring (0-10)
- Radio communication for alerts
- Visual feedback via LED matrix

## Important Note About Linter Warnings

**The linter warnings you see are EXPECTED and can be safely ignored!**

The Micro:bit code uses device-specific modules (`microbit`, `radio`) and functions (`accelerometer`, `display`, `sleep`, `button_a`, etc.) that are only available when running on a Micro:bit device or in Micro:bit Python environments (MakeCode, Mu Editor).

These functions are provided by the Micro:bit runtime and are not available in standard Python environments, which is why your IDE's linter shows warnings. The code will work perfectly when flashed to a Micro:bit device.

Configuration files (`.pylintrc`, `pyrightconfig.json`) have been added to suppress these warnings in your IDE.

## Installation

### Option 1: MakeCode (Recommended for beginners)

1. Go to [makecode.microbit.org](https://makecode.microbit.org)
2. Create a new project
3. Switch to Python mode
4. Copy the code from `main.py`
5. Download and flash to Micro:bit

### Option 2: MicroPython

1. Install [Mu Editor](https://codewith.mu/) or use online editor
2. Connect Micro:bit via USB
3. Copy `main.py` code
4. Flash to device

## Usage

- **Normal Operation**: Device monitors accelerometer continuously
- **Fall Detected**: Shows skull icon and sends radio alert
- **Button A**: Manual test (simulates fall)
- **Button B**: Display current accelerometer values

## Radio Communication

The device sends two types of messages:

1. **Fall Alert**: `DEVICE_ID|FALL|SEVERITY|TIMESTAMP|MAGNITUDE|ORIENTATION`
2. **Sensor Data**: `DEVICE_ID|DATA|X|Y|Z|MAGNITUDE|ORIENTATION`

## Configuration

Edit these parameters in `main.py`:

- `ACCEL_SAMPLE_RATE`: Sampling frequency (default: 50Hz)
- `IMPACT_THRESHOLD`: Impact detection threshold (default: 2500mg)
- `ORIENTATION_THRESHOLD`: Orientation change threshold
- `DEVICE_ID`: Unique device identifier

## Testing

1. Hold Micro:bit and drop it (safely) onto a soft surface
2. Watch for skull icon and alert
3. Check radio receiver for message
4. Use Button A for manual testing

## Advanced: TinyML Integration

For more accurate detection, you can train a TinyML model:

1. Collect accelerometer data for falls and normal activities
2. Train model using TensorFlow Lite
3. Convert to Micro:bit-compatible format
4. Integrate model inference in the code

See `ml_training/` directory for training scripts.

