# -*- mode: python ; coding: utf-8 -*-
"""
VoicePerio PyInstaller Specification File

This spec file configures PyInstaller to build a standalone Windows executable.
The resulting .exe will include all dependencies and can run without Python installed.

Build command:
    pyinstaller installer/voiceperio.spec

Output:
    dist/VoicePerio/VoicePerio.exe

Requirements:
    - Python 3.10+
    - PyInstaller 5.13+
    - All dependencies installed in the build environment
"""

import sys
import os
from pathlib import Path

# =============================================================================
# PROJECT PATH CONFIGURATION
# =============================================================================

# Get project root directory (parent of installer directory)
PROJECT_ROOT = Path(SPECPATH).parent
SRC_PATH = PROJECT_ROOT / 'src'
RESOURCES_PATH = SRC_PATH / 'voiceperio' / 'gui' / 'resources'
COMMANDS_PATH = SRC_PATH / 'voiceperio' / 'commands'
MODELS_PATH = PROJECT_ROOT / 'models'
INSTALLER_PATH = PROJECT_ROOT / 'installer'

# Encryption key for bytecode (None for no encryption)
block_cipher = None

# =============================================================================
# DATA FILES TO INCLUDE
# =============================================================================

datas = [
    # Command definitions - JSON configuration files
    (str(COMMANDS_PATH / 'default_commands.json'), 'voiceperio/commands'),
    
    # GUI resources - icons and images
    (str(RESOURCES_PATH / 'voiceperio.png'), 'voiceperio/gui/resources'),
    (str(RESOURCES_PATH / 'icon.ico'), 'voiceperio/gui/resources'),
    
    # Version information file
    (str(INSTALLER_PATH / 'version_info.txt'), '.'),
]

# Filter out non-existent paths to avoid build errors
datas = [(src, dst) for src, dst in datas if Path(src).exists()]

# =============================================================================
# BINARY FILES TO INCLUDE
# =============================================================================

binaries = []

# Add vosk DLLs - these are required for speech recognition
import vosk
vosk_path = Path(vosk.__file__).parent
for dll in vosk_path.glob('*.dll'):
    binaries.append((str(dll), 'vosk'))

# =============================================================================
# HIDDEN IMPORTS
# =============================================================================

hiddenimports = [
    # Core application modules
    'voiceperio',
    'voiceperio.__main__',
    'voiceperio.main',
    'voiceperio.config_manager',
    'voiceperio.audio_capture',
    'voiceperio.speech_engine',
    'voiceperio.command_parser',
    'voiceperio.number_sequencer',
    'voiceperio.action_executor',
    
    # GUI modules
    'voiceperio.gui',
    'voiceperio.gui.gui_manager',
    'voiceperio.gui.system_tray',
    'voiceperio.gui.floating_indicator',
    'voiceperio.gui.settings_dialog',
    
    # Utility modules
    'voiceperio.utils',
    'voiceperio.utils.logger',
    'voiceperio.utils.window_utils',
    
    # Speech recognition - Vosk
    'vosk',
    'vosk.__init__',
    'vosk.batch',
    'vosk.beam',
    'vosk.convert',
    'vosk.decoding',
    'vosk.graph',
    'vosk.loader',
    'vosk.model',
    'vosk.reconstruct',
    'vosk.set_log_level',
    
    # Audio capture - sounddevice
    'sounddevice',
    'sounddevice',
    '_sounddevice_python',
    
    # Keystroke injection - pyautogui
    'pyautogui',
    'pyautogui._pyautogui_win',
    'pyautogui._pyautogui_x11',
    
    # Global hotkeys - keyboard
    'keyboard',
    'keyboard._keyboard',
    
    # Window management - pywin32
    'win32api',
    'win32con',
    'win32gui',
    'win32process',
    'win32service',
    'win32ts',
    'pythoncom',
    'pywintypes',
    
    # Input monitoring - pynput
    'pynput',
    'pynput.keyboard',
    'pynput.keyboard._win32',
    'pynput.mouse',
    'pynput.mouse._win32',
    
    # GUI framework - PyQt6
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    
    # Numerical processing - numpy
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib',
    'numpy.lib.format',
    
    # JSON handling
    'json',
    'json.decoder',
    'json.encoder',
    
    # Logging
    'logging',
    'logging.handlers',
    
    # Threading
    'threading',
    
    # Queue for thread-safe communication
    'queue',
    
    # Windows API
    'ctypes',
    'ctypes.wintypes',
    
    # String matching - rapidfuzz
    'rapidfuzz',
    'rapidfuzz.fuzz',
    'rapidfuzz.process',
    'rapidfuzz.string_metric',
    
    # Configuration - jsonschema
    'jsonschema',
    'jsonschema._types',
    'jsonschema._typing',
    'jsonschema._utils',
    'jsonschema.validators',
    
    # Color logging - colorlog
    'colorlog',
    'colorlog.escape_codes',
]

