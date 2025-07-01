@echo off
echo ========================================
echo   Roni AI Image Generator API Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check if virtual environment exists
if exist "venv" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements-api.txt
)

echo.
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing missing dependencies...
    pip install -r requirements-api.txt
)

echo.
echo Checking OpenAI API key configuration...
if exist ".env" (
    echo .env file found
) else (
    echo WARNING: .env file not found!
    echo Please create a .env file with your OpenAI API key:
    echo OPENAI_API_KEY=sk-your-actual-key-here
    echo.
    echo Do you want to continue anyway? (y/n)
    set /p continue=
    if /i not "%continue%"=="y" (
        echo Exiting...
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Starting API Server on port 8000
echo ========================================
echo.
echo The server will be available at:
echo   - Local: http://localhost:8000
echo   - Network: http://192.168.100.4:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the API server
python api_server.py

echo.
echo Server stopped.
pause 