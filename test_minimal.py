"""Minimal test to verify PyInstaller build works"""
import sys
import os

# Add _internal to path
if getattr(sys, 'frozen', False):
    os.environ['PYTHONPATH'] = sys._MEIPASS

print("=" * 50)
print("VoicePerio Minimal Test")
print("=" * 50)
print(f"Frozen: {getattr(sys, 'frozen', False)}")
print(f"MEIPASS: {getattr(sys, 'MEIPASS', 'N/A')}")
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print("=" * 50)

# Try importing the main module
try:
    print("Importing voiceperio.main...")
    from voiceperio import main
    print("SUCCESS: voiceperio.main imported!")
    
    print("\nStarting application...")
    result = main()
    print(f"Application exited with code: {result}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
