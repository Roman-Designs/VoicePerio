"""
Floating Indicator - Small floating window showing listening status

Provides a draggable floating window that displays the current listening status
and the last recognized command. Updates in real-time as status changes.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FloatingIndicator(QWidget):
    """
    Small floating window showing listening status and last command.
    
    Features:
    - Draggable window that stays on top
    - Shows current status (Listening/Paused/Sleeping)
    - Displays last recognized command
    - Real-time status updates
    - Opacity/transparency control
    - Close/minimize button
    - Default position in bottom-right corner
    
    Example:
        >>> indicator = FloatingIndicator()
        >>> indicator.show()
        >>> indicator.set_listening()
        >>> indicator.update_command("three two three")
    """
    
    close_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize floating indicator.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.drag_position = QPoint()
        self.status_text = "Ready"
        self.last_command = ""
        self.is_listening = False
        
        # Setup UI
        self.init_ui()
        
        # Set window properties
        self.setWindowTitle("VoicePerio Status")
        # WA_StaysOnTop doesn't exist in PyQt6 - use WindowStaysOnTopHint flag instead
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Default position (bottom-right)
        self._set_default_position()
        
        # Auto-hide timer for command feedback
        self.feedback_timer = QTimer()
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.timeout.connect(self._clear_command_feedback)
        
        logger.debug("FloatingIndicator initialized")
    
    def init_ui(self) -> None:
        """
        Initialize the UI components.
        
        Layout:
        - Status label (top)
        - Command label (middle)
        - Close button (bottom)
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Status label
        self.status_label = QLabel("Ready")
        status_font = QFont()
        status_font.setPointSize(10)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Command label
        self.command_label = QLabel("")
        command_font = QFont()
        command_font.setPointSize(8)
        self.command_label.setFont(command_font)
        self.command_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.command_label.setMaximumWidth(200)
        self.command_label.setWordWrap(True)
        layout.addWidget(self.command_label)
        
        # Close button
        self.close_button = QPushButton("✕")
        self.close_button.setMaximumWidth(30)
        self.close_button.setMaximumHeight(25)
        self.close_button.clicked.connect(self._on_close)
        layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        
        # Set window size
        self.setMinimumWidth(250)
        self.setMinimumHeight(100)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        logger.debug("FloatingIndicator UI initialized")
    
    def _apply_stylesheet(self) -> None:
        """Apply stylesheet for professional appearance"""
        style = """
            QWidget {
                background-color: #1e1e1e;
                border: 2px solid #2196F3;
                border-radius: 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
        self.setStyleSheet(style)
    
    def set_listening(self) -> None:
        """
        Update to show listening status.
        
        Example:
            >>> indicator.set_listening()
        """
        self.status_text = "Listening"
        self.is_listening = True
        self._update_status_display()
        logger.debug("FloatingIndicator: Listening")
    
    def set_paused(self) -> None:
        """
        Update to show paused status.
        
        Example:
            >>> indicator.set_paused()
        """
        self.status_text = "Paused"
        self.is_listening = False
        self._update_status_display()
        logger.debug("FloatingIndicator: Paused")
    
    def set_sleeping(self) -> None:
        """
        Update to show sleeping status.
        
        Example:
            >>> indicator.set_sleeping()
        """
        self.status_text = "Sleeping"
        self.is_listening = False
        self._update_status_display()
        logger.debug("FloatingIndicator: Sleeping")
    
    def set_ready(self) -> None:
        """
        Update to show ready status.
        
        Example:
            >>> indicator.set_ready()
        """
        self.status_text = "Ready"
        self.is_listening = False
        self._update_status_display()
        logger.debug("FloatingIndicator: Ready")
    
    def _update_status_display(self) -> None:
        """Update status label with current status"""
        self.status_label.setText(f"🎤 {self.status_text}" if self.is_listening else self.status_text)
        
        # Update color based on status
        if self.status_text == "Listening":
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif self.status_text == "Paused":
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        elif self.status_text == "Sleeping":
            self.status_label.setStyleSheet("color: #9E9E9E; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #ffffff; font-weight: bold;")
    
    def update_command(self, command: str) -> None:
        """
        Update displayed command text.
        
        Args:
            command: Command text to display
            
        Example:
            >>> indicator.update_command("three two three")
        """
        self.last_command = command
        self.command_label.setText(f"Command: {command}")
        self.command_label.setStyleSheet("color: #4CAF50;")
        
        # Auto-clear after 3 seconds
        self.feedback_timer.stop()
        self.feedback_timer.start(3000)
        
        logger.debug(f"Command displayed: {command}")
    
    def _clear_command_feedback(self) -> None:
        """Clear command feedback after timeout"""
        self.command_label.setText("")
        logger.debug("Command feedback cleared")
    
    def set_opacity(self, opacity: float) -> None:
        """
        Set window opacity (0.0 to 1.0).
        
        Args:
            opacity: Opacity value (0=transparent, 1=opaque)
            
        Example:
            >>> indicator.set_opacity(0.8)
        """
        opacity = max(0.0, min(1.0, opacity))  # Clamp between 0 and 1
        self.setWindowOpacity(opacity)
        logger.debug(f"FloatingIndicator opacity: {opacity}")
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def _set_default_position(self) -> None:
        """Set default position to bottom-right corner"""
        screen = self.screen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.right() - self.width() - 20
            y = geometry.bottom() - self.height() - 20
            self.move(int(x), int(y))
            logger.debug(f"FloatingIndicator positioned at ({x}, {y})")
    
    def _on_close(self) -> None:
        """Handle close button click"""
        self.close_requested.emit()
        self.hide()
        logger.debug("FloatingIndicator close requested")
    
    def get_position(self) -> tuple:
        """
        Get current window position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        pos = self.pos()
        return (pos.x(), pos.y())
    
    def set_position(self, x: int, y: int) -> None:
        """
        Set window position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.move(x, y)
        logger.debug(f"FloatingIndicator moved to ({x}, {y})")
    
    def toggle_visibility(self) -> None:
        """
        Toggle window visibility.
        
        Example:
            >>> indicator.toggle_visibility()
        """
        if self.isVisible():
            self.hide()
            logger.debug("FloatingIndicator hidden")
        else:
            self.show()
            logger.debug("FloatingIndicator shown")
    
    def show_info(self, title: str, message: str) -> None:
        """
        Display info message temporarily.
        
        Args:
            title: Info title
            message: Info message
        """
        full_text = f"{title}\n{message}"
        self.update_command(full_text)
        logger.debug(f"Info displayed: {title} - {message}")
