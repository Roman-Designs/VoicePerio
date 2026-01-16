@echo off
REM ============================================================================
REM VoicePerio Build Script for Windows - Enhanced with full error handling
REM ============================================================================

setlocal EnableDelayedExpansion
set "PROJECT_NAME=VoicePerio"
set "SPEC_FILE=installer\voiceperio.spec"
set "DIST_DIR=dist\%PROJECT_NAME%"
set "BUILD_DIR=build"
set "VENV_DIR=venv"
set "MODELS_DIR=models"
set "MODEL_NAME=vosk-model-small-en-us"

for /f "delims=#" %%a in ('"prompt #$E# & for %%b in (1) do rem"') do set "ESC=%%a"
set "GREEN=%ESC%[92m"
set "RED=%ESC%[91m"
set "BLUE=%ESC%[94m"
set "RESET=%ESC%[0m"

REM Parse command-line arguments
set "ARG_VERIFY=0"
if "%~1"=="--verify" set "ARG_VERIFY=1"
if "%~1"=="-v" set "ARG_VERIFY=1"

if "%ARG_VERIFY%"=="1" (
    echo %BLUE%Verifying build...%RESET%
    if exist "%DIST_DIR%\%PROJECT_NAME%.exe" (
        echo %GREEN%✓ Executable found%RESET%
    ) else (
        echo %RED%✗ Executable not found%RESET%
    )
    if exist "%DIST_DIR%\models\%MODEL_NAME%" (
        echo %GREEN%✓ Model found%RESET%
    ) else (
        echo %YELLOW%! Model not found%RESET%
    )
    exit /b 0
)

echo.
echo %BLUE%========================================%RESET%
echo %BLUE%  %PROJECT_NAME% Build Script%RESET%
echo %BLUE%========================================%RESET%
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%ERROR: Python not found. Install Python 3.10+%RESET%
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python -c "import sys; print(sys.version_info.minor)"') do set "PY_MINOR=%%v"
if "%PY_MINOR%"=="" set "PY_MINOR=0"
if %PY_MINOR% LSS 10 (
    echo %RED%ERROR: Python 3.10+ required%RESET%
    pause
    exit /b 1
)
echo %GREEN%✓ Python version OK%RESET%

if not exist "src\voiceperio\__main__.py" (
    echo %RED%ERROR: Run from project root%RESET%
    pause
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)
echo %GREEN%✓ Virtual environment ready%RESET%

call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo %GREEN%✓ Dependencies installed%RESET%

set "MODEL_EXISTS=0"
if exist "%MODELS_DIR%\%MODEL_NAME%\am\final.mdl" set "MODEL_EXISTS=1"
if "%MODEL_EXISTS%"=="1" (
    echo %GREEN%✓ Vosk model found%RESET%
) else (
    echo %YELLOW%Vosk model not found. Run scripts\download_model.py%RESET%
)

if not exist "src\voiceperio\gui\resources" mkdir "src\voiceperio\gui\resources" 2>nul

echo.
echo %BLUE%Building executable...%RESET%
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%" 2>nul
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%" 2>nul

pyinstaller "%SPEC_FILE%" --noconfirm --log-level WARN
if errorlevel 1 (
    echo %RED%Build failed%RESET%
    pause
    exit /b 1
)

echo %GREEN%✓ Executable built%RESET%

if "%MODEL_EXISTS%"=="1" (
    xcopy "%MODELS_DIR%\%MODEL_NAME%" "%DIST_DIR%\models\%MODEL_NAME%\" /E /I /Q >nul
    echo %GREEN%✓ Model copied%RESET%
)

(
echo {
echo   "audio": {"device_id": null, "sample_rate": 16000, "chunk_size": 4000, "channels": 1},
echo   "behavior": {"tab_after_sequence": true, "keystroke_delay_ms": 50},
echo   "target": {"window_title": "Dentrix", "auto_focus": true},
echo   "gui": {"show_floating_indicator": true, "indicator_opacity": 0.9},
echo   "hotkey": {"toggle_listening": "ctrl+shift+v"},
echo   "speech": {"model_path": "models/vosk-model-small-en-us"}
echo }
) > "%DIST_DIR%\config.json"

(
echo VoicePerio - Voice-Controlled Periodontal Charting Assistant
echo.
echo Quick Start:
echo 1. Run VoicePerio.exe
echo 2. Open your perio charting software
echo 3. Dictate pocket depths (e.g., "three two three")
echo.
echo Commands: numbers 0-15, bleeding, suppuration, next, previous
echo Hotkeys: Ctrl+Shift+V (toggle), Ctrl+Shift+X (exit)
echo.
echo License: MIT
) > "%DIST_DIR%\README.txt"

(
echo MIT License
echo.
echo Copyright (c) 2024 VoicePerio
echo.
echo Permission is hereby granted... see LICENSE for full text.
) > "%DIST_DIR%\LICENSE.txt"

echo %GREEN%✓ Distribution package ready%RESET%
echo.
echo %GREEN%========================================%RESET%
echo %GREEN%  BUILD COMPLETE!%RESET%
echo %GREEN%========================================%RESET%
echo.
echo Output: %DIST_DIR%\
echo.
explorer "%DIST_DIR%"

endlocal
pause
exit /b 0
