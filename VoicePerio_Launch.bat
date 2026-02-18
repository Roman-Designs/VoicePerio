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

REM Pass the src path via env var to avoid embedding Windows paths with backslashes in Python string literals
set "VOICEPERIO_SRC=%APP_DIR%\src"

echo ============================================================================
echo  Starting VoicePerio...
echo  (This window will stay open for diagnostics. Do not close it.)
echo ============================================================================
echo.

REM Launch VoicePerio
REM Embedded Python ignores PYTHONPATH, so we inject the src path via sys.path using an env var
"%PYTHON_EXE%" -c "import sys, os; sys.path.insert(0, os.environ['VOICEPERIO_SRC']); import runpy; runpy.run_module('voiceperio', run_name='__main__', alter_sys=True)"

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo  VoicePerio exited with an error.
    echo  Check the output above for details.
    echo ============================================================================
    pause
)

endlocal
