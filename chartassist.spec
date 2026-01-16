# -*- mode: python ; coding: utf-8 -*-
"""
ChartAssist PyInstaller Specification File

This spec file configures PyInstaller to build a standalone Windows executable.
The resulting .exe will include all dependencies and can run without Python installed.

Build command:
    pyinstaller installer/chartassist.spec

Output:
    dist/ChartAssist/ChartAssist.exe
"""

import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(SPECPATH).parent
SRC_PATH = PROJECT_ROOT / 'src'
RESOURCES_PATH = SRC_PATH / 'chartassist' / 'gui' / 'resources'
COMMANDS_PATH = SRC_PATH / 'chartassist' / 'commands'
MODELS_PATH = PROJECT_ROOT / 'models'

block_cipher = None

# Data files to include
datas = [
    # Command definitions
    (str(COMMANDS_PATH / 'default_commands.json'), 'chartassist/commands'),
    (str(COMMANDS_PATH / 'dental_vocabulary.txt'), 'chartassist/commands'),
    
    # GUI resources (icons, styles)
    (str(RESOURCES_PATH), 'chartassist/gui/resources'),
    
    # Vosk model (if bundling - makes exe large ~50MB+)
    # Uncomment to bundle model, or distribute separately
    # (str(MODELS_PATH / 'vosk-model-small-en-us'), 'models/vosk-model-small-en-us'),
]

# Filter out non-existent paths
datas = [(src, dst) for src, dst in datas if Path(src).exists()]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'vosk',
    'sounddevice',
    'pyautogui',
    'pynput',
    'pynput.keyboard',
    'pynput.keyboard._win32',
    'pynput.mouse',
    'pynput.mouse._win32',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'numpy',
    'json',
    'logging',
    'threading',
    'queue',
    'ctypes',
    'win32api',
    'win32con',
    'win32gui',
    'win32process',
    'keyboard',
    'rapidfuzz',
    'rapidfuzz.fuzz',
    'rapidfuzz.process',
]

# Analysis - collect all Python files and dependencies
a = Analysis(
    [str(SRC_PATH / 'chartassist' / '__main__.py')],
    pathex=[str(SRC_PATH)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'PIL',
        'tkinter',
        '_tkinter',
        'test',
        'tests',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary files to reduce size
a.binaries = [b for b in a.binaries if not any(
    x in b[0].lower() for x in ['qt6webengine', 'qt6designer', 'qt6qml']
)]

# Create the PYZ archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChartAssist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX if available
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(RESOURCES_PATH / 'icon.ico') if (RESOURCES_PATH / 'icon.ico').exists() else None,
    version='version_info.txt',  # Version info for Windows
)

# Collect all files into a directory
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChartAssist',
)
