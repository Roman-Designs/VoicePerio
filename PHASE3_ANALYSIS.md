# Phase 3 (Command Processing) - Implementation Analysis

**Date**: January 16, 2026  
**Status**: Ready for Implementation  
**Complexity**: HIGH - Core business logic for command parsing

---

## Executive Summary

Phase 3 is the critical command processing layer that converts Vosk speech recognition output into executable commands. This phase bridges **Phase 2 (speech input)** and **Phase 4 (keystroke output)**.

### Current State
- ✓ **command_parser.py**: Skeleton with fuzzy matching support, **core parsing logic TODO**
- ✓ **number_sequencer.py**: Complete implementation with proper integration
- ✓ **default_commands.json**: Full command definition structure (5 categories, 40+ commands)
- ✓ **Phase 2 modules**: Fully functional audio capture and speech recognition

### What's Missing
- Command parsing logic in `CommandParser.parse()`
- Number sequence detection
- Number extraction from text
- Command matching logic with fuzzy matching
- Indicator command handling
- Navigation command handling
- App control command handling

---

## 1. CommandParser Stub Analysis

### File: `src/voiceperio/command_parser.py`

#### Current State
```python
class CommandParser:
    def __init__(self, commands_file: Optional[str] = None)
    def load_commands(self, filepath: str) -> bool      # IMPLEMENTED ✓
    def parse(self, text: str) -> Optional[Command]     # TODO - STUB
    def is_number_sequence(self, text: str) -> bool     # TODO - STUB
    def extract_numbers(self, text: str) -> List[int]   # TODO - STUB
    def fuzzy_match(...)                                # IMPLEMENTED ✓
```

#### What's Implemented
1. **Command Loading** - `load_commands()` reads JSON and populates `self.commands_db`
2. **Command Class** - Simple container with action + params
3. **Fuzzy Matching** - `fuzzy_match()` using rapidfuzz (score threshold 80/100)
4. **Logging** - All methods have error logging

#### What's NOT Implemented
1. **Main Parse Logic** - The `parse()` method is completely empty (line 81-82: `pass`)
   - No number detection
   - No command matching
   - No alias resolution
   - No return of Command objects

2. **Number Sequence Detection** - `is_number_sequence()` is stub
   - Needs to detect sequences like "three two three"
   - Must distinguish from single numbers

3. **Number Extraction** - `extract_numbers()` is stub
   - Must convert "three" → 3, "fifteen" → 15, etc.
   - Must handle "zero" and "oh" → 0
   - Must validate range 0-15

### Expected Behavior (from README)
```
Input:  "three two three"  →  Output: Command(action="number_sequence", numbers=[3, 2, 3])
Input:  "four"             →  Output: Command(action="number_sequence", numbers=[4])
Input:  "bleeding"         →  Output: Command(action="keystroke", key="b")
Input:  "next"             →  Output: Command(action="keystroke", key="tab")
Input:  "quadrant one"     →  Output: Command(action="jump_quadrant", quadrant=1)
```

---

## 2. Command Definition Structure (default_commands.json)

### File: `src/voiceperio/commands/default_commands.json` (160 lines)

#### Structure Overview
```json
{
  "numbers": { ... },              // 16 entries (0-15, including "zero" and "oh")
  "perio_indicators": { ... },     // 7 categories (bleeding, suppuration, plaque, etc.)
  "navigation": { ... },           // 8 navigation commands
  "actions": { ... },              // 5 action commands
  "app_control": { ... }           // 3 app control commands
}
```

### 2.1 Numbers Category (16 entries)
```json
"numbers": {
  "zero": 0,
  "oh": 0,
  "one": 1,
  "two": 2,
  ...
  "fifteen": 15
}
```
**Key Points:**
- Simple key-value mapping
- Two ways to say zero: "zero" and "oh"
- Range: 0-15 (pocket depth 0-15mm)
- Used for both single numbers and sequences

### 2.2 Perio Indicators Category (7 commands)

#### Simple Keystroke Indicators (no parameters)
```json
"bleeding": {
  "aliases": ["bleed", "bop"],
  "action": "keystroke",
  "key": "b"
},
"suppuration": {
  "aliases": ["pus"],
  "action": "keystroke",
  "key": "s"
},
"plaque": {
  "aliases": [],
  "action": "keystroke",
  "key": "p"
},
"calculus": {
  "aliases": ["tartar"],
  "action": "keystroke",
  "key": "c"
},
"recession": {
  "aliases": [],
  "action": "keystroke",
  "key": "r"
}
```

