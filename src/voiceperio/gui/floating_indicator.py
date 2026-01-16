"""
Floating Indicator - Small floating window showing listening status
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class FloatingIndicator(QWidget):
    """
    Floating indicator window showing listening status and last command.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        pass
    
    def set_listening(self):
        """Show listening status"""
        pass
    
    def set_paused(self):
        """Show paused status"""
        pass
    
    def update_command(self, command: str):
        """Update displayed command"""
        pass
