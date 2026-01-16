"""Minimal test - shows a message box"""
import sys

print("Test program starting...")
sys.stdout.flush()

try:
    # Try importing just the basic modules
    print("Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication, QMessageBox
    print("PyQt6 imported successfully!")
    
    # Create application
    print("Creating QApplication...")
    app = QApplication([])
    print("QApplication created!")
    
    # Show a message
    print("Showing message box...")
    QMessageBox.information(None, "Test", "VoicePerio test successful!")
    print("Message box shown!")
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
