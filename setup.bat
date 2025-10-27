@echo off
echo EchoCheck Suite Setup
echo ====================

echo.
echo Installing Node.js dependencies...
call npm install
cd server
call npm install
cd ..\client
call npm install
cd ..

echo.
echo Installing Python dependencies...
cd python
pip install -r requirements.txt
cd ..

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. Start the backend: cd server && npm run dev
echo 2. Start the frontend: cd client && npm start
echo.
echo The application will be available at:
echo - Frontend: http://localhost:8000
echo - Backend: http://localhost:8080
echo.
pause
