"""Simple microphone test"""
import sys
import numpy as np

print("="*50)
print("Microphone Test")
print("="*50)

try:
    import sounddevice as sd
    print("\n[OK] sounddevice imported")
    
    # Get default input device
    device_info = sd.query_devices(kind='input')
    print("\nDefault input device:")
    print("  Name:", device_info['name'])
    print("  Channels:", device_info['max_input_channels'])
    
    print("\n" + "="*50)
    print("Testing audio capture for 3 seconds...")
    print("="*50)
    print("Speak into your microphone now!")
    
    # Record audio
    audio_data = sd.rec(
        frames=16000 * 3,  # 3 seconds at 16kHz
        samplerate=16000,
        channels=1,
        dtype='float32'
    )
    
    # Wait for recording to complete
    sd.wait()
    
    print("\n[OK] Recorded", len(audio_data), "samples")
    max_amp = float(np.max(np.abs(audio_data)))
    print("Max amplitude:", max_amp)
    
    if max_amp > 0.001:
        print("\n[SUCCESS] Audio detected! Microphone is working.")
        print("\nThis means:")
        print("  1. Microphone IS capturing audio")
        print("  2. sounddevice IS working")
        print("  3. The issue is in VoicePerio's audio processing")
        print("\nCheck VoicePerio console for:")
        print("  - 'Partial result:' messages when you speak")
        print("  - 'Final result:' messages")
        print("  - Any audio-related errors")
    else:
        print("\n[ERROR] No audio detected. Check microphone levels.")
        
except Exception as e:
    print("\n[ERROR]", e)
    import traceback
    traceback.print_exc()