# =============================================================================
# EXCLUDED MODULES
# =============================================================================

excludes = [
    # Scientific computing (not needed)
    'matplotlib',
    'scipy',
    'pandas',
    'sklearn',
    'sympy',
    
    # Image processing (not needed, PyQt6 handles icons)
    'PIL',
    'Pillow',
    
    # Tkinter (not used)
    'tkinter',
    '_tkinter',
    
    # Test modules
    'test',
    'tests',
    'unittest',
    'doctest',
    
    # Development tools
    'pytest',
    'pytest-cov',
    'black',
    'flake8',
    'mypy',
    'ipython',
    
    # Documentation
    'sphinx',
    'mkdocs',
    
    # Web frameworks (not needed)
    'flask',
    'django',
    'bottle',
    
    # Database (not needed)
    'sqlite3',
    'sqlalchemy',
    
    # Audio editing (not needed)
    'pydub',
    
    # Unused Qt components (reduces size)
    'Qt6WebEngine',
    'Qt6WebEngineCore',
    'Qt6WebEngineWidgets',
    'Qt6Designer',
    'Qt6Qml',
    'Qt6Quick',
    'Qt6Svg',
]

# =============================================================================
# ANALYSIS PHASE
# =============================================================================

a = Analysis(
    # Entry point script
    [str(SRC_PATH / 'voiceperio' / '__main__.py')],
    
    # Search paths for imports
    pathex=[
        str(SRC_PATH),
        str(PROJECT_ROOT),
    ],
    
    # Binary dependencies
    binaries=binaries,
    
    # Data files to include
    datas=datas,
    
    # Hidden imports
    hiddenimports=hiddenimports,
    
    # Hook search paths
    hookspath=[],
    
    # Hook configuration
    hooksconfig={},
    
    # Runtime hooks
    runtime_hooks=[],
    
    # Excluded modules
    excludes=excludes,
    
    # Windows-specific options
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    
    # Encryption
    cipher=block_cipher,
    noarchive=False,
)

# =============================================================================
# OPTIMIZE AND CLEANUP
# =============================================================================

# Remove unnecessary Qt components to reduce executable size
# These components are heavy and not used by VoicePerio
if a.binaries:
    a.binaries = [b for b in a.binaries if not any(
        x in b[0].lower() 
        for x in [
            'qt6webengine', 
            'qt6webengine', 
            'qt6designer', 
            'qt6qml', 
            'qt6quick', 
            'qt6svg',
            'opengl32sw.dll',  # Software OpenGL (not needed)
        ]
    )]

# =============================================================================
# CREATE PYZ ARCHIVE
# =============================================================================

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# =============================================================================
# CREATE EXECUTABLE
# =============================================================================

exe_options = {
    # Executable name
    'name': 'VoicePerio',
    
    # Debug mode (set to True for troubleshooting build issues)
    'debug': False,
    
    # Don't ignore signals in bootloader
    'bootloader_ignore_signals': False,
    
    # Don't strip debug symbols (keep for better crash reports)
    'strip': False,
    
    # Use UPX compression if available
    'upx': True,
    
    # Windowed mode (no console) - GUI application
    # Temporarily set to True for debugging startup issues
    'console': True,
    
    # Show crash dialog even in windowed mode
    'disable_windowed_traceback': False,
    
    # argv emulation (not needed)
    'argv_emulation': False,
    
    # Target architecture (None = auto-detect)
    'target_arch': None,
    
    # Code signing identity
    'codesign_identity': None,
    
    # Entitlements file
    'entitlements_file': None,
    
    # Version information file
    'version': str(INSTALLER_PATH / 'version_info.txt'),
}

# Icon configuration
icon_path = RESOURCES_PATH / 'icon.ico'
if icon_path.exists():
    exe_options['icon'] = str(icon_path)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    **exe_options,
)

# =============================================================================
# COLLECT ALL FILES INTO DIRECTORY BUILD
# =============================================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[
        # Keep these files uncompressed (they're already compressed)
        '*.dll',
        '*.pyd',
    ],
    name='VoicePerio',
)

# =============================================================================
# SINGLE-FILE BUILD (OPTIONAL)
# =============================================================================

# Uncomment the following section to create a single-file executable instead
# of a directory build. Note: Single-file builds have longer startup times
# and may trigger false positives in antivirus software.

# splash_options = {
#     'image': str(RESOURCES_PATH / 'voiceperio.png'),
#     'banner_textoffset': 10,
#     'bannertextcolor': 'white',
#     'backcolor': '#0078d7',
#     'name': 'VoicePerio',
# }
# 
# splash = SPLASH(
#     str(RESOURCES_PATH / 'voiceperio.png'),
#     splash_options,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     name='VoicePerio',
# )
# 
# exe = EXE(
#     pyz,
#     a.scripts,
#     splash,
#     exclude_binaries=True,
#     **exe_options,
# )
