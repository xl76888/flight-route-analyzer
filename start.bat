@echo off
cd /d "D:\flight_tool"

echo ========================================
echo Flight Route Visualization Tool
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Create data folder
if not exist "data" (
    mkdir data
    echo [INFO] Created data folder
)

REM Start application
echo.
echo [INFO] Starting Flight Route Visualization Tool...
echo [INFO] The application will open in your browser
echo [INFO] Press Ctrl+C to stop the application
echo.
streamlit run web_app.py

REM Pause if error occurs
if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start
    pause
)