@echo off
echo Starting EchoCheck Suite Development Servers
echo ===========================================

echo.
echo Starting Backend Server...
start "EchoCheck Backend" cmd /k "cd server && npm run dev"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend Server...
start "EchoCheck Frontend" cmd /k "cd client && npm start"

echo.
echo Both servers are starting...
echo.
echo Backend: http://localhost:8080
echo Frontend: http://localhost:8000
echo.

echo Waiting 15 seconds for servers to fully start...
timeout /t 15 /nobreak > nul

echo.
echo Launching browser...
start http://localhost:8000

echo.
echo EchoCheck Suite is now running!
echo - Backend: http://localhost:8080
echo - Frontend: http://localhost:8000 (opened in browser)
echo.
echo Press any key to exit this window...
pause > nul
