"""
Entry point for VoicePerio application.
Allows running the application with: python -m voiceperio
"""

import sys

# Use absolute import for PyInstaller compatibility
try:
    from voiceperio.main import main
except ImportError:
    from .main import main

if __name__ == "__main__":
    sys.exit(main())
