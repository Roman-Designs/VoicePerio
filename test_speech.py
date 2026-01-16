"""Test script to verify speech recognition"""
import sys
import os

# Add the source to path
sys.path.insert(0, "src")

# Test basic imports
print("Testing imports...")
try:
    from voiceperio.speech_engine import SpeechEngine
    print("✓ SpeechEngine imported")
    
    # Test model loading
    print("\nLoading speech model...")
    engine = SpeechEngine()
    
    # Try to find and load model
    model_paths = [
        "dist/VoicePerio/models/vosk-model-small-en-us",
        "models/vosk-model-small-en-us",
    ]
    
    model_loaded = False
    for model_path in model_paths:
        if os.path.exists(model_path):
            print(f"✓ Found model at: {model_path}")
            if engine.load_model(model_path):
                print("✓ Model loaded successfully!")
                model_loaded = True
                break
    
    if not model_loaded:
        print("✗ Could not load model")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("Speech recognition is ready!")
    print("="*50)
    print("\nTo test:")
    print("1. Run: cd dist/VoicePerio && VoicePerio.exe")
    print("2. Say 'three' or 'one two three'")
    print("3. Check if text appears in console")
    print("4. Check if keystrokes are sent")
    print("\nIf no text appears, the issue is in:")
    print("- Audio capture (mic not working)")
    print("- Speech engine (Vosk not processing)")
    print("\nIf text appears but no keystrokes:")
    print("- Command parser issue")
    print("- Target window not found")
    print("- Action executor issue")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
