@echo off

echo 🧪 Testing Rumble Upload Functionality...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run install first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found. Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Set test environment variables
set LOG_LEVEL=DEBUG
set HEADLESS_MODE=false

echo 🔧 Test Configuration:
echo    - Log level: DEBUG
echo    - Headless mode: Disabled (browser will be visible)
echo    - Make sure your Rumble credentials are set in .env
echo.

REM Run the test
python test_rumble_upload.py

pause
