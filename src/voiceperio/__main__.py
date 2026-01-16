"""
Entry point for VoicePerio application.
Allows running the application with: python -m voiceperio
"""

import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
