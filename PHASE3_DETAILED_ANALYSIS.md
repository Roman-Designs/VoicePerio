# PHASE 3 ANALYSIS: Command Processing Implementation Guide

**Created**: January 16, 2026  
**Status**: Ready for Implementation  
**Complexity**: HIGH - Core speech-to-command conversion

---

## Table of Contents
1. Executive Summary
2. CommandParser Current State
3. Command JSON Structure
4. NumberSequencer Review
5. Phase 2 Integration
6. Missing Implementation
7. Critical Issues
8. Test Requirements
9. Implementation Plan

---

## 1. EXECUTIVE SUMMARY

Phase 3 converts speech recognition output into executable commands. It's the bridge between Phase 2 (speech input) and Phase 4 (keystroke output).

### Current Status
- **command_parser.py**: 132 lines, skeleton with stubs
- **number_sequencer.py**: 89 lines, COMPLETE
- **default_commands.json**: 160 lines, COMPLETE (39 commands)
- **Phase 2 modules**: COMPLETE with one critical bug

### What's Complete
✓ Command loading from JSON  
✓ Fuzzy matching infrastructure  
✓ Number sequencer execution  
✓ Command definitions database  

### What's Missing
✗ Command parsing logic (parse method)  
✗ Number extraction  
✗ Number sequence detection  
✗ Command routing  
✗ Multi-keyword handling  

---

## 2. COMMANDPARSER CURRENT STATE

**File**: `src/voiceperio/command_parser.py`

### Already Implemented
```python
class CommandParser:
    def __init__(self, commands_file=None)          # ✓ Working
    def load_commands(filepath)                     # ✓ Working
    def fuzzy_match(text, candidates, threshold)   # ✓ Working
```

### Stubs (TODO)
```python
    def parse(text)                                 # ✗ Empty (line 81-82)
    def is_number_sequence(text)                    # ✗ Empty (line 94-95)
    def extract_numbers(text)                       # ✗ Empty (line 107-108)
```

### Command Class
Simple container:
```python
class Command:
    action: str              # Type of action
    params: Dict[str, Any]   # Action parameters
```

### What Works
- JSON loading with error handling
- Fuzzy string matching using rapidfuzz (threshold 80/100)
- Comprehensive logging

### What Doesn't Work
- `parse()` returns None always (stub)
- No number detection
- No command routing
- No actual parsing logic

---

## 3. DEFAULT_COMMANDS.JSON STRUCTURE

**File**: `src/voiceperio/commands/default_commands.json`

### Overview
5 categories, 39 total commands, 20+ aliases

### Category 1: NUMBERS (16 entries)
```json
"numbers": {
  "zero": 0,
  "oh": 0,
  "one": 1,
  ...
  "fifteen": 15
}
```

**Key Points**:
- Simple key→value mapping
- "zero" and "oh" both map to 0
- Range: 0-15 (pocket depth in mm)
- Used for both single numbers and sequences
- Example: "three" → 3 or "three two three" → [3, 2, 3]

### Category 2: PERIO_INDICATORS (7 commands)

**Simple Keystroke (1 key)**:
```json
"bleeding": {
  "aliases": ["bleed", "bop"],
  "action": "keystroke",
  "key": "b"
},
```

**With Classes (2 keys)**:
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
```

**All Indicators**:
1. bleeding → "b"
2. suppuration → "s"
3. plaque → "p"
4. calculus → "c"
5. recession → "r"
6. furcation → "f" + class (1-3)
7. mobility → "m" + class (1-3)

**Examples**:
- "bleeding" → Press 'b'
- "bleed" (alias) → Press 'b'
- "furcation one" → Press 'f', then '1'
- "mobility three" → Press 'm', then '3'

### Category 3: NAVIGATION (8 commands)

**Keystroke Navigation**:
```json
"next": {
  "aliases": ["next tooth"],
  "action": "keystroke",
  "key": "tab"
},
"previous": {
  "aliases": ["back", "prev"],
  "action": "keystroke",
  "key": "shift+tab"
}
```

**Quadrant Jumps**:
```json
"upper_right": {
  "aliases": ["quadrant one", "ur"],
  "action": "jump_quadrant",
  "quadrant": 1
}
```

**Side Switch**:
```json
"facial": {
  "aliases": ["buccal"],
  "action": "switch_side",
  "side": "facial"
}
```

**All Navigation**:
1. next (tab)
2. previous (shift+tab)
3. skip (tab)
4. upper_right/quadrant_one (jump 1)
5. upper_left/quadrant_two (jump 2)
6. lower_left/quadrant_three (jump 3)
7. lower_right/quadrant_four (jump 4)
8. facial/buccal (switch facial)
9. lingual/palatal (switch lingual)

### Category 4: ACTIONS (5 commands)

```json
"enter": {
  "aliases": ["okay", "ok"],
  "action": "keystroke",
  "key": "enter"
},
"save": {
  "aliases": [],
  "action": "keystroke",
  "key": "ctrl+s"
}
```

**All Actions**:
1. enter → Enter
2. cancel → Escape
3. save → Ctrl+S
4. undo → Ctrl+Z
5. correction → Ctrl+Z (same as undo)

### Category 5: APP_CONTROL (3 commands)

```json
"wake": {
  "aliases": ["voice perio wake", "start listening"],
  "action": "app_control",
  "command": "wake"
}
```

**Special Handling**:
- These don't generate keystrokes
- Handled by application logic
- Wake: Resume listening
- Sleep: Pause listening
- Stop: Exit application

---

## 4. NUMBERSEQUENCER REVIEW

**File**: `src/voiceperio/number_sequencer.py`

### Status: ✅ COMPLETE AND READY

### Constructor
```python
NumberSequencer(
    inter_number_delay_ms=50,      # Delay between entries
    tab_after_sequence=True,       # Press Tab after last number
    advance_key="tab"              # Key between numbers
)
```

### Core Method
```python
def sequence_numbers(numbers: List[int]) -> bool:
    """Type sequence like [3, 2, 3]"""
