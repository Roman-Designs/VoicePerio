# VoicePerio GUI Guide

## Overview

VoicePerio does **NOT** require a command prompt window. The entire application runs with a polished, professional GUI that stays out of your way while you work in Dentrix.

## GUI Components

### 1. System Tray Icon

**Location:** Windows system tray (bottom-right of taskbar)

**What it does:**
- Shows the application is running
- Provides quick access to controls
- Remains accessible at all times

**Right-click menu:**
```
┌─ Show/Hide          (toggle floating indicator)
├─ Settings           (open configuration dialog)
├─ Pause Listening    (or "Resume Listening" when paused)
├─ ─────────────────
└─ Exit               (close application)
```

**Icons indicate status:**
- 🎤 Blue icon = Listening
- ⏸️ Orange icon = Paused
- 😴 Gray icon = Sleeping

### 2. Floating Indicator Window

**Location:** Floats on screen (default: bottom-right corner)

**Appearance:**
```
╔═══════════════════════════════╗
║     🎤 Listening              ║
║                               ║
║  Command: three two three      ║
║                               ║
║                            ✕  ║
╚═══════════════════════════════╝
```

**Features:**
- **Status Display** (top)
  - Shows: Listening, Paused, Sleeping, Ready
  - Color-coded: Green (listening), Orange (paused), Gray (sleeping)
  - 🎤 emoji appears when actively listening

- **Command Display** (middle)
  - Shows last recognized command in real-time
  - Auto-clears after 3 seconds
  - Helps confirm what was heard

- **Close Button** (bottom-right)
  - Click to hide the indicator
  - Reopen from system tray menu

**Interaction:**
- **Drag** the window by clicking and dragging anywhere
- **Click close** (✕) to minimize to system tray
- **Always stays on top** so you can see it while working
- **Adjustable opacity** via Settings dialog

### 3. Settings Dialog

**Access:** Right-click system tray → Settings

```
┌─ VoicePerio Settings ──────────────────┐
│                                        │
│ Audio Settings                         │
│ ├─ Microphone Device: [Dropdown]       │
│ └─ Test microphone [Button]            │
│                                        │
│ Recognition Settings                  │
│ ├─ Pause Threshold: 300 ms             │
│ │  (gap > 300ms = new field)           │
│ └─ Keystroke Delay: 50 ms              │
│                                        │
│ Keystroke Settings                    │
│ ├─ Advance Key: [Enter / Tab]          │
│ └─ Target Window: Dentrix              │
│                                        │
│ GUI Settings                          │
│ ├─ Floating Indicator Opacity: 0.9    │
│ ├─ Show Floating Indicator: ☑ Checked │
│ └─ Show Command Feedback: ☑ Checked   │
│                                        │
│  [Cancel]  [Save]                     │
└────────────────────────────────────────┘
```

**Key Settings:**

| Setting | Purpose | Default |
|---------|---------|---------|
| Microphone Device | Select audio input | System default |
| Pause Threshold | Gap between words for field separation | 300ms |
| Keystroke Delay | Delay between characters typed | 50ms |
| Advance Key | Key to press after each field entry | Enter |
| Target Window | Name of charting software window | Dentrix |
| Indicator Opacity | Transparency of floating window (0.0-1.0) | 0.9 |

## Workflow Example

### Scenario: Enter perio readings for tooth #8 (upper right)

```
1. VoicePerio running - system tray icon visible
   ✓ Floating indicator shows "🎤 Listening"

2. Open Dentrix, navigate to patient's perio chart
   ✓ Click into first field (tooth #8, Distal Buccal)

3. Say: "three two four"
   ✓ Floating indicator flashes: "Command: three two four"
   ✓ Field shows "324", cursor moves to next field

4. Say: "bleeding"
   ✓ Floating indicator flashes: "Command: bleeding"
   ✓ BOP marked, indicator clears after 3 seconds

5. Say: "next"
   ✓ Cursor advances to Buccal field
   ✓ Ready for next reading

6. Say: "three"
   ✓ Field shows "3", cursor advances

7. (Continue charting...)

8. After completing chart, say: "save"
   ✓ Chart saved (Ctrl+S)
```

