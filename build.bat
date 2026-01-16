@echo off
REM ============================================================================
REM VoicePerio Build Script for Windows
REM Creates a standalone .exe that can be distributed to end users
REM ============================================================================

echo.
echo ============================================
echo   VoicePerio Build Script
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "src\voiceperio\__main__.py" (
    echo ERROR: Please run this script from the VoicePerio project root
    echo Expected to find: src\voiceperio\__main__.py
    pause
    exit /b 1
)

REM Create/activate virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

REM Check if Vosk model exists
if not exist "models\vosk-model-small-en-us" (
    echo.
    echo WARNING: Vosk model not found!
    echo The speech recognition model needs to be downloaded.
    echo.
    set /p DOWNLOAD_MODEL="Download model now? (Y/N): "
    if /i "%DOWNLOAD_MODEL%"=="Y" (
        python scripts\download_model.py
    ) else (
        echo.
        echo Skipping model download. You will need to:
        echo   1. Run: python scripts\download_model.py
        echo   2. Or manually place model in: models\vosk-model-small-en-us
        echo.
    )
)

REM Create resources directory if it doesn't exist
if not exist "src\voiceperio\gui\resources" (
    mkdir "src\voiceperio\gui\resources"
)

REM Build the executable
echo.
echo ============================================
echo   Building executable...
echo ============================================
echo.

pyinstaller installer\voiceperio.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Output location: dist\VoicePerio\VoicePerio.exe
echo.
echo To distribute VoicePerio:
echo   1. Copy the entire "dist\VoicePerio" folder
echo   2. Include the "models" folder with the Vosk model
echo   3. Users run VoicePerio.exe
echo.

REM Open output folder
explorer dist\VoicePerio

pause
