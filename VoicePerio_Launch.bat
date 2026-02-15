@echo off
REM ============================================================================
REM VoicePerio - Portable Launcher
REM ============================================================================
REM Double-click this file to start VoicePerio.
REM No installation required!
REM ============================================================================

setlocal

REM Get the directory where this batch file is located (the USB drive root)
set "BASE_DIR=%~dp0"
set "PYTHON_EXE=%BASE_DIR%python\python.exe"
set "APP_DIR=%BASE_DIR%app"
set "MODEL_DIR=%BASE_DIR%models"

REM Check that portable Python exists
if not exist "%PYTHON_EXE%" (
    echo ============================================================================
    echo  ERROR: Portable Python not found!
    echo  Expected at: %PYTHON_EXE%
    echo.
    echo  Make sure you are running this from the VoicePerio_Portable folder.
    echo ============================================================================
    pause
    exit /b 1
)

REM Check that the app exists
if not exist "%APP_DIR%\src\voiceperio\__main__.py" (
    echo ============================================================================
    echo  ERROR: VoicePerio application files not found!
    echo  Expected at: %APP_DIR%\src\voiceperio\
    echo ============================================================================
    pause
    exit /b 1
)

REM Check for Vosk model
if not exist "%MODEL_DIR%\vosk-model-small-en-us" (
    echo ============================================================================
    echo  WARNING: Speech recognition model not found!
    echo  Attempting to download it now...
    echo ============================================================================
    if exist "%APP_DIR%\download_model.py" (
        "%PYTHON_EXE%" "%APP_DIR%\download_model.py"
    ) else (
        echo  Please download the Vosk model manually:
        echo  https://alphacephei.com/vosk/models
        echo  Extract "vosk-model-small-en-us" into the "models" folder.
        pause
        exit /b 1
    )
)

REM Set environment variables so VoicePerio can find the model
set "VOSK_MODEL_PATH=%MODEL_DIR%\vosk-model-small-en-us"

REM Add the app source to Python path
set "PYTHONPATH=%APP_DIR%\src;%PYTHONPATH%"

echo ============================================================================
echo  Starting VoicePerio...
echo  (This window will stay open for diagnostics. Do not close it.)
echo ============================================================================
echo.

REM Launch VoicePerio
"%PYTHON_EXE%" -m voiceperio

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo  VoicePerio exited with an error.
    echo  Check the output above for details.
    echo ============================================================================
    pause
)

endlocal
