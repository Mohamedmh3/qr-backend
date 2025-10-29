@echo off
echo ======================================
echo   QR Backend - Database Reset & Fix
echo ======================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Reset migrations
echo Step 1: Resetting migrations...
python manage.py migrate --fake-initial
if %errorlevel% neq 0 (
    echo Warning: Migration reset had issues, continuing...
)
echo.

REM Clear existing migration files
echo Step 2: Clearing old migrations...
if exist users\migrations\0001_initial.py del users\migrations\0001_initial.py
if exist users\migrations\__pycache__ rmdir /s /q users\migrations\__pycache__
echo.

REM Create fresh migrations
echo Step 3: Creating fresh migrations...
python manage.py makemigrations users
if %errorlevel% neq 0 (
    echo ERROR: Failed to create migrations
    pause
    exit /b 1
)
echo.

REM Apply migrations
echo Step 4: Applying migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to apply migrations
    pause
    exit /b 1
)
echo.

REM Clear media files
echo Step 5: Clearing old QR codes...
if exist media\qr_codes rmdir /s /q media\qr_codes
if not exist media mkdir media
if not exist media\qr_codes mkdir media\qr_codes
echo.

REM Run debug tests
echo Step 6: Running debug tests...
python debug_qr.py
if %errorlevel% neq 0 (
    echo Warning: Debug tests had issues, continuing...
)
echo.

REM Create admin user
echo Step 7: Creating admin user...
python manage.py shell -c "
from users.models import User
from django.contrib.auth import get_user_model

User = get_user_model()
try:
    if not User.objects.filter(email='admin@example.com').exists():
        admin = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='Admin123!',
            role='admin'
        )
        print('✅ Admin user created successfully!')
        print(f'   Email: admin@example.com')
        print(f'   Password: Admin123!')
        print(f'   QR ID: {admin.qr_id}')
    else:
        print('ℹ️  Admin user already exists')
except Exception as e:
    print(f'❌ Error creating admin user: {e}')
"
echo.

echo ======================================
echo Setup Complete!
echo.
echo Next steps:
echo 1. Start server: python manage.py runserver 8000
echo 2. Test registration: POST /api/register/
echo 3. Check Swagger UI: http://localhost:8000/api/docs/
echo ======================================
echo.

pause
