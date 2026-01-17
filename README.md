⚠️ **IMPORTANT FOR AGENTS: READ AGENTS.md FIRST**

Before starting ANY work on this project, you MUST read **[AGENTS.md](AGENTS.md)** in the root directory. This file contains:
- Complete list of 24 specialized agents available for this project
- What each agent does and how to invoke them
- Recommended agents for different development tasks
- How to properly delegate work to specialists

**Failure to read AGENTS.md will result in inefficient development and missed opportunities to use expert agents.**

---

# VoicePerio

**Voice-Controlled Periodontal Charting Assistant**

VoicePerio is a hands-free voice recognition application for periodontal probing. Dictate pocket depths and perio indicators while keeping your hands on the probe and your eyes on the patient.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Voice Command Reference](#voice-command-reference)
4. [Technical Architecture](#technical-architecture)
5. [Development Specification](#development-specification)
6. [Project Structure](#project-structure)
7. [Dependencies](#dependencies)
8. [Building the EXE](#building-the-exe)
9. [Installation & Usage](#installation--usage)
10. [Configuration](#configuration)

---

## Overview

### Problem

During periodontal charting, the clinician must:
- Probe each site
- Remove hands from patient to type/click
- Look away from patient to verify entry
- Repeat 6 times per tooth × 28+ teeth = 168+ interruptions

### Solution

VoicePerio is a **standalone overlay application** that:
- Runs as an independent `.exe` - no software integration required
- Listens for spoken pocket depths and indicators
- Types numbers directly into your perio charting software (Dentrix, Open Dental, Eaglesoft, etc.)
- Works with ANY software that accepts keyboard input

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR DESKTOP                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              DENTRIX PERIO CHART                        ││
│  │         (receives typed numbers)                        ││
│  │    ┌───┬───┬───┬───┬───┬───┐                           ││
│  │    │ 3 │ 2 │ 3 │   │   │   │  ← Numbers appear here    ││
│  │    └───┴───┴───┴───┴───┴───┘                           ││
│  └─────────────────────────────────────────────────────────┘│
│                           ▲                                  │
│                           │ Keystrokes                       │
│  ┌─────────────────────────────────────────────────────────┐│
│  │         VOICEPERIO (floating overlay)                   ││
│  │    🎤 "three two three" → Types: 3 [Tab] 2 [Tab] 3      ││
│  └─────────────────────────────────────────────────────────┘│
│                           ▲                                  │
│                       🎤 Voice                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Points

1. **Zero Integration**: VoicePerio never touches your charting software - it only simulates keyboard input
2. **Standalone EXE**: Runs without Python, no installation into Dentrix
3. **Universal**: Works with Dentrix, Open Dental, Eaglesoft, or any software
4. **Offline**: All speech recognition happens locally - HIPAA compliant
5. **Non-Invasive**: Close it anytime, leaves no trace

---

## Features

### Core Features

- **Pocket Depth Entry**: Dictate numbers 0-15, entered with automatic Tab between fields
- **Sequence Entry**: Say "three two three" → enters 3, Tab, 2, Tab, 3
- **Perio Indicators**: Bleeding, suppuration, furcation (I/II/III), mobility (I/II/III), recession
- **Navigation**: Next tooth, previous tooth, quadrant jumps
- **Side Switching**: Facial/buccal, lingual/palatal

### User Interface

- System tray icon (minimize out of the way)
- Small floating indicator showing listening status
- Visual feedback when commands are recognized
- Audio feedback (optional beep on recognition)

---

## Voice Command Reference

### Timing-Based Number Entry (NEW)

VoicePerio uses **timing-based grouping** to intelligently interpret your spoken numbers. Numbers spoken quickly together are entered as a single field value, while pauses indicate moving to the next field.

**Example:** Saying "2, 232, 43, 3, 231" naturally with pauses produces:
| Field | Entered Value |
|-------|---------------|
| 1 | 2 |
| 2 | 232 |
| 3 | 43 |
| 4 | 3 |
| 5 | 231 |

**How it works:**
- Words spoken within 300ms of each other are grouped as ONE field entry
- A pause > 300ms indicates a NEW field entry
- After each entry, the cursor automatically advances to the next field

### Pocket Depths (0-15)

| Say | Enters |
|-----|--------|
| "zero" or "oh" | 0 |
| "one" | 1 |
| "two" | 2 |
| "three" | 3 |
| ... | ... |
| "fifteen" | 15 |

### Number Combinations

| Say (quickly together) | Enters | Then |
|------------------------|--------|------|
| "three two three" | 323 | Advances to next field |
| "four three" | 43 | Advances to next field |
| "two" | 2 | Advances to next field |

*Speak numbers quickly together for multi-digit entries, pause to move to next field.*

### Perio Indicators (Dentrix Enterprise)

| Say | Dentrix Key | Action |
|-----|-------------|--------|
| "bleeding" / "bleed" / "BOP" | B | Marks bleeding on probing |
| "suppuration" / "pus" | S | Marks suppuration |
| "plaque" | A | Opens plaque context menu |
| "calculus" / "tartar" | C | Marks calculus |
| "furcation" / "furca" | G | Opens furcation menu |
| "mobility" / "mobile" | M | Marks mobility |
| "bone loss" / "bone" | L | Opens bone loss menu |

### Navigation (Dentrix Enterprise)

| Say | Dentrix Key | Action |
|-----|-------------|--------|
| "next" / "advance" | Enter | Move to next field |
| "previous" / "back" | Page Up | Move to previous field |
| "skip" / "missing" | - | Enter "000" and advance |
| "skip five" (any number) | - | Skip 5 fields without entering data |
| "home" / "start" | Home | Go to first position |
| "switch" / "flip" | * | Toggle Facial/Lingual |
| "facial" / "buccal" | - | Switch to facial side |
| "lingual" / "palatal" | - | Switch to lingual side |

### Actions (Dentrix Enterprise)

| Say | Dentrix Key | Action |
|-----|-------------|--------|
| "save" | Ctrl+S | Save current exam |
| "new exam" | Ctrl+N | Start new exam |
| "open" | Ctrl+O | Open existing exam |
| "print" | F3 | Open print dialog |
| "undo" / "correction" | Ctrl+Z | Undo last entry |
| "clear" | Delete | Clear current selection |
| "cancel" / "escape" | Escape | Cancel/close dialog |

### App Control

| Say | Action |
|-----|--------|
| "voice perio wake" / "listen" | Start listening |
| "voice perio sleep" / "pause" | Pause listening |
| "voice perio stop" / "exit" | Exit application |

---

## Technical Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        VoicePerio                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Audio      │    │    Vosk      │    │   Command    │   │
│  │   Capture    │───▶│   Speech     │───▶│   Parser     │   │
│  │ (sounddevice)│    │   Engine     │    │              │   │
│  └──────────────┘    └──────────────┘    └──────┬───────┘   │
│                                                  │           │
│                                                  ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Target     │◀───│  Keystroke   │◀───│   Number     │   │
│  │   Window     │    │  Injector    │    │   Sequencer  │   │
│  │  (Dentrix)   │    │ (pyautogui)  │    │              │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  GUI (PyQt6)                          │   │
│  │  [System Tray] [Floating Status] [Settings Panel]    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| Audio Capture | sounddevice | Stream microphone input |
| Speech Engine | Vosk | Offline speech-to-text |
| Command Parser | Custom | Match speech to commands |
| Number Sequencer | Custom | Handle "three two three" → 3,2,3 |
| Keystroke Injector | pyautogui | Type into target window |
| GUI | PyQt6 | System tray + floating indicator |

---

## Development Specification

### Module 1: Audio Capture (`audio_capture.py`)

```python
class AudioCapture:
    """
    Streams audio from microphone to speech engine.
    
    Config:
    - sample_rate: 16000 (Vosk requirement)
    - chunk_size: 4000 samples
    - channels: 1 (mono)
    
    Methods:
    - list_devices() -> List[Dict]
    - set_device(device_id: int)
    - start()
    - stop()
    - get_audio_chunk() -> bytes
    """
```

### Module 2: Speech Engine (`speech_engine.py`)

```python
class SpeechEngine:
    """
    Vosk wrapper for offline speech recognition.
    
    Methods:
    - load_model(path: str)
    - process_audio(chunk: bytes) -> Optional[str]
    - get_partial() -> str
    - set_grammar(words: List[str])  # Constrain to perio vocabulary
    """
```

### Module 3: Command Parser (`command_parser.py`)

```python
class CommandParser:
    """
    Interprets recognized speech as perio commands.
    
    Key Logic:
    - Detect number sequences: "three two three" → [3, 2, 3]
    - Detect single numbers: "four" → [4]
    - Detect indicators: "bleeding" → {action: "keystroke", key: "b"}
    - Detect navigation: "next" → {action: "keystroke", key: "tab"}
    
    Methods:
    - parse(text: str) -> Command
    - is_number_sequence(text: str) -> bool
    - extract_numbers(text: str) -> List[int]
    """
```

### Module 4: Number Sequencer (`number_sequencer.py`)

```python
class NumberSequencer:
    """
    Handles entry of pocket depth sequences.
    
    Workflow:
    1. Receive numbers [3, 2, 3]
    2. Type "3", press Tab
    3. Type "2", press Tab  
    4. Type "3"
    5. Optionally press Tab to advance to next site
    
    Config:
    - inter_number_delay: 50ms
    - tab_after_sequence: True/False
    - advance_key: "tab" (configurable)
    """
```

### Module 5: Action Executor (`action_executor.py`)

```python
class ActionExecutor:
    """
    Sends keystrokes to target window.
    
    Methods:
    - find_target_window(title_pattern: str) -> bool
    - focus_target_window()
    - send_keystroke(key: str)
    - send_key_combo(keys: List[str])
    - type_text(text: str)
    - type_number_sequence(numbers: List[int])
    
    Uses:
    - win32gui for window finding/focusing
    - pyautogui for keystroke injection
    """
```

### Module 6: GUI Manager (`gui_manager.py`)

```python
class GUIManager:
    """
    System tray and floating indicator.
    
    Components:
    - System tray icon with menu
    - Floating indicator (shows: Listening/Paused/Last command)
    - Settings dialog
    
    Methods:
    - show_indicator()
    - hide_indicator()
    - update_status(text: str, color: str)
    - show_command_feedback(command: str)
    """
```

### Module 7: Main Application (`main.py`)

```python
class VoicePerioApp:
    """
    Main controller - wires everything together.
    
    Startup:
    1. Load config
    2. Load Vosk model
    3. Initialize audio capture
    4. Initialize GUI
    5. Start listening loop
    
    Main Loop:
    1. Get audio chunk
    2. Process through Vosk
    3. Parse recognized text
    4. Execute command (type numbers, press keys)
    5. Show feedback
    """
```

---

## Project Structure

```
VoicePerio/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── build.bat                      # Double-click to build EXE
├── .gitignore
│
├── src/
│   └── voiceperio/
│       ├── __init__.py
│       ├── __main__.py            # Entry point
│       ├── main.py                # Main app controller
│       ├── audio_capture.py
│       ├── speech_engine.py
│       ├── command_parser.py
│       ├── number_sequencer.py
│       ├── action_executor.py
│       ├── config_manager.py
│       │
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── gui_manager.py
│       │   ├── system_tray.py
│       │   ├── floating_indicator.py
│       │   ├── settings_dialog.py
│       │   └── resources/
│       │       ├── icon.ico
│       │       ├── icon_listening.png
│       │       └── icon_paused.png
│       │
│       ├── commands/
│       │   └── default_commands.json
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py
│           └── window_utils.py
│
├── models/
│   └── vosk-model-small-en-us/    # Downloaded separately
│
├── installer/
│   ├── voiceperio.spec            # PyInstaller config
│   └── version_info.txt
│
├── scripts/
│   └── download_model.py
│
└── tests/
    ├── test_command_parser.py
    └── test_number_sequencer.py
```

---

## Dependencies

### requirements.txt

```
vosk>=0.3.45           # Offline speech recognition
sounddevice>=0.4.6     # Audio capture
pyautogui>=0.9.54      # Keystroke injection
pynput>=1.7.6          # Global hotkeys
PyQt6>=6.5.0           # GUI
numpy>=1.24.0          # Audio processing
keyboard>=0.13.5       # Hotkey support (Windows)
pywin32>=306           # Window management
rapidfuzz>=3.2.0       # Fuzzy string matching
```

---

## Building the EXE

### Quick Build (Windows)

```
Double-click build.bat
```

This will:
1. Create virtual environment
2. Install dependencies
3. Download Vosk model (if needed)
4. Build `VoicePerio.exe`

Output: `dist/VoicePerio/VoicePerio.exe`

### Build Options

| Command | Description |
|---------|-------------|
| `build.bat` | Full build with all checks |
| `build.bat --quick` | Quick build (skip model download) |
| `build.bat --clean` | Clean and rebuild |
| `build.bat --verify` | Verify existing build |

### Manual Build

```bash
pip install -r requirements.txt
pip install pyinstaller
python scripts/download_model.py
pyinstaller installer/voiceperio.spec --noconfirm
```

### Distribution Package

```
VoicePerio/
├── VoicePerio.exe              # Main executable
├── models/
│   └── vosk-model-small-en-us/ # Required (~40MB)
├── config.json                 # Default configuration
├── README.txt                  # Quick start guide
└── LICENSE.txt                 # MIT License
```

**Total size**: ~100-150MB

### Detailed Documentation

For comprehensive build instructions, troubleshooting, and CI/CD integration, see:
- [BUILD.md](BUILD.md) - Complete build process documentation
- [DEPLOY.md](DEPLOY.md) - Distribution and deployment guide

---

## Installation & Usage

### For End Users

1. Download and extract VoicePerio
2. Run `VoicePerio.exe`
3. Open your perio charting software (Dentrix, etc.)
4. Click into the first probing depth field
5. Start dictating!

### User Interface (No Command Prompt Needed)

VoicePerio runs entirely in the background with a refined GUI interface:

#### System Tray Icon
- Located in Windows system tray (bottom-right of taskbar)
- Right-click for menu: Show/Hide, Settings, Pause/Resume, Exit
- Left-click to access quick actions
- Shows listening status via icon indicator

#### Floating Indicator Window
- **Semi-transparent window** that floats above Dentrix
- Shows **listening status** (Listening, Paused, Sleeping, Ready)
- Displays **last recognized command** with real-time feedback
- **Fully draggable** - position it anywhere on screen
- **Auto-minimizes** when not needed
- Color-coded indicators:
  - 🎤 Green: Listening (actively recognizing speech)
  - Orange: Paused (not listening)
  - Gray: Sleeping (backgrounded)
  - White: Ready (startup state)

#### Settings Dialog
- Access via system tray menu → Settings
- Configure microphone input device
- Adjust pause threshold for number grouping (default: 300ms)
- Set keystroke delay for reliability
- Adjust floating indicator opacity
- Save target window title (Dentrix, Open Dental, etc.)

### Typical Workflow

1. **Start VoicePerio** - small icon appears in system tray
   - Floating indicator shows in corner of screen
   - Status says "Listening" (green with 🎤)

2. **Open Dentrix** perio chart for patient
   - No need to interact with VoicePerio window
   - Floating indicator stays visible but out of way

3. **Click** into first probing field (tooth 1, DB facial)

4. **Just dictate naturally** - no console needed:
   - "three two three" → enters 323, advances
   - "bleeding" → marks BOP
   - "skip 5" → skips 5 fields
   - "next" → advances to next site
   - etc.

5. **Floating indicator** updates in real-time showing what was recognized

6. **When done** - say "save" to save the chart

7. **Close VoicePerio** via system tray menu → Exit

### Tips for Best Results

- **Speak naturally** - don't rush or over-enunciate
- **Use natural pauses** between different field entries
  - "two three two" (quick) = one field with "232"
  - "two [pause] three two" (with pause) = two separate fields
- **The floating indicator is always visible** for feedback
  - Don't try to cover it - it stays on top
  - Drag it to position that doesn't interfere with Dentrix
- **Pause the app** when not charting (system tray → Pause)
  - Reduces CPU usage
  - Resume with system tray menu or say "wake"
- **Correct mistakes** with "correction" or "scratch that"
- **System tray menu** accessible anytime for quick access

---

## Configuration

### Config File Location

`%APPDATA%/VoicePerio/config.json`

### Key Settings

```json
{
  "audio": {
    "device_id": null
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
    "toggle_listening": "ctrl+shift+v"
  }
}
```

### Customizing for Your Software

If using Open Dental, Eaglesoft, or other software:

1. Open Settings (right-click tray icon)
2. Change "Target Window" to match your software's window title
3. Test with a sample chart
4. Adjust keystroke delay if entries are missed

---

## Claude Code Development Instructions

Build this application in the following phases:

### Phase 1: Core Infrastructure
1. Set up project structure
2. Implement `config_manager.py`
3. Implement `logger.py`
4. Create `main.py` skeleton

### Phase 2: Audio & Speech
5. Implement `audio_capture.py`
6. Download Vosk model
7. Implement `speech_engine.py`
8. Test: speak numbers, verify recognition

### Phase 3: Command Processing
9. Implement `command_parser.py`
10. Implement `number_sequencer.py`
11. Test: "three two three" → [3, 2, 3]

### Phase 4: Keystroke Injection
12. Implement `window_utils.py`
13. Implement `action_executor.py`
14. Test: inject keystrokes into Notepad

### Phase 5: GUI
15. Implement `system_tray.py`
16. Implement `floating_indicator.py`
17. Implement `settings_dialog.py`
18. Implement `gui_manager.py`

### Phase 6: Integration
19. Wire all components in `main.py`
20. Add global hotkey support
21. End-to-end testing

### Phase 7: Build & Package
22. Finalize PyInstaller spec
23. Build EXE
24. Test on clean Windows machine

---

## License

MIT License

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Numbers not recognized | Speak more clearly, check microphone |
| Keystrokes not appearing | Verify Dentrix is focused, run as admin if needed |
| Wrong numbers entered | Say "correction" to undo, re-dictate |
| App won't start | Check models/ folder has Vosk model |
| High CPU usage | Normal during listening; use "sleep" when not charting |