#### Complex Indicators (with class/severity)
```json
"furcation": {
  "aliases": ["furca"],
  "action": "multi_keystroke",
  "key": "f",
  "classes": {
    "one": "1",
    "two": "2",
    "three": "3"
  }
},
"mobility": {
  "aliases": ["mobile"],
  "action": "multi_keystroke",
  "key": "m",
  "classes": {
    "one": "1",
    "two": "2",
    "three": "3"
  }
}
```

**Implementation Notes:**
- `multi_keystroke` means: press key, then press class number
- Example: "furcation two" → keystroke 'f', then keystroke '2'
- Requires detecting the class number after the indicator

### 2.3 Navigation Category (8 commands)
```json
"navigation": {
  "next": {
    "aliases": ["next tooth"],
    "action": "keystroke",
    "key": "tab"
  },
  "previous": {
    "aliases": ["back", "prev"],
    "action": "keystroke",
    "key": "shift+tab"
  },
  "skip": {
    "aliases": ["missing"],
    "action": "keystroke",
    "key": "tab"
  },
  "upper_right": {
    "aliases": ["quadrant one", "ur"],
    "action": "jump_quadrant",
    "quadrant": 1
  },
  "upper_left": {
    "aliases": ["quadrant two", "ul"],
    "action": "jump_quadrant",
    "quadrant": 2
  },
  "lower_left": {
    "aliases": ["quadrant three", "ll"],
    "action": "jump_quadrant",
    "quadrant": 3
  },
  "lower_right": {
    "aliases": ["quadrant four", "lr"],
    "action": "jump_quadrant",
    "quadrant": 4
  },
  "facial": {
    "aliases": ["buccal"],
    "action": "switch_side",
    "side": "facial"
  },
  "lingual": {
    "aliases": ["palatal"],
    "action": "switch_side",
    "side": "lingual"
  }
}
```

**Key Features:**
- Simple tab/shift+tab for next/previous
- Jump commands store quadrant number (1-4)
- Side switch stores side name ("facial" or "lingual")

### 2.4 Actions Category (5 commands)
```json
"actions": {
  "enter": {
    "aliases": ["okay", "ok"],
    "action": "keystroke",
    "key": "enter"
  },
  "cancel": {
    "aliases": ["escape", "esc"],
    "action": "keystroke",
    "key": "escape"
  },
  "save": {
    "aliases": [],
    "action": "keystroke",
    "key": "ctrl+s"
  },
  "undo": {
    "aliases": [],
    "action": "keystroke",
    "key": "ctrl+z"
  },
  "correction": {
    "aliases": ["scratch that", "scratch"],
    "action": "keystroke",
    "key": "ctrl+z"
  }
}
```

### 2.5 App Control Category (3 commands)
```json
"app_control": {
  "wake": {
    "aliases": ["voice perio wake", "start listening"],
    "action": "app_control",
    "command": "wake"
  },
  "sleep": {
    "aliases": ["voice perio sleep", "pause", "voice perio pause"],
    "action": "app_control",
    "command": "sleep"
  },
  "stop": {
    "aliases": ["voice perio stop", "exit"],
    "action": "app_control",
    "command": "stop"
  }
}
```

**Key Points:**
- These don't generate keystrokes
- Handled by application logic (pause listening, exit, etc.)

### Summary of JSON Structure

| Category | Count | Action Types | Special Features |
|----------|-------|--------------|------------------|
| Numbers | 16 | (values) | 0-15, alternate names |
| Indicators | 7 | keystroke, multi_keystroke | Some have class variations |
| Navigation | 8 | keystroke, jump_quadrant, switch_side | Quadrant/side params |
| Actions | 5 | keystroke | Key combos (ctrl+s) |
| App Control | 3 | app_control | Custom command param |
| **TOTAL** | **39** | - | - |

---

## 3. NumberSequencer Implementation Review

### File: `src/voiceperio/number_sequencer.py` (89 lines)

#### Status: ✅ COMPLETE

### Implementation Details

#### Constructor
```python
def __init__(
    self,
    inter_number_delay_ms: int = 50,
    tab_after_sequence: bool = True,
    advance_key: str = "tab"
):
```
- **inter_number_delay_ms**: 50ms between numbers (default)
- **tab_after_sequence**: Press Tab after all numbers (default True)
- **advance_key**: Key pressed between numbers (default "tab")

#### Core Method: `sequence_numbers()`
```python
def sequenc