```

### Execution Example
Input: `[3, 2, 3]`

Output:
1. Type "3"
2. Wait 50ms
3. Press Tab
4. Type "2"
5. Wait 50ms
6. Press Tab
7. Type "3"
8. Wait 50ms
9. Press Tab (final tab)

**Result in Dentrix**:
```
Field 1: 3
Field 2: 2
Field 3: 3
```

### Integration Points
- Requires `set_action_executor(executor)` before use
- Calls `executor.type_text()` and `executor.send_keystroke()`
- Complete, tested, and ready to use

### What Phase 3 Needs to Do
1. Parse "three two three" text
2. Extract [3, 2, 3]
3. Create Command(action="number_sequence", numbers=[3, 2, 3])
4. Phase 4 handles calling `sequencer.sequence_numbers()`

---

## 5. PHASE 2 INTEGRATION

### Phase 2 Output

**SpeechEngine delivers**:
```python
recognized_text = "three two three"  # or "bleeding", "next", etc.
```

**Properties**:
- Lowercase
- Trimmed
- ASCII only
- Complete phrases
- Real-time partial results available

### Data Flow
```
Microphone Audio
    ↓
AudioCapture.get_audio_chunk()
    ↓
Raw audio bytes (16kHz, mono, int16)
    ↓
SpeechEngine.process_audio(chunk)
    ↓
Recognized text: "three two three"
    ↓
CommandParser.parse(text)
    ↓
Command(action="number_sequence", numbers=[3, 2, 3])
    ↓
ActionExecutor.execute()
    ↓
Dentrix receives keystrokes
```

### Critical Bug in Phase 2
**Location**: `speech_engine.py` line 99

```python
# WRONG - gets confidence score
text = ' '.join([w['conf'] for w in result_dict['result']])

# CORRECT - gets actual word (verify field name in Vosk)
text = ' '.join([w['result'] for w in result_dict['result']])
```

**Impact**: CommandParser receives garbage like "0.95 0.87 0.91" instead of "three two three"

**Status**: Must be fixed before Phase 3 testing

---

## 6. MISSING IMPLEMENTATION

### Method 1: `extract_numbers(text: str) -> List[int]`

**Purpose**: Convert number words to integers

**Examples**:
```
"three two three" → [3, 2, 3]
"four" → [4]
"zero" → [0]
"oh" → [0]
"five three two one" → [5, 3, 2, 1]
```

**Algorithm**:
```python
def extract_numbers(self, text: str) -> List[int]:
    # 1. Split by spaces
    words = text.split()
    
    # 2. Look up each word in numbers database
    numbers = []
    for word in words:
        if word in self.commands_db["numbers"]:
            numbers.append(self.commands_db["numbers"][word])
    
    # 3. Return list
    return numbers
```

**Validation**:
- Empty result if no numbers found
- Only 0-15 valid
- Log warnings for out-of-range values

### Method 2: `is_number_sequence(text: str) -> bool`

**Purpose**: Detect if text is a number sequence

**Examples**:
```
"three" → True (even single number)
"four" → True
"three two three" → True
"bleeding" → False
"next" → False
"three bleed three" → False (mixed)
```

**Algorithm**:
```python
def is_number_sequence(self, text: str) -> bool:
    # 1. Split by spaces
    words = text.sp
