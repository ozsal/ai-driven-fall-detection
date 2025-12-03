#!/bin/bash

# Start script for Raspberry Pi Fall Detection System

echo "Starting Fall Detection System..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# SQLite doesn't need a separate service - it's file-based

# Check if Mosquitto MQTT broker is running
if ! pgrep -x "mosquitto" > /dev/null; then
    echo "Starting Mosquitto MQTT broker..."
    mosquitto -d
fi

# Start FastAPI server
echo "Starting FastAPI server..."
cd api
python main.py

