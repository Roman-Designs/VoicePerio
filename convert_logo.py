"""Convert PNG to ICO for PyInstaller"""
from PIL import Image
import os

# Paths
png_path = "src/voiceperio/gui/resources/voiceperio.png"
ico_path = "src/voiceperio/gui/resources/icon.ico"

print("Converting PNG to ICO...")

try:
    # Open and convert image
    img = Image.open(png_path)
    
    # Create ICO with multiple sizes
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ico_path, format='ICO', sizes=sizes)
    
    print(f"[OK] Created icon at: {ico_path}")
    print(f"     File size: {os.path.getsize(ico_path)} bytes")
    
except Exception as e:
    print(f"[ERROR] {e}")
