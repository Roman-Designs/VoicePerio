#!/usr/bin/env python3
"""
Integration Test for Audio Capture and Speech Engine (Phase 2)

Tests the audio capture and speech recognition components working together.
This is a basic integration test that verifies:
1. Audio capture can be initialized and list devices
2. Audio stream can start and stop
3. Speech engine can load Vosk model
4. Audio can be processed through the speech engine
"""

import sys
import os
from pathlib import Path
import time
import logging

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from voiceperio.audio_capture import AudioCapture
from voiceperio.speech_engine import SpeechEngine
from voiceperio.config_manager import ConfigManager
from voiceperio.utils.logger import setup_logging


def setup_test_logging():
    """Set up logging for tests."""
    log_file = Path(__file__).parent.parent / "logs" / "test_phase2.log"
    logger = setup_logging(
        log_level=logging.DEBUG,
        log_file=str(log_file),
        console_output=True
    )
    return logger


def test_audio_capture():
    """Test AudioCapture module."""
    print("\n" + "=" * 70)
    print("TEST 1: Audio Capture Module")
    print("=" * 70)
    
    try:
        # Create AudioCapture instance
        print("1. Creating AudioCapture instance...")
        audio = AudioCapture(sample_rate=16000, chunk_size=4000, channels=1)
        print("   ✓ AudioCapture created successfully")
        
        # List devices
        print("2. Listing audio devices...")
        devices = audio.list_devices()
        
        if not devices:
            print("   ✗ No audio devices found!")
            return False
        
        print(f"   ✓ Found {len(devices)} audio device(s):")
        for device in devices:
            print(f"      - Device {device['id']}: {device['name']} ({device['channels']} channels)")
        
        # Set device (use default)
        print("3. Setting audio device to default...")
        if audio.set_device(None):
            print("   ✓ Device set successfully")
        else:
            print("   ⚠ Failed to set device, trying device 0...")
            if audio.set_device(0):
                print("   ✓ Device 0 set successfully")
            else:
                print("   ✗ Could not set any device")
                return False
        
        # Start stream
        print("4. Starting audio capture stream...")
        if not audio.start():
            print("   ✗ Failed to start audio stream")
            return False
        print("   ✓ Audio stream started")
        
        # Try to get audio chunks (brief recording)
        print("5. Capturing audio for 2 seconds...")
        chunks_received = 0
        start_time = time.time()
        
        while time.time() - start_time < 2:
            chunk = audio.get_audio_chunk()
            if chunk:
                chunks_received += 1
            time.sleep(0.05)  # Small delay
        
        if chunks_received > 0:
            print(f"   ✓ Received {chunks_received} audio chunk(s)")
        else:
            print("   ⚠ No audio chunks received (might be normal depending on audio device)")
        
        # Stop stream
        print("6. Stopping audio capture stream...")
        if not audio.stop():
            print("   ✗ Failed to stop audio stream")
            return False
        print("   ✓ Audio stream stopped")
        
        print("\n✓ Audio Capture test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ Audio Capture test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_speech_engine():
    """Test SpeechEngine module."""
    print("\n" + "=" * 70)
    print("TEST 2: Speech Engine Module")
    print("=" * 70)
    
    try:
        # Create SpeechEngine instance
        print("1. Creating SpeechEngine instance...")
        engine = SpeechEngine()
        print("   ✓ SpeechEngine created successfully")
        
        # Find model path
        print("2. Looking for Vosk model...")
        project_root = Path(__file__).parent.parent
        model_path = project_root / "models" / "vosk-model-small-en-us"
        
        if not model_path.exists():
            print(f"   ✗ Model not found at {model_path}")
            print(f"\n   Please download the model using:")
            print(f"   python scripts/download_model.py")
            return False
        
        print(f"   ✓ Found model at {model_path}")
        
        # Load model
        print("3. Loading Vosk model...")
        if not engine.load_model(str(model_path)):
            print("   ✗ Failed to load model")
            return False
        print("   ✓ Model loaded successfully")
        
        # Test grammar setting
        print("4. Setting grammar (optional vocabulary)...")
        test_words = ["zero", "one", "two", "three", "bleeding", "next"]
        if engine.set_grammar(test_words):
            print(f"   ✓ Grammar set with {len(test_words)} words")
        else:
            print("   ⚠ Failed to set grammar (may not be critical)")
        
        # Test reset
        print("5. Testing engine reset...")
        engine.reset()
        print("   ✓ Engine reset successfully")
        
        # Test partial result
        print("6. Testing partial result...")
        partial = engine.get_partial()
        print(f"   ✓ Current partial result: '{partial}'")
        
        print("\n✓ Speech Engine test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ Speech Engine test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test AudioCapture and SpeechEngine working together."""
    print("\n" + "=" * 70)
    print("TEST 3: Integration - Audio → Speech")
    print("=" * 70)
    
    try:
        # Setup instances
        print("1. Setting up AudioCapture and SpeechEngine...")
        audio = AudioCapture(sample_rate=16000, chunk_size=4000, channels=1)
        engine = SpeechEngine()
        print("   ✓ Instances created")
        
        # Load model
        print("2. Loading Vosk model...")
        project_root = Path(__file__).parent.parent
        model_path = project_root / "models" / "vosk-model-small-en-us"
        
        if not model_path.exists():
            print(f"   ✗ Model not found - cannot complete integration test")
            return False
        
        if not engine.load_model(str(model_path)):
            print("   ✗ Failed to load model")
            return False
        print("   ✓ Model loaded")
        
        # Start audio capture
        print("3. Starting audio capture stream...")
        if not audio.start():
            print("   ✗ Failed to start audio stream")
            return False
        print("   ✓ Stream started")
        
        # Process audio through engine
        print("4. Processing audio through speech engine (3 seconds)...")
        print("   [Try saying something like 'hello' or 'one two three']")
        
        results = []
        start_time = time.time()
        
        while time.time() - start_time < 3:
            chunk = audio.get_audio_chunk()
            if chunk:
                result = engine.process_audio(chunk)
                partial = engine.get_partial()
                
                if partial and (not results or results[-1] != partial):
                    results.append(partial)
                    print(f"   Partial: {partial}")
            
            time.sleep(0.01)
        
        if results:
            print(f"   ✓ Heard: {results[-1]}")
        else:
            print("   ⚠ No speech recognized (try speaking more clearly or louder)")
        
        # Stop audio
        print("5. Stopping audio capture stream...")
        if not audio.stop():
            print("   ✗ Failed to stop audio stream")
            return False
        print("   ✓ Stream stopped")
        
        print("\n✓ Integration test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ Integration test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_config_manager():
    """Test ConfigManager integration."""
    print("\n" + "=" * 70)
    print("TEST 4: Configuration Manager")
    print("=" * 70)
    
    try:
        print("1. Creating ConfigManager instance...")
        config = ConfigManager()
        print("   ✓ ConfigManager created")
        
        # Test getting values
        print("2. Reading configuration values...")
        sample_rate = config.get("audio.sample_rate")
        print(f"   Sample rate: {sample_rate}")
        
        chunk_size = config.get("audio.chunk_size")
        print(f"   Chunk size: {chunk_size}")
        
        window_title = config.get("target.window_title")
        print(f"   Target window: {window_title}")
        print("   ✓ Configuration read successfully")
        
        # Test setting values
        print("3. Modifying configuration...")
        original_title = window_title
        config.set("target.window_title", "Test Window")
        
        new_title = config.get("target.window_title")
        if new_title == "Test Window":
            print(f"   ✓ Configuration updated: {new_title}")
            
            # Restore original
            config.set("target.window_title", original_title)
            print("   ✓ Configuration restored")
        else:
            print("   ✗ Configuration update failed")
            return False
        
        print("\n✓ ConfigManager test PASSED\n")
        return True
    
    except Exception as e:
        print(f"\n✗ ConfigManager test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "VoicePerio Phase 2 Integration Tests" + " " * 17 + "║")
    print("║" + " " * 18 + "Audio Capture & Speech Recognition" + " " * 16 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Setup logging
    logger = setup_test_logging()
    logger.info("Starting Phase 2 integration tests")
    
    # Run tests
    results = {}
    
    results['audio_capture'] = test_audio_capture()
    results['speech_engine'] = test_speech_engine()
    results['integration'] = test_integration()
    results['config'] = test_config_manager()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for p in results.values() if p)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n╔" + "=" * 68 + "╗")
        print("║" + " " * 20 + "✓ ALL TESTS PASSED!" + " " * 30 + "║")
        print("║" + " " * 16 + "Phase 2 implementation is working!" + " " * 18 + "║")
        print("╚" + "=" * 68 + "╝\n")
        return 0
    else:
        print("\n╔" + "=" * 68 + "╗")
        print("║" + " " * 18 + "✗ SOME TESTS FAILED" + " " * 30 + "║")
        print("║" + " " * 16 + "Please review the errors above" + " " * 22 + "║")
        print("╚" + "=" * 68 + "╝\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
