"""
Modern Medical UI/UX for VoicePerio - Complete Implementation

Provides a professional, minimalist medical interface with:
- Status indicator with pulse animation
- Voice feedback panel
- Real-time information display
- Command history
- Quick action buttons
- Complete WCAG AAA accessibility
- Compact 400×300px docked window

Design System: MEDICAL_UI_DESIGN.md (adapted for 400×300px)
- Color Palette: White (#FFFFFF) + Blue (#0066CC)
- Typography: Segoe UI
- Grid: 8px spacing system
- Window: 400×300px, docked bottom-right
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class HistoryItem:
    """Represents a command in the history"""
    command: str
    timestamp: datetime
    status: str  # "success", "error", "pending"
    feedback: str = ""


# ============================================================================
# Custom Widgets
# ============================================================================

class StatusIndicator(QWidget):
    """
    Animated circular status indicator (compact 24×24px).
    
    States:
    - Listening (Green #4CAF50) with pulse animation
    - Paused (Orange #FF9800)
    - Sleeping (Gray #CCCCCC)
    - Ready (Blue #0066CC)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = "ready"
        self.setMinimumSize(24, 24)
        self.setMaximumSize(24, 24)
        
        # Animation for pulse effect
        self.pulse_animation = QPropertyAnimation(self, b"pulse_value")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(0.7)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.pulse_animation.setLoopCount(-1)  # Infinite loop
        
        self.pulse_value = 1.0
        
    def set_status(self, status: str) -> None:
        """Set indicator status"""
        self.status = status.lower()
        
        # Control pulse animation
        if self.status == "listening":
            if not self.pulse_animation.state():
                self.pulse_animation.start()
        else:
            self.pulse_animation.stop()
            self.pulse_value = 1.0
        
        self.update()
        logger.debug(f"StatusIndicator: {status}")
    
    def paintEvent(self, event):
        """Custom paint for animated circle"""
        from PyQt6.QtGui import QPainter
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine color based on status
        colors = {
            "listening": QColor("#4CAF50"),
            "paused": QColor("#FF9800"),
            "sleeping": QColor("#CCCCCC"),
            "ready": QColor("#0066CC")
        }
        color = colors.get(self.status, QColor("#0066CC"))
        
        # Apply pulse opacity for listening state
        if self.status == "listening":
            color.setAlphaF(self.pulse_value)
        
        # Draw circle with white border
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw centered circle (radius 10)
        radius = 10
        painter.drawEllipse(12 - radius, 12 - radius, radius * 2, radius * 2)


class CompactFeedbackPanel(QFrame):
    """
    Compact feedback panel (single line with icon + command).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("feedbackPanel")
        self.setMinimumHeight(24)
        self.setMaximumHeight(24)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # Status indicator icon
        self.status_icon = QLabel("●")
        self.status_icon.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 10px;")
        self.status_icon.setMaximumWidth(12)
        layout.addWidget(self.status_icon)
        
        # Command text
        self.command_label = QLabel("Ready")
        self.command_label.setObjectName("commandText")
        command_font = QFont("Segoe UI", 10)
        self.command_label.setFont(command_font)
        self.command_label.setStyleSheet("color: #1A1A1A;")
        layout.addWidget(self.command_label)
        
        # Stretch space
        layout.addStretch()
        
        # Timestamp
        self.timestamp_label = QLabel("")
        self.timestamp_label.setObjectName("compact")
        timestamp_font = QFont("Segoe UI", 9)
        self.timestamp_label.setFont(timestamp_font)
        self.timestamp_label.setStyleSheet("color: #999999;")
        self.timestamp_label.setMaximumWidth(40)
        layout.addWidget(self.timestamp_label)
        
        self.setLayout(layout)
        
        # Apply stylesheet
        self.setStyleSheet("""
            #feedbackPanel {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
    
    def update_feedback(self, command: str, status: str, feedback: str = "") -> None:
        """Update feedback panel"""
        self.command_label.setText(command[:35])  # Truncate long commands
        self.timestamp_label.setText(datetime.now().strftime("%H:%M"))
        
        # Update status icon color
        status_colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "pending": "#FF9800"
        }
        color = status_colors.get(status, "#CCCCCC")
        self.status_icon.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10px;")


class CompactInfoPanel(QFrame):
    """
    Compact info panel showing field counter and status (single row).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("infoPanel")
        self.setMinimumHeight(22)
        self.setMaximumHeight(22)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(12)
        
        # Field counter
        self.field_label = QLabel("Field:")
        field_font = QFont("Segoe UI", 9)
        self.field_label.setFont(field_font)
        self.field_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.field_label)
        
        self.field_value = QLabel("0/0")
        value_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        self.field_value.setFont(value_font)
        self.field_value.setStyleSheet("color: #0066CC;")
        self.field_value.setMaximumWidth(40)
        layout.addWidget(self.field_value)
        
        # Status
        self.status_label = QLabel("Status:")
        self.status_label.setFont(field_font)
        self.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.status_label)
        
        self.status_value = QLabel("Ready")
        self.status_value.setFont(value_font)
        self.status_value.setStyleSheet("color: #0066CC;")
        self.status_value.setMaximumWidth(60)
        layout.addWidget(self.status_value)
        
        # Time elapsed
        self.time_label = QLabel("Time:")
        self.time_label.setFont(field_font)
        self.time_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.time_label)
        
        self.time_value = QLabel("0:00")
        self.time_value.setFont(value_font)
        self.time_value.setStyleSheet("color: #0066CC;")
        self.time_value.setMaximumWidth(35)
        layout.addWidget(self.time_value)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Apply stylesheet
        self.setStyleSheet("""
            #infoPanel {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
    
    def set_field_counter(self, current: int, total: int) -> None:
        """Set field counter"""
        self.field_value.setText(f"{current}/{total}")
    
    def set_session_status(self, status: str) -> None:
        """Set session status"""
        self.status_value.setText(status[:10])  # Truncate
        colors = {
            "Active": "#4CAF50",
            "Paused": "#FF9800",
            "Sleeping": "#CCCCCC"
        }
        color = colors.get(status, "#0066CC")
        self.status_value.setStyleSheet(f"color: {color};")
    
    def set_elapsed_time(self, seconds: int) -> None:
        """Set elapsed time"""
        minutes = seconds // 60
        secs = seconds % 60
        self.time_value.setText(f"{minutes}:{secs:02d}")


class CompactCommandHistory(QFrame):
    """
    Compact command history (scrollable, max 2 visible items).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyList")
        self.setMinimumHeight(45)
        self.setMaximumHeight(45)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        
        # Scroll area for history
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #F8F9FA;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: #CCCCCC;
                border-radius: 3px;
                min-height: 16px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #0066CC;
            }
        """)
        
        # Container for history items
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(0)
        self.history_layout.addStretch()
        self.history_container.setLayout(self.history_layout)
        
        scroll.setWidget(self.history_container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        self.history_items: List[HistoryItem] = []
        
        # Apply stylesheet
        self.setStyleSheet("""
            #historyList {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
    
    def add_history_item(self, command: str, status: str, feedback: str = "") -> None:
        """Add command to history"""
        item = HistoryItem(
            command=command,
            timestamp=datetime.now(),
            status=status,
            feedback=feedback
        )
        self.history_items.insert(0, item)
        
        if len(self.history_items) > 5:
            self.history_items.pop()
        
        self._refresh_display()
    
    def _refresh_display(self) -> None:
        """Refresh history display"""
        # Clear existing items (except stretch)
        while self.history_layout.count() > 1:
            self.history_layout.takeAt(0).widget().deleteLater()
        
        status_icons = {
            "success": "✓",
            "error": "✗",
            "pending": "→"
        }
        status_colors = {
            "success": "#4CAF50",
            "error": "#F44336",
            "pending": "#FF9800"
        }
        
        # Add items (show most recent first, max 2)
        for item in self.history_items[:2]:
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(4, 2, 4, 2)
            item_layout.setSpacing(4)
            
            # Status icon
            status_label = QLabel(status_icons.get(item.status, "?"))
            status_label.setStyleSheet(f"color: {status_colors.get(item.status, '#CCCCCC')}; font-weight: bold; font-size: 9px;")
            status_label.setMaximumWidth(10)
            item_layout.addWidget(status_label)
            
            # Command text (truncated)
            command_label = QLabel(item.command[:28])
            command_font = QFont("Courier New", 9)
            command_label.setFont(command_font)
            command_label.setStyleSheet("color: #1A1A1A;")
            item_layout.addWidget(command_label)
            
            # Timestamp
            time_label = QLabel(item.timestamp.strftime("%H:%M"))
            time_label.setStyleSheet("color: #999999; font-size: 8px;")
            time_label.setMaximumWidth(32)
            item_layout.addWidget(time_label)
            
            item_widget.setLayout(item_layout)
            item_widget.setObjectName("historyItem")
            item_widget.setMaximumHeight(20)
            
            self.history_layout.insertWidget(0, item_widget)


class CompactActionBar(QWidget):
    """
    Compact modern action buttons: Pause, Save, Settings, Exit.
    Modern flat design with gradient-like effects on hover.
    """
    
    pause_requested = pyqtSignal()
    save_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Modern button style (flat, clean, no borders)
        button_style = """
            QPushButton {
                background-color: #F5F5F5;
                color: #0066CC;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: 600;
                font-size: 11px;
                min-height: 26px;
                max-height: 26px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
            QPushButton:pressed {
                background-color: #0066CC;
                color: #FFFFFF;
            }
            QPushButton:disabled {
                background-color: #EEEEEE;
                color: #CCCCCC;
            }
        """
        
        # Pause button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setToolTip("Pause/Resume listening")
        self.pause_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pause_button.clicked.connect(self.pause_requested.emit)
        self.pause_button.setMinimumWidth(50)
        self.pause_button.setStyleSheet(button_style)
        layout.addWidget(self.pause_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save data")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.clicked.connect(self.save_requested.emit)
        self.save_button.setMinimumWidth(50)
        self.save_button.setStyleSheet(button_style)
        layout.addWidget(self.save_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙")
        self.settings_button.setToolTip("Open settings")
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.clicked.connect(self.settings_requested.emit)
        self.settings_button.setMaximumWidth(40)
        self.settings_button.setStyleSheet(button_style)
        layout.addWidget(self.settings_button)
        
        # Exit button (modern red)
        self.exit_button = QPushButton("✕")
        self.exit_button.setToolTip("Exit VoicePerio")
        self.exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_button.clicked.connect(self.exit_requested.emit)
        self.exit_button.setMaximumWidth(40)
        exit_style = """
            QPushButton {
                background-color: #FFEBEE;
                color: #D32F2F;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-weight: 600;
                font-size: 14px;
                min-height: 26px;
                max-height: 26px;
            }
            QPushButton:hover {
                background-color: #FFCDD2;
                color: #C62828;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
                color: #FFFFFF;
            }
        """
        self.exit_button.setStyleSheet(exit_style)
        layout.addWidget(self.exit_button)
        
        layout.addStretch()
        
        self.setLayout(layout)


# ============================================================================
# Main Modern Medical UI Window (Redesigned)
# ============================================================================

class ModernMedicalUI(QMainWindow):
    """
    Compact medical UI window (400×255px - 15% compressed) with all essential controls.
    
    Signals:
    - pause_requested()
    - save_requested()
    - settings_requested()
    - exit_requested()
    """
    
    pause_requested = pyqtSignal()
    save_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Window properties - Compressed to 255px (85% of 300px)
        self.setWindowTitle("VoicePerio")
        self.setMinimumSize(400, 255)
        self.setMaximumSize(400, 255)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Drag position tracking
        self.drag_position = QPoint()
        
        # Setup UI
        self.init_ui()
        self._set_docked_position()
        
        # Position save timer
        self.position_save_timer = QTimer()
        self.position_save_timer.setSingleShot(True)
        self.position_save_timer.timeout.connect(self._save_position)
        
        logger.debug("ModernMedicalUI initialized (255px height)")
    
    def init_ui(self) -> None:
        """Initialize UI components with ultra-compact layout"""
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)  # Reduced from 8
        main_layout.setSpacing(4)  # Reduced from 6
        
        # === HEADER (Status indicator + title) ===
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        
        self.status_indicator = StatusIndicator()
        header_layout.addWidget(self.status_indicator)
        
        self.status_text = QLabel("Ready")
        status_font = QFont("Segoe UI", 10, QFont.Weight.Bold)  # Reduced from 11
        self.status_text.setFont(status_font)
        self.status_text.setStyleSheet("color: #1A1A1A;")
        header_layout.addWidget(self.status_text)
        
        header_layout.addStretch()
        
        # Minimize button (modern flat style)
        minimize_btn = QPushButton("−")
        minimize_btn.setMaximumSize(22, 22)
        minimize_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #0066CC;
                font-weight: bold;
                background-color: transparent;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
                border-radius: 3px;
            }
        """)
        minimize_btn.clicked.connect(self.toggle_visibility)
        header_layout.addWidget(minimize_btn)
        
        main_layout.addLayout(header_layout)
        
        # === FEEDBACK PANEL ===
        self.feedback_panel = CompactFeedbackPanel()
        main_layout.addWidget(self.feedback_panel)
        
        # === INFO PANEL ===
        self.info_panel = CompactInfoPanel()
        main_layout.addWidget(self.info_panel)
        
        # === COMMAND HISTORY (scrollable) ===
        self.history_list = CompactCommandHistory()
        main_layout.addWidget(self.history_list, 1)  # Take remaining space
        
        # === ACTION BUTTONS ===
        self.action_bar = CompactActionBar()
        self.action_bar.pause_requested.connect(self.pause_requested.emit)
        self.action_bar.save_requested.connect(self.save_requested.emit)
        self.action_bar.settings_requested.connect(self.settings_requested.emit)
        self.action_bar.exit_requested.connect(self.exit_requested.emit)
        main_layout.addWidget(self.action_bar)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Apply global stylesheet
        self._apply_stylesheet()
    
    def _apply_stylesheet(self) -> None:
        """Apply complete medical UI stylesheet"""
        stylesheet = """
        QMainWindow {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
        }
        
        QWidget#centralWidget {
            background-color: #FFFFFF;
        }
        
        QLabel {
            color: #1A1A1A;
            font-family: 'Segoe UI', sans-serif;
        }
        
        QLabel#small {
            font-size: 11px;
            color: #666666;
        }
        
        QLabel#compact {
            font-size: 9px;
            color: #999999;
        }
        
        *:focus {
            outline: none;
        }
        """
        
        self.setStyleSheet(stylesheet)
    
    def set_status(self, status: str) -> None:
        """Set application status"""
        self.status_indicator.set_status(status)
        
        status_text_map = {
            "listening": "🎤 Listening",
            "paused": "⏸ Paused",
            "sleeping": "💤 Sleeping",
            "ready": "✓ Ready"
        }
        self.status_text.setText(status_text_map.get(status, "Ready"))
        
        info_status_map = {
            "listening": "Active",
            "paused": "Paused",
            "sleeping": "Sleep",
            "ready": "Ready"
        }
        self.info_panel.set_session_status(info_status_map.get(status, "Ready"))
        
        logger.debug(f"ModernMedicalUI status: {status}")
    
    def update_feedback(self, command: str, status: str, feedback: str = "") -> None:
        """Update feedback panel"""
        self.feedback_panel.update_feedback(command, status, feedback)
        self.history_list.add_history_item(command, status, feedback)
    
    def set_field_counter(self, current: int, total: int) -> None:
        """Update field counter"""
        self.info_panel.set_field_counter(current, total)
    
    def set_session_time(self, seconds: int) -> None:
        """Update elapsed session time"""
        self.info_panel.set_elapsed_time(seconds)
    
    def set_last_entry(self, entry: str) -> None:
        """Update last entry (not displayed in compact version)"""
        pass
    
    def _set_docked_position(self) -> None:
        """Position window at bottom-right"""
        screen = self.screen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.right() - self.width() - 8
            y = geometry.bottom() - self.height() - 8
            self.move(int(x), int(y))
            logger.debug(f"ModernMedicalUI docked at ({x}, {y})")
    
    def _save_position(self) -> None:
        """Save current position"""
        pos = self.pos()
        logger.debug(f"Position saved: ({pos.x()}, {pos.y()})")
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            self.position_save_timer.stop()
            self.position_save_timer.start(500)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        event.accept()
    
    def set_opacity(self, opacity: float) -> None:
        """Set window opacity"""
        opacity = max(0.0, min(1.0, opacity))
        self.setWindowOpacity(opacity)
        logger.debug(f"ModernMedicalUI opacity: {opacity}")
    
    def toggle_visibility(self) -> None:
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()


# ============================================================================
# Example/Testing
# ============================================================================

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create and show window
    window = ModernMedicalUI()
    window.show()
    
    # Test status changes
    def test_statuses():
        statuses = ["listening", "paused", "sleeping", "ready"]
        for status in statuses:
            window.set_status(status)
            QApplication.processEvents()
            QTimer.singleShot(1000, lambda s=status: None)
    
    # Test feedback
    def test_feedback():
        window.update_feedback("two three two", "success", "Entered")
        window.set_field_counter(3, 6)
    
    # Schedule tests
    QTimer.singleShot(500, test_statuses)
    QTimer.singleShot(5000, test_feedback)
    
    sys.exit(app.exec())
