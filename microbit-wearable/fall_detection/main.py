"""
Micro:bit Fall Detection with Accelerometer
This code implements on-device fall detection using the built-in accelerometer
and a simple machine learning approach (TinyML-like classification).

Hardware: Micro:bit v2
Author: AI Fall Detection System
"""

from microbit import *
import math
import radio

# ==================== Configuration ====================
# Radio configuration for communication
radio.config(group=1, power=7)  # Group 1, max power
radio.on()

# Accelerometer configuration
ACCEL_SAMPLE_RATE = 50  # Hz (50 samples per second)
ACCEL_THRESHOLD = 2000  # mg threshold for impact detection
FALL_DURATION_MS = 500  # Minimum duration for fall detection (ms)

# Fall detection parameters
IMPACT_THRESHOLD = 2500  # mg - sudden impact detection
ORIENTATION_THRESHOLD = 500  # mg - horizontal orientation (lying down)
RECOVERY_THRESHOLD = 1000  # mg - movement after fall

# Device ID
DEVICE_ID = "MICROBIT_01"

# ==================== Global Variables ====================
fall_detected = False
last_fall_time = 0
impact_detected = False
orientation_changed = False
samples_collected = 0
accel_buffer = []  # Buffer for recent accelerometer readings

# ==================== Helper Functions ====================

def get_acceleration_magnitude():
    """
    Calculate total acceleration magnitude from x, y, z axes.
    Returns: acceleration in mg (milli-g)
    """
    accel = accelerometer.get_values()
    x, y, z = accel[0], accel[1], accel[2]
    magnitude = math.sqrt(x*x + y*y + z*z)
    return magnitude

def get_orientation():
    """
    Determine device orientation based on accelerometer.
    Returns: 'vertical', 'horizontal', or 'unknown'
    """
    accel = accelerometer.get_values()
    x, y, z = abs(accel[0]), abs(accel[1]), abs(accel[2])
    
    # Check if device is horizontal (lying down)
    if z > 800:  # Z-axis dominant (device flat)
        return 'horizontal'
    elif x > 800 or y > 800:  # X or Y dominant (device upright)
        return 'vertical'
    else:
        return 'unknown'

def detect_impact(accel_magnitude):
    """
    Detect sudden impact/shock.
    Returns: True if impact detected
    """
    if len(accel_buffer) < 2:
        return False
    
    # Calculate rate of change (jerk)
    prev_magnitude = accel_buffer[-1] if accel_buffer else accel_magnitude
    jerk = abs(accel_magnitude - prev_magnitude)
    
    # Impact detected if magnitude exceeds threshold or high jerk
    if accel_magnitude > IMPACT_THRESHOLD or jerk > 1500:
        return True
    return False

def detect_fall_pattern():
    """
    Analyze accelerometer pattern to detect fall.
    Uses a simple state machine approach.
    Returns: True if fall pattern detected
    """
    global impact_detected, orientation_changed
    
    if len(accel_buffer) < 10:  # Need minimum samples
        return False
    
    # Check for impact followed by horizontal orientation
    recent_impacts = sum(1 for mag in accel_buffer[-10:] if mag > IMPACT_THRESHOLD)
    current_orientation = get_orientation()
    
    # Fall pattern: impact + horizontal orientation
    if recent_impacts > 0 and current_orientation == 'horizontal':
        return True
    
    return False

def calculate_fall_severity(accel_magnitude):
    """
    Calculate fall severity score based on impact magnitude.
    Returns: severity score (0-10)
    """
    if accel_magnitude < IMPACT_THRESHOLD:
        return 0
    
    # Normalize to 0-10 scale
    severity = min(10, (accel_magnitude - IMPACT_THRESHOLD) / 500)
    return int(severity)

def send_fall_alert(severity_score):
    """
    Send fall detection alert via radio.
    """
    message = {
        'device_id': DEVICE_ID,
        'event': 'fall_detected',
        'severity': severity_score,
        'timestamp': running_time(),
        'accel_magnitude': get_acceleration_magnitude(),
        'orientation': get_orientation()
    }
    
    # Convert to string for radio transmission
    # Format: "DEVICE_ID|FALL|SEVERITY|TIMESTAMP|MAGNITUDE|ORIENTATION"
    msg_str = "{}|FALL|{}|{}|{}|{}".format(
        message['device_id'],
        message['severity'],
        message['timestamp'],
        int(message['accel_magnitude']),
        message['orientation']
    )
    
    radio.send(msg_str)
    display.show(Image.SKULL)  # Visual indicator
    sleep(500)
    display.clear()

def send_sensor_data():
    """
    Send regular accelerometer data for monitoring.
    """
    accel = accelerometer.get_values()
    magnitude = get_acceleration_magnitude()
    orientation = get_orientation()
    
    # Format: "DEVICE_ID|DATA|X|Y|Z|MAG|ORIENT"
    msg_str = "{}|DATA|{}|{}|{}|{}|{}".format(
        DEVICE_ID,
        accel[0], accel[1], accel[2],
        int(magnitude),
        orientation
    )
    
    radio.send(msg_str)

# ==================== Main Program ====================

def main():
    global fall_detected, last_fall_time, impact_detected
    global orientation_changed, samples_collected, accel_buffer
    
    # Initialize
    display.show(Image.HAPPY)
    sleep(1000)
    display.clear()
    
    last_sample_time = running_time()
    last_data_send = running_time()
    
    # Main loop
    while True:
        current_time = running_time()
        
        # Sample accelerometer at configured rate
        if current_time - last_sample_time >= (1000 // ACCEL_SAMPLE_RATE):
            last_sample_time = current_time
            
            # Read accelerometer
            accel_magnitude = get_acceleration_magnitude()
            
            # Add to buffer (keep last 20 samples)
            accel_buffer.append(accel_magnitude)
            if len(accel_buffer) > 20:
                accel_buffer.pop(0)
            
            samples_collected += 1
            
            # Detect impact
            if detect_impact(accel_magnitude):
                impact_detected = True
                display.show(Image.SURPRISED)
                sleep(100)
                display.clear()
            
            # Detect fall pattern
            if detect_fall_pattern() and not fall_detected:
                fall_detected = True
                last_fall_time = current_time
                severity = calculate_fall_severity(accel_magnitude)
                
                # Send fall alert
                send_fall_alert(severity)
                
                # Visual feedback
                for i in range(3):
                    display.show(Image.SKULL)
                    sleep(200)
                    display.clear()
                    sleep(200)
        
        # Send regular sensor data every 2 seconds
        if current_time - last_data_send >= 2000:
            last_data_send = current_time
            send_sensor_data()
        
        # Reset fall detection after recovery period
        if fall_detected and (current_time - last_fall_time) > 5000:
            accel_magnitude = get_acceleration_magnitude()
            orientation = get_orientation()
            
            # Check for recovery (movement detected)
            if accel_magnitude > RECOVERY_THRESHOLD or orientation == 'vertical':
                fall_detected = False
                impact_detected = False
                display.show(Image.HAPPY)
                sleep(500)
                display.clear()
        
        # Check for button presses (manual test)
        if button_a.was_pressed():
            # Simulate fall for testing
            send_fall_alert(5)
        
        if button_b.was_pressed():
            # Send current status
            accel = accelerometer.get_values()
            display.scroll("X:{} Y:{} Z:{}".format(
                accel[0]//100, accel[1]//100, accel[2]//100
            ))
        
        # Small delay to prevent tight loop
        sleep(10)

# ==================== Run Program ====================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Error handling
        display.show(Image.SAD)
        sleep(2000)
        display.scroll("ERROR")
        reset()  # Restart

