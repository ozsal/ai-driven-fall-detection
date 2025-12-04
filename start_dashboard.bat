@echo off
echo Starting Fall Detection Dashboard...
echo.

echo Step 1: Starting Backend API...
start "Backend API" cmd /k "cd raspberry-pi-backend\api && python main.py"

timeout /t 3 /nobreak >nul

echo Step 2: Starting React Dashboard...
start "React Dashboard" cmd /k "cd web-dashboard\react-app && npm start"

echo.
echo Both services are starting...
echo Backend API: http://localhost:8000
echo Dashboard: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul

