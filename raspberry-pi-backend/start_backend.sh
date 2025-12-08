#!/bin/bash
# Bash script to start the backend server
# Run this script to start the FastAPI backend

echo "Starting Fall Detection Backend Server..."
echo ""

# Change to the api directory
cd "$(dirname "$0")/api"

# Check if virtual environment exists
if [ -f "../venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "Warning: Virtual environment not found. Using system Python."
fi

# Set environment variables
export API_HOST=0.0.0.0
export API_PORT=8000

echo "Starting server on http://0.0.0.0:8000"
echo "API will be accessible at:"
echo "  - http://localhost:8000"
echo "  - http://10.162.131.191:8000"
echo ""

# Start the server
python main.py




