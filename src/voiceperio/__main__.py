"""
Entry point for VoicePerio application.
Allows running the application with: python -m voiceperio
Properly handles console window for both development and production builds.
"""

import sys
import os

from voiceperio.main import main

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        # If running as GUI app without console, try to show error in system tray
        try:
            import logging
            logger = logging.getLogger("voiceperio")
            logger.error(f"Fatal error: {e}", exc_info=True)
        except:
            pass
        
        # Exit with error code
        sys.exit(1)
