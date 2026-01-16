# VoicePerio Distribution Guide

This document provides instructions for distributing VoicePerio to end users.

## Table of Contents

1. [Overview](#overview)
2. [Distribution Package Structure](#distribution-package-structure)
3. [Preparing for Distribution](#preparing-for-distribution)
4. [Distribution Methods](#distribution-methods)
5. [Installation Instructions for Users](#installation-instructions-for-users)
6. [Silent/Enterprise Deployment](#silententerprise-deployment)
7. [Code Signing](#code-signing)
8. [Antivirus Considerations](#antivirus-considerations)
9. [Updating VoicePerio](#updating-voiceperio)

---

## Overview

VoicePerio is distributed as a standalone Windows application that doesn't require Python installation. Users simply extract the zip file and run the executable.

**Key Points:**
- No installer required (portable)
- No Python installation needed
- Works on Windows 10/11
- Requires ~150MB disk space
- Speech recognition works offline

---

## Distribution Package Structure

When you build VoicePerio, the distribution folder contains:

```
VoicePerio/
├── VoicePerio.exe                    # Main executable
├── models/
│   └── vosk-model-small-en-us/       # Speech recognition model
│       ├── am/final.mdl              # Acoustic model
│       ├── conf/mfcc.conf            # MFCC configuration
│       ├── conf/model.conf           # Model configuration
│       └── vosk-model-small-en-us    # Model metadata
├── config.json                       # Default configuration
├── README.txt                        # Quick start guide
└── LICENSE.txt                       # MIT License

Total: ~100-150MB
```

### File Descriptions

| File/Folder | Purpose | Required |
|-------------|---------|----------|
| `VoicePerio.exe` | Main application | Yes |
| `models/` | Speech recognition | Yes |
| `config.json` | Settings | No (created on first run) |
| `README.txt` | Instructions | Recommended |
| `LICENSE.txt` | Legal | Recommended |

---

## Preparing for Distribution

### 1. Complete the Build

```cmd
cd C:\path\to\VoicePerio
build.bat
```

### 2. Verify the Build

```cmd
build.bat --verify
```

This checks that all required files are present.

### 3. Test the Executable

Before distributing, test the built executable:

1. Navigate to `dist\VoicePerio\`
2. Double-click `VoicePerio.exe`
3. Verify:
   - System tray icon appears
   - Application starts without errors
   - Speech recognition works (use microphone)
   - Keystroke injection works (test in Notepad)

### 4. Prepare Distribution Files

Create a zip file:

```cmd
cd dist
zip -r VoicePerio-1.0.0-Windows.zip VoicePerio/
```

Or using Windows Explorer:
1. Right-click the `VoicePerio` folder
2. Select "Send to" > "Compressed (zipped) folder"
3. Rename to `VoicePerio-1.0.0-Windows.zip`

---

## Distribution Methods

### Method 1: Direct Download (Recommended)

Host the zip file on:
- GitHub Releases
- Your website
- File sharing service

**Pros:**
- Easy to update
- Users can download directly

**Cons:**
- Requires hosting
- Large file (~150MB)

### Method 2: USB/Network Share

Copy the extracted folder to:
- USB drive
- Network file share
- Internal company distribution point

**Pros:**
- No internet required
- Fast for internal distribution

**Cons:**
- Manual update process

### Method 3: Enterprise Deployment

See [Silent/Enterprise Deployment](#silententerprise-deployment)

---

## Installation Instructions for Users

### Quick Start Guide (for README.txt)

```
VoicePerio - Voice-Controlled Periodontal Charting Assistant

INSTALLATION:
1. Extract the VoicePerio.zip file
2. Open the extracted VoicePerio folder
3. Double-click VoicePerio.exe to start

USAGE:
1. Run VoicePerio.exe
2. Open your perio charting software (Dentrix, Open Dental, etc.)
3. Click into a probing depth field
4. Dictate pocket depths (e.g., "three two three")
5. Numbers are automatically typed with Tab between fields

COMMANDS:
- Numbers 0-15: "zero", "one", "two", ... "fifteen"
- Sequences: "three two three" types 3 [Tab] 2 [Tab] 3
- Indicators: "bleeding", "suppuration", "furcation"
- Navigation: "next", "previous", "facial", "lingual"

HOTKEYS:
- Ctrl+Shift+V: Toggle listening on/off
- Ctrl+Shift+P: Pause/Resume
- Ctrl+Shift+X: Exit application

TROUBLESHOOTING:
- Ensure microphone is connected and enabled
- Speak clearly at a normal pace
- Keep application window focused when dictating

For more information, visit: https://your-website.com/voiceperio
```

### Visual Installation Guide

1. **Extract the zip file**
   ```
   Right-click VoicePerio-1.0.0-Windows.zip
   Select "Extract All..."
   Choose destination folder
   Click "Extract"
   ```

2. **Launch VoicePerio**
   ```
   Open the extracted folder
   Double-click VoicePerio.exe
   (If Windows SmartScreen appears, click "More info" > "Run anyway")
   ```

3. **First Run Setup**
   ```
   System tray icon appears (small microphone icon)
   Right-click the icon to access settings
   Configure target window (your perio software name)
   ```

---

## Silent/Enterprise Deployment

### Group Policy Deployment

1. Create a network share:
   ```
   \\server\share\VoicePerio\
   ├── VoicePerio-1.0.0-Windows.zip
   ├── install.bat
   └── config.json (customized)
   ```

2. Create `install.bat`:
   ```batch
   @echo off
   echo Installing VoicePerio...
   
   rem Extract to Program Files
   powershell Expand-Archive -Path "VoicePerio-1.0.0-Windows.zip" -DestinationPath "C:\Program Files\VoicePerio"
   
   rem Copy custom config
   copy config.json "C:\Program Files\VoicePerio\config.json"
   
   rem Create desktop shortcut
   powershell $s = (New-Object -COM WScript.Shell).CreateShortcut("$env:USERPROFILE\Desktop\VoicePerio.lnk")
   $s.TargetPath = "C:\Program Files\VoicePerio\VoicePerio.exe"
   $s.Save()
   
   echo Installation complete.
   ```

3. Deploy via Group Policy:
   - Computer Configuration > Windows Settings > Scripts
   - Add `install.bat` as startup script

### SCCM/Intune Deployment

For System Center Configuration Manager or Microsoft Intune:

1. Package the application as a standard application
2. Detection rule:
   ```
   Path: C:\Program Files\VoicePerio\VoicePerio.exe
   File exists: Yes
   ```
3. Install command: `VoicePerio.exe /S`
4. Uninstall command: `rmdir /s /q "C:\Program Files\VoicePerio"`

### Default Configuration

For enterprise deployments, pre-configure `config.json`:

```json
{
  "audio": {
    "device_id": 0,
    "sample_rate": 16000
  },
  "behavior": {
    "tab_after_sequence": true,
    "keystroke_delay_ms": 50
  },
  "target": {
    "window_title": "YourPerioSoftware",
    "auto_focus": true
  },
  "gui": {
    "show_floating_indicator": true,
    "indicator_opacity": 0.9
  },
  "hotkey": {
    "toggle_listening": "ctrl+shift+v"
  }
}
```

---

## Code Signing

### Why Code Sign?

- Eliminates SmartScreen warnings
- Establishes trust with users
- Required for some enterprise deployments
- Professional appearance

### Getting a Code Signing Certificate

1. **Certificate Authorities:**
   - DigiCert (digi cert.com)
   - Sectigo (sectigo.com)
   - GlobalSign (globalsign.com)

2. **Certificate Types:**
   - Organization Validation (OV) - $200-400/year
   - Extended Validation (EV) - $300-600/year (recommended)

### Signing the Executable

After building, sign the executable:

```cmd
rem Using signtool (from Windows SDK)
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist\VoicePerio\VoicePerio.exe
```

Using a cloud signing service (e.g., SignPath.io):

```cmd
signpath.exe sign --api-token YOUR_API_TOKEN --configuration Release --input dist\VoicePerio\VoicePerio.exe
```

### Verifying Signature

```cmd
signtool verify /pa /v dist\VoicePerio\VoicePerio.exe
```

---

## Antivirus Considerations

### False Positives

PyInstaller-built executables may be flagged by some antivirus software. This is a known issue and doesn't indicate malware.

### Reducing False Positives

1. **Code Sign**: Signed executables are less likely to be flagged
2. **Use Updated PyInstaller**: Newer versions have fewer issues
3. **Whitelist**: Provide instructions for users to add exclusion
4. **Submit Sample**: Report false positives to antivirus vendors

### Handling SmartScreen

Windows SmartScreen may show warnings for unsigned executables:

1. **Click "More info"** > **"Run anyway"**
2. **Code sign** the executable to prevent this
3. **Build reputation** by distributing widely

### Enterprise Antivirus Exclusion

For enterprise deployments, add to antivirus exclusions:

```
Path: C:\Program Files\VoicePerio\
Process: VoicePerio.exe
```

---

## Updating VoicePerio

### Update Process

1. **Build new version** on development machine
2. **Test thoroughly** before release
3. **Create release notes** (CHANGELOG.md)
4. **Distribute new zip file**
5. **Notify users** of update

### Automatic Updates

VoicePerio doesn't include automatic update functionality. To implement:

1. Add update check code:
   ```python
   def check_for_updates():
       response = requests.get("https://api.example.com/voiceperio/version")
       latest = response.json()['version']
       if latest > CURRENT_VERSION:
           # Notify user of available update
   ```

2. Use a versioning service:
   - GitHub Releases API
   - Custom API endpoint
   - Version file on server

### Silent Update Deployment

For enterprise environments:

```batch
@echo off
echo Updating VoicePerio...

rem Stop running instance
taskkill /F /IM VoicePerio.exe 2>nul

rem Backup current version
if exist "C:\Program Files\VoicePerio" (
    rmdir /s /q "C:\Program Files\VoicePerio_backup"
    ren "C:\Program Files\VoicePerio" "VoicePerio_backup"
)

rem Install new version
powershell Expand-Archive -Path "VoicePerio-1.1.0-Windows.zip" -DestinationPath "C:\Program Files\VoicePerio"

rem Restore config
if exist "C:\Program Files\VoicePerio_backup\config.json" (
    copy "C:\Program Files\VoicePerio_backup\config.json" "C:\Program Files\VoicePerio\"
)

rem Clean up old version
rmdir /s /q "C:\Program Files\VoicePerio_backup"

echo Update complete.
```

---

## Checklist Before Distribution

- [ ] Build completes successfully
- [ ] Executable runs without errors
- [ ] Speech recognition works
- [ ] Keystroke injection works
- [ ] Code signing applied (if available)
- [ ] README.txt is clear and complete
- [ ] LICENSE.txt included
- [ ] Zip file created and tested
- [ ] Download link tested
- [ ] Release notes prepared
- [ ] Support contact information available

---

## Support

For distribution issues:
- Check [BUILD.md](BUILD.md) for build troubleshooting
- Check [README.md](README.md) for usage questions
- Search existing issues on GitHub
- Create a new issue with details

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2024 | Initial distribution package |
