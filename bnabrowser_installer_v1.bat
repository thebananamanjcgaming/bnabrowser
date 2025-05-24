@echo off
echo Checking for Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed! Install Python first.
    pause
    exit /b
)

echo Python detected!
echo Installing required Python packages...
python -m pip install --upgrade pip
python -m pip install PyQt5 PyQtWebEngine
python -m pip install validators
python -m pip install requests

echo Installation complete!
echo.

echo Choose how to launch Banana Browser:
echo [1] Run as administrator
echo [2] Run normally
set /p choice="Enter your choice: "

if "%choice%"=="1" (
    echo Launching as administrator...
    powershell -Command "Start-Process pythonw -ArgumentList 'assets\bnabrowser_x86.pyw' -Verb RunAs"
    exit /b
) else (
    echo Launching normally...
    pythonw assets\bnabrowser_x86.pyw
)

echo Banana Browser started successfully!
pause
