# Phase 2 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
cd C:\Users\rdoro\Desktop\Github\ChartAssist
pip install -r requirements.txt
```

This installs all required packages including:
- vosk (speech recognition)
- sounddevice (audio capture)
- numpy (numerical operations)

### Step 2: Download Vosk Model (1-2 minutes)

```bash
python scripts/download_model.py
```

This downloads and extracts the ~40MB speech model to `models/vosk-model-small-en-us/`

**Expected output:**
```
======================================================================
Vosk Model Download Script
======================================================================
...
✓ Vosk model successfully installed at ...
```

### Step 3: Verify Installation (1 minute)

```bash
python tests/test_audio_speech_integration.py
```

This runs all Phase 2 tests. You should see:
```
✓ Audio Capture test PASSED
✓ Speech Engine test PASSED
✓ Integration test PASSED
✓ ConfigManager test PASSED

Total: 4/4 tests passed

✓ ALL TESTS PASSED!
```

## What Works Now

✓ **Microphone Input**: Your computer's microphone is now accessible
✓ **Audio Capture**: Real-time audio streaming at 16kHz mono
✓ **Speech Recognition**: Offline voice-to-text using Vosk
✓ **Partial Results**: Real-time feedback as you speak

## Quick Test: Listen and Recognize

Create a simple test script `test_voice.py`:

```python
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from voiceperio.audio_capture import AudioCapture
from voiceperio.speech_engine import SpeechEngine
import time

# Setup
audio = AudioCapture()
engine = SpeechEngine()

# Load model
print("Loading model...")
if not engine.load_model("models/vosk-model-small-en-us"):
    print("Failed to load model!")
    exit(1)

# Start recording
print("Starting audio capture...")
audio.start()

# Process audio
print("Listening for 5 seconds. Try saying 'hello' or numbers...")
print("-" * 50)

start = time.time()
while time.time() - start < 5:
    chunk = audio.get_audio_chunk()
    if chunk:
        result = engine.process_audio(chunk)
        partial = engine.get_partial()
        
        if partial:
            print(f"Heard: {partial}")

audio.stop()
print("-" * 50)
print("Done!")
```

Run it:
```bash
python test_voice.py
```

## Common Issues & Solutions

### "No audio devices found"
**Problem:** Microphone not detected
**Solution:** 
1. Check microphone in Windows Settings → Sound settings
2. Try plugging in USB microphone
3. Restart Python/terminal and try again

### "Failed to load Vosk model"
**Problem:** Model not downloaded or corrupted
**Solution:**
```bash
# Re-download the model
python scripts/download_model.py
```

### "No speech recognized"
**Problem:** Microphone too far away or too quiet
**Solution:**
1. Speak closer to microphone (6 inches)
2. Speak clearly and at normal volume
3. Try in a quiet room
4. Check microphone levels in Windows

### Model download is slow
**Problem:** Large file (~40MB) on slow connection
**Solution:**
1. Be patient (can take 5-10 minutes on slow connection)
2. Try again if interrupted

## What's Next (Phase 3)

Once Phase 2 is working:
1. Parser will convert speech to commands
2. "three two three" → Extract numbers [3, 2, 3]
3. "bleeding" → Mark indicator
4. "next" → Navigate to next tooth

## File Structure After Setup

```
VoicePerio/
├── src/voiceperio/
│   ├── audio_capture.py       ← Captures microphone audio
│   ├── speech_engine.py        ← Recognizes speech
│   ├── config_manager.py       ← Manages settings
│   └── utils/
│       └── logger.py           ← Logging
├── models/
│   └── vosk-model-small-en-us/ ← Downloaded model (~40MB)
├── scripts/
│   └── download_model.py       ← Model download script
├── tests/
│   └── test_audio_speech_integration.py ← Tests
└── requirements.txt            ← Dependencies
```

## Testing Phase 2 Components

### Test 1: List Audio Devices

```python
from src.voiceperio.audio_capture import AudioCapture

audio = AudioCapture()
devices = audio.list_devices()

for device in devices:
    print(f"Device {device['id']}: {device['name']}")
```

### Test 2: Test Audio Capture

```python
from src.voiceperio.audio_capture import AudioCapture
import time

audio = AudioCapture()
audio.start()

print("Recording for 2 seconds...")
for _ in range(100):
    chunk = audio.get_audio_chunk()
    if chunk:
        print(f"Got chunk: {len(chunk)} bytes")
    time.sleep(0.02)

audio.stop()
```

### Test 3: Test Speech Recognition

```python
from src.voiceperio.speech_engine import SpeechEngine

engine = SpeechEngine()
engine.load_model("models/vosk-model-small-en-us")

# Now use with AudioCapture (see integration test)
```

## Performance Notes

- **CPU Usage**: 5-15% while recording/processing
- **Memory**: ~50-60MB total (mostly model)
- **Latency**: ~100-150ms end-to-end
- **Model Loading**: Takes 2-3 seconds on first use

## Key Classes

### AudioCapture
```python
audio = AudioCapture()
devices = audio.list_devices()        # Get available devices
audio.set_device(0)                   # Select device
audio.start()                         # Start recording
chunk = audio.get_audio_chunk()       # Get audio data
audio.stop()                          # Stop recording
```

### SpeechEngine
```python
engine = SpeechEngine()
engine.load_model("path/to/model")   # Load Vosk model
result = engine.process_audio(chunk)  # Process audio
partial = engine.get_partial()        # Get partial result
engine.set_grammar(["words"])         # Optional vocabulary
engine.reset()                        # Reset state
```

## Documentation

For complete documentation, see:
- `PHASE2_IMPLEMENTATION.md` - Full API and technical details
- `README.md` - Project overview
- `src/voiceperio/audio_capture.py` - Source code with docstrings
- `src/voiceperio/speech_engine.py` - Source code with docstrings

## Success Criteria

Phase 2 is working when you can:
1. ✓ List audio devices from your microphone
2. ✓ Start and stop audio capture
3. ✓ Get audio chunks from microphone
4. ✓ Load Vosk model without errors
5. ✓ Process audio and get partial recognition results
6. ✓ All 4 integration tests pass

---

**You're now ready to move on to Phase 3: Command Processing!**
