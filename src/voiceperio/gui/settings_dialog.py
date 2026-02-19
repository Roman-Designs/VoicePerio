"""
Settings Dialog - Configuration and settings management UI

Provides a comprehensive settings dialog with multiple tabs for configuring
audio devices, behavior, target window, GUI preferences, and hotkeys.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
    QSpinBox, QSlider, QCheckBox, QComboBox, QPushButton, QFormLayout,
    QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """
    Settings dialog for user configuration.
    
    Provides tabs for:
    - Audio: Device selection, sample rate configuration
    - Behavior: Tab after sequence, keystroke delay, auto-advance
    - Target Window: Window title pattern, auto-focus
    - GUI: Floating indicator, opacity level
    - Hotkeys: Global hotkey configuration
    
    Features:
    - Live preview of settings
    - Validation before saving
    - Reset to defaults option
    - Settings persistence to config.json
    
    Example:
        >>> dialog = SettingsDialog(config_manager)
        >>> if dialog.exec() == QDialog.DialogCode.Accepted:
        ...     # Settings saved
    """
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config_manager=None, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            config_manager: ConfigManager instance for loading/saving
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config_manager
        self.original_settings: Dict[str, Any] = {}
        
        self.setWindowTitle("VoicePerio Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        self.init_ui()
        self.load_settings()
        
        logger.debug("SettingsDialog initialized")
    
    def init_ui(self) -> None:
        """Initialize the UI with tabs"""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self._create_audio_tab(), "Audio")
        self.tab_widget.addTab(self._create_behavior_tab(), "Behavior")
        self.tab_widget.addTab(self._create_target_tab(), "Target Window")
        self.tab_widget.addTab(self._create_gui_tab(), "GUI")
        self.tab_widget.addTab(self._create_hotkeys_tab(), "Hotkeys")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self._on_reset)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        logger.debug("SettingsDialog UI created")
    
    def _create_audio_tab(self) -> QGroupBox:
        """Create audio settings tab"""
        group = QGroupBox("Audio Settings")
        layout = QFormLayout()
        
        # Device selection
        self.device_combo = QComboBox()
        self.device_combo.addItem("Default Device")
        self.device_combo.addItem("Device 1")
        self.device_combo.addItem("Device 2")
        layout.addRow("Audio Device:", self.device_combo)
        
        # Sample rate
        self.sample_rate_spinbox = QSpinBox()
        self.sample_rate_spinbox.setMinimum(8000)
        self.sample_rate_spinbox.setMaximum(48000)
        self.sample_rate_spinbox.setValue(16000)
        self.sample_rate_spinbox.setSingleStep(1000)
        layout.addRow("Sample Rate (Hz):", self.sample_rate_spinbox)
        
        # Chunk size
        self.chunk_size_spinbox = QSpinBox()
        self.chunk_size_spinbox.setMinimum(1000)
        self.chunk_size_spinbox.setMaximum(16000)
        self.chunk_size_spinbox.setValue(4000)
        self.chunk_size_spinbox.setSingleStep(1000)
        layout.addRow("Chunk Size:", self.chunk_size_spinbox)
        
        group.setLayout(layout)
        return group
    
    def _create_behavior_tab(self) -> QGroupBox:
        """Create behavior settings tab"""
        group = QGroupBox("Behavior Settings")
        layout = QFormLayout()
        
        # Tab after sequence
        self.tab_after_check = QCheckBox("Tab after entering sequence")
        self.tab_after_check.setChecked(True)
        layout.addRow(self.tab_after_check)
        
        # Keystroke delay
        delay_layout = QHBoxLayout()
        self.keystroke_slider = QSlider(Qt.Orientation.Horizontal)
        self.keystroke_slider.setMinimum(10)
        self.keystroke_slider.setMaximum(500)
        self.keystroke_slider.setValue(50)
        self.keystroke_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.keystroke_slider.setTickInterval(50)
        
        self.keystroke_label = QLabel("50 ms")
        self.keystroke_slider.valueChanged.connect(
            lambda v: self.keystroke_label.setText(f"{v} ms")
        )
        
        delay_layout.addWidget(self.keystroke_slider)
        delay_layout.addWidget(self.keystroke_label, 0, Qt.AlignmentFlag.AlignRight)
        layout.addRow("Keystroke Delay:", delay_layout)
        
        # Auto-advance tooth
        self.auto_advance_check = QCheckBox("Auto-advance to next tooth")
        self.auto_advance_check.setChecked(False)
        layout.addRow(self.auto_advance_check)

        # Audio feedback mode
        self.feedback_mode_combo = QComboBox()
        self.feedback_mode_combo.addItem("Off", "off")
        self.feedback_mode_combo.addItem("Chime", "chime")
        self.feedback_mode_combo.addItem("Readback", "readback")
        self.feedback_mode_combo.currentIndexChanged.connect(lambda _: self._update_feedback_controls())
        layout.addRow("Audio Feedback:", self.feedback_mode_combo)

        # Readback speech rate
        self.readback_rate_spinbox = QSpinBox()
        self.readback_rate_spinbox.setMinimum(-5)
        self.readback_rate_spinbox.setMaximum(8)
        self.readback_rate_spinbox.setValue(3)
        layout.addRow("Readback Speed:", self.readback_rate_spinbox)

        # Readback max chars
        self.readback_max_chars_spinbox = QSpinBox()
        self.readback_max_chars_spinbox.setMinimum(8)
        self.readback_max_chars_spinbox.setMaximum(80)
        self.readback_max_chars_spinbox.setValue(32)
        layout.addRow("Readback Max Chars:", self.readback_max_chars_spinbox)

        group.setLayout(layout)
        return group

    def _update_feedback_controls(self) -> None:
        """Enable readback controls only when readback mode is selected."""
        is_readback = self.feedback_mode_combo.currentData() == "readback"
        self.readback_rate_spinbox.setEnabled(is_readback)
        self.readback_max_chars_spinbox.setEnabled(is_readback)
    
    def _create_target_tab(self) -> QGroupBox:
        """Create target window settings tab"""
        group = QGroupBox("Target Window Settings")
        layout = QFormLayout()
        
        # Window title
        self.window_title_edit = QLineEdit()
        self.window_title_edit.setPlaceholderText("e.g., Dentrix, Open Dental, Eaglesoft")
        layout.addRow("Target Window Title:", self.window_title_edit)
        
        # Auto-focus
        self.auto_focus_check = QCheckBox("Auto-focus target window")
        self.auto_focus_check.setChecked(True)
        layout.addRow(self.auto_focus_check)
        
        # Match method
        self.match_method_combo = QComboBox()
        self.match_method_combo.addItem("Contains")
        self.match_method_combo.addItem("Exact Match")
        self.match_method_combo.addItem("Starts With")
        layout.addRow("Window Match Method:", self.match_method_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_gui_tab(self) -> QGroupBox:
        """Create GUI settings tab"""
        group = QGroupBox("GUI Settings")
        layout = QFormLayout()
        
        # Floating indicator
        self.show_indicator_check = QCheckBox("Show floating indicator")
        self.show_indicator_check.setChecked(True)
        layout.addRow(self.show_indicator_check)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(20)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(90)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        
        self.opacity_label = QLabel("90%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label, 0, Qt.AlignmentFlag.AlignRight)
        layout.addRow("Floating Indicator Opacity:", opacity_layout)
        
        # Command feedback
        self.command_feedback_check = QCheckBox("Show command feedback")
        self.command_feedback_check.setChecked(True)
        layout.addRow(self.command_feedback_check)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark (Default)")
        self.theme_combo.addItem("Light")
        layout.addRow("Theme:", self.theme_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_hotkeys_tab(self) -> QGroupBox:
        """Create hotkeys settings tab"""
        group = QGroupBox("Hotkey Settings")
        layout = QFormLayout()
        
        # Toggle listening hotkey
        self.toggle_hotkey_edit = QLineEdit()
        self.toggle_hotkey_edit.setPlaceholderText("e.g., ctrl+shift+v")
        self.toggle_hotkey_edit.setText("ctrl+shift+v")
        layout.addRow("Toggle Listening:", self.toggle_hotkey_edit)
        
        # Pause hotkey
        self.pause_hotkey_edit = QLineEdit()
        self.pause_hotkey_edit.setPlaceholderText("Leave empty to disable")
        layout.addRow("Pause Listening:", self.pause_hotkey_edit)
        
        # Wake hotkey
        self.wake_hotkey_edit = QLineEdit()
        self.wake_hotkey_edit.setPlaceholderText("Leave empty to disable")
        layout.addRow("Wake/Resume:", self.wake_hotkey_edit)
        
        # Exit hotkey
        self.exit_hotkey_edit = QLineEdit()
        self.exit_hotkey_edit.setPlaceholderText("Leave empty to disable")
        layout.addRow("Exit Application:", self.exit_hotkey_edit)
        
        info_label = QLabel("Note: Hotkeys are global and work even when app is minimized")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow(info_label)
        
        group.setLayout(layout)
        return group
    
    def load_settings(self) -> None:
        """Load current settings from config"""
        try:
            if not self.config:
                logger.warning("No config manager provided")
                return
            
            # Audio settings
            device_id = self.config.get("audio.device_id", None)
            if device_id is not None:
                self.device_combo.setCurrentIndex(min(device_id, self.device_combo.count() - 1))
            
            self.sample_rate_spinbox.setValue(self.config.get("audio.sample_rate", 16000))
            self.chunk_size_spinbox.setValue(self.config.get("audio.chunk_size", 4000))
            
            # Behavior settings
            self.tab_after_check.setChecked(self.config.get("behavior.tab_after_sequence", True))
            self.keystroke_slider.setValue(self.config.get("behavior.keystroke_delay_ms", 50))
            self.auto_advance_check.setChecked(self.config.get("behavior.auto_advance_tooth", False))
            feedback_mode = self.config.get("behavior.audio_feedback_mode", "off")
            mode_index = self.feedback_mode_combo.findData(feedback_mode)
            self.feedback_mode_combo.setCurrentIndex(mode_index if mode_index >= 0 else 0)
            self.readback_rate_spinbox.setValue(self.config.get("behavior.readback_rate", 3))
            self.readback_max_chars_spinbox.setValue(self.config.get("behavior.readback_max_chars", 32))
            self._update_feedback_controls()
            
            # Target settings
            self.window_title_edit.setText(self.config.get("target.window_title", "Dentrix"))
            self.auto_focus_check.setChecked(self.config.get("target.auto_focus", True))
            
            # GUI settings
            self.show_indicator_check.setChecked(self.config.get("gui.show_floating_indicator", True))
            self.opacity_slider.setValue(int(self.config.get("gui.indicator_opacity", 0.9) * 100))
            self.command_feedback_check.setChecked(self.config.get("gui.show_command_feedback", True))
            
            # Hotkey settings
            self.toggle_hotkey_edit.setText(self.config.get("hotkey.toggle_listening", "ctrl+shift+v"))
            
            logger.info("Settings loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self) -> bool:
        """
        Save settings changes to config.
        
        Returns:
            True if saved successfully
        """
        try:
            if not self.config:
                logger.warning("No config manager provided")
                return False
            
            # Audio settings
            self.config.set("audio.sample_rate", self.sample_rate_spinbox.value())
            self.config.set("audio.chunk_size", self.chunk_size_spinbox.value())
            
            # Behavior settings
            self.config.set("behavior.tab_after_sequence", self.tab_after_check.isChecked())
            self.config.set("behavior.keystroke_delay_ms", self.keystroke_slider.value())
            self.config.set("behavior.auto_advance_tooth", self.auto_advance_check.isChecked())
            self.config.set("behavior.audio_feedback_mode", self.feedback_mode_combo.currentData())
            self.config.set("behavior.readback_rate", self.readback_rate_spinbox.value())
            self.config.set("behavior.readback_max_chars", self.readback_max_chars_spinbox.value())
            
            # Target settings
            self.config.set("target.window_title", self.window_title_edit.text())
            self.config.set("target.auto_focus", self.auto_focus_check.isChecked())
            
            # GUI settings
            self.config.set("gui.show_floating_indicator", self.show_indicator_check.isChecked())
            self.config.set("gui.indicator_opacity", self.opacity_slider.value() / 100.0)
            self.config.set("gui.show_command_feedback", self.command_feedback_check.isChecked())
            
            # Hotkey settings
            self.config.set("hotkey.toggle_listening", self.toggle_hotkey_edit.text())
            
            # Emit signal with changed settings
            settings = {
                "tab_after_sequence": self.tab_after_check.isChecked(),
                "keystroke_delay_ms": self.keystroke_slider.value(),
                "audio_feedback_mode": self.feedback_mode_combo.currentData(),
                "readback_rate": self.readback_rate_spinbox.value(),
                "readback_max_chars": self.readback_max_chars_spinbox.value(),
                "show_floating_indicator": self.show_indicator_check.isChecked(),
                "indicator_opacity": self.opacity_slider.value() / 100.0,
                "window_title": self.window_title_edit.text(),
            }
            self.settings_changed.emit(settings)
            
            logger.info("Settings saved successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def _validate_settings(self) -> bool:
        """
        Validate settings before saving.
        
        Returns:
            True if all settings are valid
        """
        # Validate window title
        if not self.window_title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Target window title cannot be empty")
            return False
        
        # Validate hotkey format (basic check)
        hotkey_text = self.toggle_hotkey_edit.text().strip()
        if hotkey_text and '+' not in hotkey_text:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Hotkey must be in format: ctrl+shift+v or similar"
            )
            return False
        
        return True
    
    def _on_ok(self) -> None:
        """Handle OK button"""
        if self._validate_settings():
            if self.save_settings():
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save settings")
    
    def _on_reset(self) -> None:
        """Handle reset to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.config:
                self.config.config = self.config.DEFAULT_CONFIG.copy()
                self.config.save()
            self.load_settings()
            logger.info("Settings reset to defaults")
