@echo off
echo ======================================
echo Installing QR Backend Dependencies
echo ======================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install Pillow first (latest version with binary wheel)
echo Step 1: Installing Pillow (using binary wheel)...
pip install Pillow --only-binary=:all:
if %errorlevel% neq 0 (
    echo Warning: Failed to install Pillow with binary wheel
    echo Trying without binary restriction...
    pip install Pillow
)
echo.

REM Install Django and other packages (without djongo first)
echo Step 2: Installing Django and core packages...
pip install Django==4.1.13 djangorestframework==3.14.0 djangorestframework-simplejwt==5.3.0 django-cors-headers==4.3.1 PyJWT==2.8.0 qrcode==7.4.2 python-dotenv==1.0.0 pytz==2023.3 pymongo==3.12.3
if %errorlevel% neq 0 (
    echo Error: Failed to install core packages
    pause
    exit /b 1
)
echo.

REM Install djongo (will manage sqlparse version)
echo Step 3: Installing djongo...
pip install djongo==1.3.6
if %errorlevel% neq 0 (
    echo Warning: djongo installation had issues, but may still work
)
echo.

REM Verify installation
echo ======================================
echo Verifying installation...
echo ======================================
python -m django --version
if %errorlevel% neq 0 (
    echo Error: Django not properly installed
    pause
    exit /b 1
)
echo.

echo ======================================
echo Installation Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Run migrations: python manage.py makemigrations
echo 2. Apply migrations: python manage.py migrate
echo 3. Start server: python manage.py runserver 8000
echo.
pause
