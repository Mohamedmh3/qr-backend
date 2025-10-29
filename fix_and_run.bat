@echo off
echo ======================================
echo   QR Backend - Complete Fix Script
echo ======================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Fix migration order issue
echo Step 1: Fixing migration order...
python manage.py migrate --fake-initial
if %errorlevel% neq 0 (
    echo Warning: Migration fix had issues, continuing...
)
echo.

REM Apply migrations
echo Step 2: Applying migrations...
python manage.py migrate users --fake-initial
if %errorlevel% neq 0 (
    echo Warning: User migration had issues, continuing...
)
echo.

REM Create superuser if needed
echo Step 3: Creating admin user...
python manage.py shell -c "
from users.models import User
try:
    if not User.objects.filter(email='admin@example.com').exists():
        User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='Admin123!',
            role='admin'
        )
        print('Admin user created successfully!')
    else:
        print('Admin user already exists')
except Exception as e:
    print(f'Error creating admin user: {e}')
"
echo.

REM Start server
echo Step 4: Starting development server...
echo.
echo ======================================
echo Server starting on http://localhost:8000
echo Swagger UI: http://localhost:8000/api/docs/
echo ======================================
echo.
python manage.py runserver 8000

pause
