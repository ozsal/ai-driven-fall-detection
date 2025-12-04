#!/bin/bash

echo "Starting Fall Detection Dashboard..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Start Backend API in background
echo "Step 1: Starting Backend API..."
cd raspberry-pi-backend/api
python3 main.py &
BACKEND_PID=$!
cd ../..

# Wait a bit for backend to start
sleep 3

# Start React Dashboard
echo "Step 2: Starting React Dashboard..."
cd web-dashboard/react-app
npm start &
DASHBOARD_PID=$!
cd ../..

echo ""
echo "Both services are starting..."
echo "Backend API: http://localhost:8000"
echo "Dashboard: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"
echo "Backend PID: $BACKEND_PID"
echo "Dashboard PID: $DASHBOARD_PID"

# Wait for user interrupt
trap "kill $BACKEND_PID $DASHBOARD_PID 2>/dev/null; exit" INT TERM
wait

