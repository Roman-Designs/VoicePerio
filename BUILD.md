# VoicePerio Build Documentation

This document provides detailed instructions for building the VoicePerio standalone Windows executable.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Build Process Overview](#build-process-overview)
4. [Build Options](#build-options)
5. [Manual Build](#manual-build)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [CI/CD Integration](#cicd-integration)

---

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Windows | 10 | 11 |
| Python | 3.10 | 3.11 or 3.12 |
| RAM | 4 GB | 8 GB |
| Disk Space | 2 GB | 5 GB |
| Internet | Required (first build) | Required (updates) |

### Required Software

1. **Python 3.10+**
   - Download from: https://python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation
   - Verify: `python --version`

2. **Git** (optional, for version control)
   - Download from: https://git-scm.com/

3. **UPX** (optional, for compression)
   - Download from: https://upx.github.io/
   - Add to PATH for smaller executables

### Python Dependencies

All dependencies are listed in `requirements.txt`:

```
vosk>=0.3.45          # Speech recognition
sounddevice>=0.4.6    # Audio capture
pyautogui>=0.9.54     # Keystroke injection
pynput>=1.7.6         # Input monitoring
PyQt6>=6.5.0          # GUI framework
numpy>=1.24.0         # Audio processing
keyboard>=0.13.5      # Hotkey support
pywin32>=306          # Windows API
rapidfuzz>=3.2.0      # Fuzzy matching
jsonschema>=4.19.0    # Config validation
colorlog>=6.7.0       # Colored logging
pyinstaller>=5.13.0   # Build tool
```

---

## Quick Start

### Option 1: Double-Click Build (Easiest)

1. Navigate to the VoicePerio project directory
2. Double-click `build.bat`
3. Wait for the build to complete (~5-15 minutes)
4. Find your executable at: `dist\VoicePerio\VoicePerio.exe`

### Option 2: Command Line Build

```cmd
cd C:\path\to\VoicePerio
build.bat
```

### Option 3: Quick Build (Skip Model Download)

```cmd
build.bat --quick
```

---

## Build Process Overview

The `build.bat` script performs these steps:

```
1. Validate Environment
   ├── Check Python version (3.10+)
   ├── Verify project structure
   └── Confirm spec file exists

2. Setup Virtual Environment
   ├── Create venv (if missing)
   ├── Activate venv
   └── Upgrade pip

3. Install Dependencies
   ├── Install from requirements.txt
   └── Install PyInstaller

4. Download Vosk Model (if missing)
   ├── Check if model exists
   ├── Prompt to download (if needed)
   └── Verify model integrity

5. Run PyInstaller
   ├── Parse spec file
   ├── Collect dependencies
   ├── Bundle Python runtime
   └── Create executable

6. Prepare Distribution
   ├── Copy model to dist folder
   ├── Create config.json
   ├── Create README.txt
   ├── Create LICENSE.txt
   └── Verify all files

7. Final Output
   ├── Display build summary
   └── Open output folder
```

---

## Build Options

### Available Command-Line Options

| Option | Description |
|--------|-------------|
| `--quick` | Skip model download (use if model already exists) |
| `--clean` | Remove old build artifacts before building |
| `--verify` | Verify existing build without rebuilding |
| `--help` | Show help message |

### Examples

```cmd
# Full build with all checks
build.bat

# Quick build (skip model download)
build.bat --quick

# Clean and rebuild from scratch
build.bat --clean

# Verify existing build
build.bat --verify

# Show help
build.bat --help
```

---

## Manual Build

If you prefer to build manually or need custom options:

### Step 1: Setup Environment

```cmd
cd C:\path\to\VoicePerio

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### Step 2: Download Model (if needed)

```cmd
python scripts\download_model.py
```

### Step 3: Run PyInstaller

```cmd
pyinstaller installer\voiceperio.spec --noconfirm
```

### Step 4: Prepare Distribution

```cmd
# Copy model
xcopy models\vosk-model-small-en-us dist\VoicePerio\models\ /E /I

# Create config
(
echo {
echo   "audio": {"device_id": null},
echo   "behavior": {"tab_after_sequence": true},
echo   "target": {"window_title": "Dentrix"}
echo }
) > dist\VoicePerio\config.json
```

### Step 5: Verify Build

```cmd
# Test executable
dist\VoicePerio\VoicePerio.exe --help

# Check file structure
tree /F dist\VoicePerio\
```

---

## Troubleshooting

### Common Issues

#### Issue: Python Not Found

**Error**: `ERROR: Python is not installed or not in PATH`

**Solution**:
1. Install Python 3.10+ from https://python.org/downloads/
2. Check "Add Python to PATH" during installation
3. Restart command prompt
4. Verify: `python --version`

#### Issue: Build Fails with Import Error

**Error**: `ModuleNotFoundError: No module named '...'`

**Solution**:
1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```cmd
   venv\Scripts\activate.bat
   pip install -r requirements.txt
   pip install pyinstaller
   ```

#### Issue: PyInstaller Hangs

**Symptom**: Build process stops at "Analyzing..." or similar

**Solution**:
1. Cancel with Ctrl+C
2. Clean build artifacts:
   ```cmd
   rmdir /s /q build
   rmdir /s /q dist
   ```
3. Try again with `--clean` option

#### Issue: Antivirus False Positive

**Symptom**: Executable flagged as malware

**Solution**:
1. Add PyInstaller output folder to antivirus exclusions
2. Code sign the executable (requires certificate)
3. Submit false positive report to antivirus vendor

#### Issue: Missing Vosk Model

**Error**: Speech recognition doesn't work

**Solution**:
1. Download model manually:
   ```cmd
   python scripts\download_model.py
   ```
2. Or manually from: https://alphacephei.com/vosk/models/
3. Extract to: `models\vosk-model-small-en-us`

#### Issue: Large Executable Size

**Symptom**: Executable is very large (>200MB)

**Solution**:
1. Install UPX for compression:
   ```cmd
   pip install upx-win32
   ```
2. Re-run build (UPX is auto-detected)
3. Consider single-file build (see below)

#### Issue: GUI Doesn't Start

**Error**: Application runs but no window appears

**Solution**:
1. Check if running in windowed mode (spec file has `console=False`)
2. Check Windows Event Viewer for errors
3. Run with debug mode enabled in spec file

### Debug Build

To create a debug build with console output:

1. Edit `installer/voiceperio.spec`
2. Change `console=False` to `console=True`
3. Rebuild:
   ```cmd
   pyinstaller installer\voiceperio.spec --noconfirm --debug
   ```

---

## Advanced Configuration

### Single-File Build

By default, the build creates a directory with the executable and all dependencies. To create a single `.exe` file:

1. Edit `installer/voiceperio.spec`
2. Uncomment the "SINGLE-FILE BUILD" section
3. Rebuild

**Trade-offs**:
- Single file is easier to distribute
- Longer startup time (~10-15 seconds)
- May trigger more false positives in antivirus

### Custom Icon

To use a custom icon:

1. Place your `.ico` file at: `src/voiceperio/gui/resources/icon.ico`
2. Rebuild (icon is auto-detected)

### Version Information

To update version numbers:

1. Edit `installer/version_info.txt`
2. Update:
   - `filevers=(1, 0, 0, 0)` - File version
   - `prodvers=(1, 0, 0, 0)` - Product version
   - `FileVersion` string
   - `ProductVersion` string
   - Copyright year

### Custom Output Directory

To change the output directory:

1. Edit `build.bat`
2. Change: `set "DIST_DIR=dist\YourName"`

### Excluding Modules

To exclude unused modules and reduce size:

1. Edit `installer/voiceperio.spec`
2. Add to `excludes` list:
   ```python
   excludes=[
       'matplotlib',
       'scipy',
       # ... other exclusions
   ]
   ```

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/build.yml`:

```yaml
name: Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
          
      - name: Download Vosk model
        run: python scripts/download_model.py
        
      - name: Build executable
        run: pyinstaller installer/voiceperio.spec --noconfirm
        
      - name: Verify build
        run: build.bat --verify
        
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: VoicePerio
          path: dist/VoicePerio/
```

### Azure DevOps Example

```yaml
trigger:
  - main

pool:
  vmImage: 'windows-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'
      
  - script: |
      pip install -r requirements.txt
      pip install pyinstaller
    displayName: 'Install dependencies'
    
  - script: python scripts/download_model.py
    displayName: 'Download model'
    
  - script: pyinstaller installer/voiceperio.spec --noconfirm
    displayName: 'Build executable'
    
  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: 'dist/VoicePerio'
      artifactName: 'VoicePerio'
```

---

## Build Output

After a successful build, you'll find:

```
dist/VoicePerio/
├── VoicePerio.exe          # Main executable (~50-100MB)
├── models/
│   └── vosk-model-small-en-us/  # Speech model (~40MB)
├── config.json             # Default configuration
├── README.txt              # Quick start guide
└── LICENSE.txt             # MIT License

Total size: ~100-150MB
```

### Running the Built Executable

1. Navigate to `dist\VoicePerio\`
2. Double-click `VoicePerio.exe`
3. The application will start with a system tray icon

### Distributing

To distribute to users:

1. Zip the entire `dist\VoicePerio\` folder
2. Include instructions for extraction and running
3. Users don't need Python installed

---

## Support

If you encounter issues not covered here:

1. Check the [main README](README.md)
2. Search existing issues on GitHub
3. Create a new issue with:
   - Operating system version
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release |
