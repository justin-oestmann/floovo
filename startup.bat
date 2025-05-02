:: filepath: e:\MediaTinder\floovo\start_floovo.bat
@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

:: Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip is not installed. Please ensure Python 3.12.x or higher is installed correctly.
    pause
    exit /b 1
)

:: Navigate to the Floovo directory
cd /d "%~dp0"

:: Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Please install Git to continue.
    pause
    exit /b 1
)

:: Update the repository to ensure the script is up-to-date
echo Checking for updates from the repository...
git pull https://github.com/justin-oestmann/floovo.git

:: Check if the required libraries are installed
echo Checking for required Python libraries...
pip install -r requirements.txt

:: Start the Python application
echo Starting Floovo...
python app.py

pause