## Status Indicators

### Floating Indicator Colors

| Status | Color | Meaning |
|--------|-------|---------|
| Listening | 🟢 Green | App is active and recognizing speech |
| Paused | 🟠 Orange | App is paused, not listening |
| Sleeping | ⚪ Gray | App is running but backgrounded |
| Ready | ⚪ White | App is starting up or idle |

### System Tray Icon

| Icon | Meaning |
|------|---------|
| 🎤 Blue | Listening/Ready |
| ⏸️ Orange | Paused |
| 😴 Gray | Sleeping |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+V` | Toggle listening on/off |
| `Ctrl+Shift+P` | Pause/Resume listening |
| `Ctrl+Shift+S` | Sleep/Wake app |
| `Ctrl+Shift+X` | Exit application |

*Can be customized in config file*

## Positioning the Floating Indicator

### Initial Position
- Appears in **bottom-right corner** of screen
- Sized to be visible but not intrusive (~250×100 pixels)

### Moving the Indicator
1. Click and hold on the indicator window
2. Drag to desired position
3. Release to drop in new location
4. Position is remembered between sessions

### Recommended Positions
- **Upper-right:** Out of way, visible over Dentrix
- **Lower-right:** Default, works well with most setups
- **Left side:** If Dentrix window is fullscreen

### Show/Hide
- **Show:** Right-click system tray → Show/Hide
- **Hide:** Click ✕ button on indicator, or hide from system tray
- **Toggle:** Say "hide" or use keyboard shortcut (if enabled)

## Troubleshooting Display Issues

### Floating Indicator Won't Show
1. Check system tray for VoicePerio icon
2. Right-click → Settings
3. Verify "Show Floating Indicator" is checked
4. Restart VoicePerio

### Floating Indicator Blocked by Other Windows
- Drag indicator to different position
- Or disable "Always on Top" (if you prefer) via settings
- Adjust opacity so you can see through it

### Indicator Position Lost After Restart
- Positions are saved in config file
- If position is off-screen, manually edit config or drag window to visible position

### Command Text Not Updating
- Ensure "Show Command Feedback" is checked in settings
- Check if "Pause Listening" is active (disable via system tray)

## Tips & Tricks

### Optimization Tips
1. **Minimize floating indicator** when not needed to reduce screen clutter
2. **Adjust opacity** so indicator is visible but transparent (0.7-0.8)
3. **Position indicator** near your vision line so you can see feedback easily

### Efficiency Tips
1. **Keep system tray visible** so you can quickly pause/resume
2. **Use keyboard shortcut** Ctrl+Shift+P to quickly pause between patients
3. **Customize advance key** - Tab works better for some workflows than Enter

### Microphone Tips
1. **Position microphone** 6-12 inches from mouth
2. **Adjust pause threshold** higher (400ms) if you naturally pause between numbers
3. **Test microphone** via Settings dialog before charting

## Customization

### Via Settings Dialog
- Microphone device selection
- Threshold adjustments
- Opacity settings
- Window target selection

### Via Config File
`%APPDATA%/VoicePerio/config.json`

```json
{
  "gui": {
    "show_floating_indicator": true,
    "indicator_opacity": 0.9,
    "show_command_feedback": true,
    "indicator_position": [1670, 670]
  },
  "behavior": {
    "pause_threshold_ms": 300,
    "keystroke_delay_ms": 50,
    "advance_key": "enter"
  }
}
```

## Support

**System Tray Right-Click Menu** always provides access to:
- ✓ Quick Settings
- ✓ Pause/Resume
- ✓ Exit (graceful shutdown)

**If issues occur:**
1. Check floating indicator for error messages
2. Review log file: `%APPDATA%/VoicePerio/voiceperio.log`
3. Try restarting the application
4. Check microphone connection and permissions

---

**Remember:** You should never need to interact with a command prompt. The GUI handles everything!
