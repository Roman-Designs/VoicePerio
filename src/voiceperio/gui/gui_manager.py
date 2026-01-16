"""
GUI Manager - System tray and floating indicator management
"""

from PyQt6.QtWidgets import QWidget, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon


class GUIManager:
    """
    System tray and floating indicator management.
    
    Components:
    - System tray icon with menu
    - Floating indicator (shows: Listening/Paused/Last command)
    - Settings dialog
    
    Methods:
    - show_indicator()
    - hide_indicator()
    - update_status(text: str, color: str)
    - show_command_feedback(command: str)
    """
    
    def __init__(self):
        self.tray_icon = None
        self.indicator_widget = None
        
    def show_indicator(self):
        """Show the floating indicator window"""
        pass
    
    def hide_indicator(self):
        """Hide the floating indicator window"""
        pass
    
    def update_status(self, text: str, color: str):
        """Update the status text and color"""
        pass
    
    def show_command_feedback(self, command: str):
        """Display feedback for recognized command"""
        pass
