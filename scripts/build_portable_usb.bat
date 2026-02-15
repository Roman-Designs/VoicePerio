@echo off
REM ============================================================================
REM VoicePerio - Portable USB Bundle Builder
REM ============================================================================
REM Run this script on YOUR machine (where Python is installed) to create
REM a portable USB-ready folder. Then copy the output folder to a USB drive.
REM ============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "OUTPUT_DIR=%PROJECT_DIR%\VoicePerio_Portable"
set "PYTHON_VERSION=3.10.11"
set "PYTHON_EMBED_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"

echo ============================================================================
echo  VoicePerio Portable USB Builder
echo ============================================================================
echo.
echo This script will create a portable, no-install-needed copy of VoicePerio.
echo Output folder: %OUTPUT_DIR%
echo.

REM Clean previous build
if exist "%OUTPUT_DIR%" (
    echo Cleaning previous build...
    rmdir /s /q "%OUTPUT_DIR%"
)

REM Create directory structure
echo Creating directory structure...
mkdir "%OUTPUT_DIR%"
mkdir "%OUTPUT_DIR%\python"
mkdir "%OUTPUT_DIR%\app"
mkdir "%OUTPUT_DIR%\models"

REM ============================================================================
REM Step 1: Download Python Embeddable Package
REM ============================================================================
echo.
echo [1/5] Downloading Python %PYTHON_VERSION% Embeddable Package...
echo       URL: %PYTHON_EMBED_URL%

powershell -Command "Invoke-WebRequest -Uri '%PYTHON_EMBED_URL%' -OutFile '%OUTPUT_DIR%\python_embed.zip'"
if errorlevel 1 (
    echo ERROR: Failed to download Python embeddable package.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo       Extracting...
powershell -Command "Expand-Archive -Path '%OUTPUT_DIR%\python_embed.zip' -DestinationPath '%OUTPUT_DIR%\python' -Force"
del "%OUTPUT_DIR%\python_embed.zip"

REM ============================================================================
REM Step 2: Enable pip in the embeddable Python
REM ============================================================================
echo.
echo [2/5] Setting up pip in portable Python...

REM Uncomment the import site line in python310._pth to enable pip/site-packages
powershell -Command "(Get-Content '%OUTPUT_DIR%\python\python310._pth') -replace '#import site', 'import site' | Set-Content '%OUTPUT_DIR%\python\python310._pth'"

REM Download get-pip.py
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%OUTPUT_DIR%\python\get-pip.py'"

REM Install pip
"%OUTPUT_DIR%\python\python.exe" "%OUTPUT_DIR%\python\get-pip.py" --no-warn-script-location
if errorlevel 1 (
    echo ERROR: Failed to install pip.
    pause
    exit /b 1
)
del "%OUTPUT_DIR%\python\get-pip.py"

REM ============================================================================
REM Step 3: Install VoicePerio dependencies
REM ============================================================================
echo.
echo [3/5] Installing VoicePerio dependencies (this may take a few minutes)...

"%OUTPUT_DIR%\python\python.exe" -m pip install --no-warn-script-location ^
    vosk>=0.3.45 ^
    sounddevice>=0.4.6 ^
    pyautogui>=0.9.54 ^
    pynput>=1.7.6 ^
    PyQt6>=6.5.0 ^
    numpy>=1.24.0 ^
    keyboard>=0.13.5 ^
    pywin32>=306 ^
    rapidfuzz>=3.2.0 ^
    jsonschema>=4.19.0 ^
    colorlog>=6.7.0

if errorlevel 1 (
    echo ERROR: Failed to install some dependencies.
    echo Some packages may require Visual C++ Build Tools.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 4: Copy VoicePerio application files
REM ============================================================================
echo.
echo [4/5] Copying VoicePerio application files...

REM Copy source code
xcopy /s /e /i /q "%PROJECT_DIR%\src" "%OUTPUT_DIR%\app\src"

REM Copy default commands
if exist "%PROJECT_DIR%\default_commands.json" (
    copy "%PROJECT_DIR%\default_commands.json" "%OUTPUT_DIR%\app\"
)

REM Copy Vosk model
if exist "%PROJECT_DIR%\models\vosk-model-small-en-us" (
    echo       Copying Vosk speech model (~40MB)...
    xcopy /s /e /i /q "%PROJECT_DIR%\models\vosk-model-small-en-us" "%OUTPUT_DIR%\models\vosk-model-small-en-us"
) else (
    echo       WARNING: Vosk model not found at models\vosk-model-small-en-us
    echo       You will need to download it separately.
    echo       Run: python download_model.py
)

REM Copy model download script
if exist "%PROJECT_DIR%\download_model.py" (
    copy "%PROJECT_DIR%\download_model.py" "%OUTPUT_DIR%\app\"
)
if exist "%PROJECT_DIR%\scripts\download_model.py" (
    copy "%PROJECT_DIR%\scripts\download_model.py" "%OUTPUT_DIR%\app\"
)

REM Copy resources
if exist "%PROJECT_DIR%\VoicePerio.png" (
    copy "%PROJECT_DIR%\VoicePerio.png" "%OUTPUT_DIR%\app\"
)

REM ============================================================================
REM Step 5: Create launcher
REM ============================================================================
echo.
echo [5/5] Creating launcher...

REM The launcher .bat is created separately (VoicePerio_Launch.bat)
copy "%SCRIPT_DIR%\..\VoicePerio_Launch.bat" "%OUTPUT_DIR%\VoicePerio_Launch.bat" 2>nul
if errorlevel 1 (
    echo       Launcher will be created from template...
)

echo.
echo ============================================================================
echo  BUILD COMPLETE!
echo ============================================================================
echo.
echo  Output folder: %OUTPUT_DIR%
echo.
echo  To deploy:
echo    1. Copy the entire "VoicePerio_Portable" folder to a USB drive
echo    2. On the target computer, open the folder from the USB drive
echo    3. Double-click "VoicePerio_Launch.bat" to start
echo.
echo  No installation required on the target computer!
echo ============================================================================
echo.
pause
