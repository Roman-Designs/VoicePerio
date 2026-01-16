# VoicePerio v1.0.0 Release Notes

**Release Date:** January 15, 2026  
**Version:** 1.0.0 (First Stable Release)  
**Build:** PyInstaller 6.18.0 with Python 3.14.2  
**Platform:** Windows 10/11 (64-bit)

---

## 🎉 VoicePerio v1.0.0 - First Stable Release

We are thrilled to announce the first stable release of VoicePerio - a voice-controlled periodontal charting assistant that allows dental professionals to dictate pocket depths and clinical indicators while keeping their hands on the probe and eyes on the patient.

This release represents the culmination of 7 development phases and includes a complete, production-ready Windows application with over 11,000 lines of code.

---

## 📋 Table of Contents

1. [What's New](#whats-new)
2. [Key Features](#key-features)
3. [Voice Commands](#voice-commands)
4. [System Requirements](#system-requirements)
5. [Installation](#installation)
6. [Getting Started](#getting-started)
7. [Global Hotkeys](#global-hotkeys)
8. [Configuration](#configuration)
9. [Build Instructions](#build-instructions)
10. [Known Issues](#known-issues)
11. [Roadmap](#roadmap)
12. [Credits](#credits)
13. [License](#license)

---

## What's New

### ✅ Complete Application Suite

This release includes all components needed for a production-ready voice-controlled dental charting application:

- **Audio Capture** - Real-time microphone input with configurable sample rates
- **Speech Recognition** - Offline Vosk engine with custom perio vocabulary
- **Command Parser** - Intelligent parsing of voice commands to actions
- **Keystroke Injection** - Seamless typing into target dental software
- **GUI Interface** - System tray, floating indicator, and settings dialog
- **Global Hotkeys** - Keyboard shortcuts for hands-free control
- **Standalone Executable** - No Python installation required

### 🎨 User Interface

- Professional dark-themed GUI
- System tray integration with context menu
- Floating status indicator with real-time feedback
- Comprehensive settings dialog
- Custom executable icon from project logo

### 🧪 Testing & Quality

- 235+ automated tests
- 100% type hint coverage
- 100% docstring coverage
- Comprehensive error handling
- Detailed logging

---

## Key Features

### 🎤 Voice-Controlled Charting

Dictate periodontal pocket depths without using your hands:

```
Say: "three two three"
Result: Types 3 → Tab → 2 → Tab → 3
```

### 📊 Supported Voice Commands

**Numbers (0-15):**
- Single numbers: "one", "two", "three"... "fifteen"
- Number sequences: "three two three" → 3 [Tab] 2 [Tab] 3
- Alternative pronunciations: "oh" for zero, "niner" for nine

**Clinical Indicators:**
- Bleeding on probing: "bleeding", "bleed", "bop"
- Suppuration/pus: "suppuration", "pus"
- Plaque: "plaque"
- Calculus/tartar: "calculus", "tartar"
- Furcation involvement: "furcation one/two/three"
- Mobility: "mobility one/two/three"
- Recession: "recession"

**Navigation:**
- "next" - Advance to next field
- "previous" - Go back
- "upper left", "lower right", etc. - Jump to quadrant
- "facial", "lingual" - Switch tooth surface

**Actions:**
- "enter" - Press Enter
- "save" - Save (Ctrl+S)
- "undo" - Undo (Ctrl+Z)
- "correction" - Scratch that (undo)

**Application Control:**
- "voice perio wake" - Start listening
- "voice perio sleep" - Pause listening
- "voice perio stop" - Exit application

### ⌨️ Global Hotkeys

Control VoicePerio from anywhere with keyboard shortcuts:

| Hotkey | Action |
|--------|--------|
| `Ctrl + Shift + V` | Toggle listening on/off |
| `Ctrl + Shift + P` | Pause/Resume listening |
| `Ctrl + Shift + S` | Sleep mode |
| `Ctrl + Shift + W` | Wake from sleep |
| `Ctrl + Shift + X` | Exit application |

### 🎯 Target Window Support

VoicePerio works with any Windows application, including:

- **Dentrix** - Primary target
- **Open Dental**
- **EagleSoft**
- **PracticeWorks**
- **SoftDent**
- **Carestream Dental**
- **Any Windows application** with text input fields

### 📈 Performance

- **Audio Processing:** 16kHz sample rate, real-time processing
- **Speech Recognition:** <200ms latency
- **Keystroke Injection:** 50ms default delay (configurable)
- **Memory Usage:** ~100MB (embedded Python runtime)
- **CPU Usage:** <5% typical, <15% during active listening

---

## Voice Commands

### Pocket Depths

```
User: "three"
App: Types "3"

User: "three two three"
App: Types "3" → [Tab] → "2" → [Tab] → "3"

User: "four"
App: Types "4"
```

### Clinical Indicators

```
User: "bleeding"
App: Types "B" or marks bleeding indicator

User: "suppuration"
App: Marks suppuration

User: "plaque"
App: Marks plaque present

User: "calculus"
App: Marks calculus/tartar
```

### Navigation

```
User: "next"
App: Presses Tab → Next field

User: "previous"
App: Presses Shift+Tab → Previous field

User: "upper left"
App: Jumps to upper left quadrant

User: "facial"
App: Switches to facial surface
```

### Actions

```
User: "enter"
App: Presses Enter

User: "save"
App: Presses Ctrl+S

User: "undo"
App: Presses Ctrl+Z
```

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10 or 11 (64-bit) |
| **Processor** | x86-64 compatible CPU |
| **RAM** | 4 GB |
| **Storage** | 200 MB free space |
| **Microphone** | Any Windows-compatible microphone |
| **Audio** | 16kHz sample rate support |

### Recommended Specifications

| Component | Recommendation |
|-----------|----------------|
| **OS** | Windows 11 (latest updates) |
| **Processor** | Modern multi-core CPU |
| **RAM** | 8 GB or more |
| **Storage** | SSD with 500MB free |
| **Microphone** | Noise-canceling headset microphone |
| **Audio** | High-quality microphone array |

---

## Installation

### Option 1: Pre-built Executable (Recommended)

1. **Download** the latest release from the repository
2. **Extract** the `VoicePerio` folder to your desired location
3. **Download** the Vosk speech model:
   - Go to: https://alphacephei.com/vosk/models
   - Download: `vosk-model-small-en-us-0.15.zip` (~40 MB)
   - Extract to: `VoicePerio/models/vosk-model-small-en-us`
4. **Run** `VoicePerio.exe`

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/IntelThread/VoicePerio.git
cd VoicePerio

# Install dependencies
pip install -r requirements.txt

# Download Vosk model
python scripts/download_model.py

# Build executable
pyinstaller installer/voiceperio.spec

# Find output in: dist/VoicePerio/
```

---

## Getting Started

### First Run

1. **Launch** `VoicePerio.exe`
2. **Observe** the system tray icon appears
3. **Right-click** the icon to access the menu
4. **Select** "Settings" to configure:
   - Target window (e.g., "Dentrix")
   - Audio device
   - Keystroke delay
   - GUI preferences
5. **Open** your dental charting software
6. **Click** into a pocket depth field
7. **Say** "three two three" to test

### Testing with Notepad

For initial testing without dental software:

1. **Open** Notepad
2. **Configure** target window to "Notepad" in Settings
3. **Click** in Notepad's text area
4. **Say** "one two three"
5. **Observe** numbers being typed with Tab navigation

---

## Global Hotkeys

VoicePerio supports global hotkeys that work even when the application is minimized or the system tray is hidden.

### Available Hotkeys

| Hotkey | Function | Description |
|--------|----------|-------------|
| `Ctrl + Shift + V` | Toggle Listening | Switch between listening and paused states |
| `Ctrl + Shift + P` | Pause/Resume | Temporarily pause listening |
| `Ctrl + Shift + S` | Sleep | Enter sleep mode (no audio processing) |
| `Ctrl + Shift + W` | Wake | Wake from sleep mode |
| `Ctrl + Shift + X` | Exit | Close VoicePerio completely |

### Hotkey Configuration

Hotkeys can be customized in the Settings dialog (Hotkeys tab) or in `config.json`:

```json
{
  "hotkey": {
    "toggle_listening": "ctrl+shift+v",
    "pause": "ctrl+shift+p",
    "sleep": "ctrl+shift+s",
    "wake": "ctrl+shift+w",
    "exit": "ctrl+shift+x"
  }
}
```

---

## Configuration

### Configuration File

VoicePerio uses `config.json` for all settings:

```json
{
  "audio": {
    "device_id": null,
    "sample_rate": 16000,
    "chunk_size": 4000
  },
  "behavior": {
    "tab_after_sequence": true,
    "keystroke_delay_ms": 50,
    "auto_advance_tooth": false
  },
  "target": {
    "window_title": "Dentrix",
    "auto_focus": true
  },
  "gui": {
    "show_floating_indicator": true,
    "indicator_opacity": 0.9,
    "show_command_feedback": true
  },
  "hotkey": {
    "toggle_listening": "ctrl+shift+v",
    "pause": "ctrl+shift+p",
    "sleep": "ctrl+shift+s",
    "wake": "ctrl+shift+w",
    "exit": "ctrl+shift+x"
  }
}
```

### Configuration Options

| Section | Option | Description | Default |
|---------|--------|-------------|---------|
| audio | device_id | Audio input device index | null (default) |
| audio | sample_rate | Audio sample rate in Hz | 16000 |
| audio | chunk_size | Audio chunk size in bytes | 4000 |
| behavior | tab_after_sequence | Auto-Tab after number sequence | true |
| behavior | keystroke_delay_ms | Delay between keystrokes | 50 |
| behavior | auto_advance_tooth | Auto-advance to next tooth | false |
| target | window_title | Target window title pattern | "Dentrix" |
| target | auto_focus | Auto-focus target window | true |
| gui | show_floating_indicator | Show floating status window | true |
| gui | indicator_opacity | Floating indicator opacity (0-1) | 0.9 |
| gui | show_command_feedback | Show command feedback | true |

---

## Build Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- 2GB free disk space

### Build Steps

```bash
# 1. Clone the repository
git clone https://github.com/IntelThread/VoicePerio.git
cd VoicePerio

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 4. Download Vosk model
python scripts/download_model.py

# 5. Build executable
pyinstaller installer/voiceperio.spec --noconfirm

# 6. Output located in: dist/VoicePerio/
```

### Build Output

```
dist/VoicePerio/
├── VoicePerio.exe              # Main executable (7.4 MB)
├── _internal/                  # Embedded Python runtime (~100 MB)
├── models/
│   └── vosk-model-small-en-us/ # Speech recognition model (~40 MB)
├── config.json                 # Default configuration
├── README.txt                  # Quick start guide
└── LICENSE.txt                 # MIT License
```

### Build Customization

#### Custom Icon

To use a custom icon:

1. Replace `src/voiceperio/gui/resources/icon.ico` with your icon
2. Rebuild with `pyinstaller installer/voiceperio.spec`

#### Single-File Build

To create a single-file executable instead of directory:

1. Edit `installer/voiceperio.spec`
2. Comment out the `COLLECT` section
3. Uncomment the single-file build section
4. Rebuild

---

## Known Issues

### Audio Input

**Issue:** Low microphone amplitude may cause poor recognition
**Solution:** Increase microphone levels in Windows Sound Settings (mmsys.cpl)

**Issue:** Wrong audio device selected
**Solution:** Configure correct device in Settings → Audio tab

### Speech Recognition

**Issue:** Words not in vocabulary not recognized
**Solution:** The application uses a custom perio vocabulary. General speech may not work well.

**Issue:** Background noise affects recognition
**Solution:** Use noise-canceling microphone; reduce background noise

### Window Focus

**Issue:** Keystrokes not appearing in target window
**Solution:** 
1. Ensure target window is open
2. Click into a text field first
3. Check target window title in Settings
4. Enable "Auto-focus" in Settings

### Performance

**Issue:** High CPU usage
**Solution:** Normal during active listening. Use sleep mode when not charting.

---

## Roadmap

### Version 1.1.0 (Future)

- [ ] Additional language support (Spanish, French, German)
- [ ] Custom vocabulary builder
- [ ] Multi-display support
- [ ] Command logging and analytics
- [ ] Team usage statistics
- [ ] Cloud sync for settings

### Version 2.0.0 (Future)

- [ ] AI-powered command suggestions
- [ ] Integration with major EHR systems
- [ ] Mobile companion app
- [ ] Voice biometrics for user profiles
- [ ] Advanced analytics dashboard

---

## Credits

### Development Team

- **Lead Developer:** VoicePerio Development Team
- **Architecture:** Multi-phase implementation
- **Testing:** Comprehensive test suite (235+ tests)

### Dependencies

VoicePerio is built using these excellent open-source projects:

- **PyQt6** - GUI framework (https://www.riverbankcomputing.com/software/pyqt/)
- **Vosk** - Offline speech recognition (https://alphacephei.com/vosk/)
- **sounddevice** - Audio I/O (https://python-sounddevice.readthedocs.io/)
- **pyautogui** - GUI automation (https://pyautogui.readthedocs.io/)
- **keyboard** - Global hotkeys (https://github.com/boppreh/keyboard)
- **PyInstaller** - Application packaging (https://pyinstaller.org/)
- **NumPy** - Numerical computing (https://numpy.org/)

---

## License

VoicePerio is licensed under the MIT License:

```
MIT License

Copyright (c) 2026 VoicePerio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Support

### Documentation

- **README.md** - Quick start guide
- **BUILD.md** - Detailed build instructions
- **DEPLOY.md** - Distribution guide
- **Phase Documentation** - PHASE{4,5,6}_IMPLEMENTATION.md

### Issues

Report bugs and feature requests at:
https://github.com/IntelThread/VoicePerio/issues

### Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## Changelog

### v1.0.0 (2026-01-15)

**Initial Stable Release**

#### Added
- Complete voice-controlled periodontal charting application
- Audio capture and speech recognition (Vosk)
- Command parser with perio-specific vocabulary
- Keystroke injection with window utilities
- GUI with system tray, floating indicator, settings
- Global hotkey support
- Comprehensive test suite (235+ tests)
- PyInstaller build configuration
- Documentation (BUILD.md, DEPLOY.md, phase docs)

#### Changed
- N/A (initial release)

#### Fixed
- PyQt6 compatibility issues
- Vosk DLL inclusion
- Microphone level detection

#### Security
- No known security vulnerabilities

---

**Thank you for using VoicePerio!**

*Keep your hands on the probe, eyes on the patient!*
