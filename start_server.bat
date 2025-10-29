@echo off
REM Quick start script for QR Access Verification System
REM This script activates the virtual environment and starts the Django server

echo.
echo ================================================
echo   QR Access Verification System - Server Start
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if MongoDB is running (optional - will continue anyway)
echo [2/3] Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000).admin.command('ping')" 2>nul
if errorlevel 1 (
    echo [WARNING] MongoDB is not running or not accessible!
    echo Please start MongoDB with: net start MongoDB
    echo.
)

REM Start Django server
echo [3/3] Starting Django development server...
echo.
echo Server will be available at: http://localhost:8000
echo Press CTRL+C to stop the server
echo.
python manage.py runserver

pause
