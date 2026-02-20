"""
GUI Manager - Orchestrates all GUI components

Coordinates the system tray, floating indicator, and settings dialog.
Handles signals and updates from the main application.
Thread-safe GUI updates using Qt signals/slots.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from .system_tray import SystemTray
from .floating_indicator import FloatingIndicator
from .settings_dialog import SettingsDialog
from .modern_medical_ui import ModernMedicalUI

logger = logging.getLogger(__name__)


class GUIManagerSignals(QObject):
    """Signals emitted by GUIManager"""
    
    status_changed = pyqtSignal(str)  # Status text
    command_feedback = pyqtSignal(str)  # Command text
    listening_toggled = pyqtSignal(bool)  # True=listening, False=paused
    settings_changed = pyqtSignal(dict)  # Settings dict
    exit_requested = pyqtSignal()


class GUIManager(QObject):
    """
    System tray and floating indicator management.
    
    Orchestrates all GUI components:
    - SystemTray: Icon in system tray with context menu
    - FloatingIndicator: Small window showing listening status
    - SettingsDialog: Configuration dialog
    
    Thread-safe operations with proper signal/slot connections.
    
    Features:
    - Show/hide main window via system tray
    - Real-time status updates (Listening/Paused/Sleeping)
    - Settings management with persistence
    - Command feedback display
    - Signal coordination between components
    - Thread-safe GUI updates
    
    Example:
        >>> gui_manager = GUIManager(config_manager, app)
        >>> gui_manager.setup()
        >>> gui_manager.set_listening()
        >>> gui_manager.show_command_feedback("three two three")
    """
    
    def __init__(self, config_manager=None, app: Optional[QApplication] = None, use_modern_ui: bool = True):
        """
        Initialize GUI Manager.
        
        Args:
            config_manager: ConfigManager instance for settings persistence
            app: QApplication instance
            use_modern_ui: Use new ModernMedicalUI instead of FloatingIndicator (default True)
        """
        super().__init__()
        self.config = config_manager
        self.app = app or QApplication.instance()
        self.use_modern_ui = use_modern_ui
        
        # Components
        self.tray: Optional[SystemTray] = None
        self.indicator: Optional[FloatingIndicator] = None
        self.modern_ui: Optional[ModernMedicalUI] = None
        self.settings_dialog: Optional[SettingsDialog] = None
        
        # State tracking
        self.is_listening = False
        self.is_visible = True
        self.current_status = "Ready"
        self.session_time_seconds = 0
        
        # Signals
        self.signals = GUIManagerSignals()
        
        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(False)
        self.update_timer.timeout.connect(self._on_update_timer)
        
        # Session timer (for elapsed time tracking)
        self.session_timer = QTimer()
        self.session_timer.setSingleShot(False)
        self.session_timer.timeout.connect(self._on_session_timer)
        
        logger.debug("GUIManager initialized")
    
    def setup(self) -> bool:
        """
        Initialize all GUI components.
        
        Returns:
            True if setup successful
            
        Example:
            >>> manager = GUIManager(config)
            >>> if manager.setup():
            ...     manager.show()
        """
        try:
            # Create system tray
            self.tray = SystemTray(self.app)
            if not self.tray.setup():
                logger.error("Failed to setup system tray")
                return False
            
            # Create appropriate UI based on setting
            if self.use_modern_ui:
                self.modern_ui = ModernMedicalUI()
                logger.debug("ModernMedicalUI created")
            else:
                self.indicator = FloatingIndicator()
                logger.debug("FloatingIndicator created")
            
            # Create settings dialog
            self.settings_dialog = SettingsDialog(self.config)
            
            # Connect signals
            self._connect_signals()
            
            # Load settings
            self._apply_settings()
            
            logger.info("GUIManager setup completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error setting up GUIManager: {e}")
            return False
    
    def _connect_signals(self) -> None:
        """Connect signals between components"""
        # System tray signals
        if self.tray:
            self.tray.signals.show_hide_requested.connect(self.toggle_visibility)
            self.tray.signals.settings_requested.connect(self.show_settings)
            self.tray.signals.toggle_listening_requested.connect(self.toggle_listening)
            self.tray.signals.exit_requested.connect(self.signals.exit_requested.emit)
        
        # Floating indicator signals (old UI)
        if self.indicator:
            self.indicator.close_requested.connect(self.hide_indicator)
        
        # Modern medical UI signals
        if self.modern_ui:
            self.modern_ui.pause_requested.connect(self.toggle_listening)
            self.modern_ui.settings_requested.connect(self.show_settings)
            self.modern_ui.exit_requested.connect(self.signals.exit_requested.emit)
        
        # Settings dialog signals
        if self.settings_dialog:
            self.settings_dialog.settings_changed.connect(self._on_settings_changed)
        
        # Internal signals
        self.signals.status_changed.connect(self._on_status_changed)
        self.signals.command_feedback.connect(self._on_command_feedback)
        
        logger.debug("Signals connected")
    
    def show(self) -> None:
        """
        Show all GUI components.
        
        Example:
            >>> manager.show()
        """
        if self.tray:
            self.tray.show()
        
        # Show appropriate UI
        if self.use_modern_ui:
            if self.modern_ui and self.config and self.config.get("gui.show_floating_indicator", True):
                self.modern_ui.show()
        else:
            if self.indicator and self.config and self.config.get("gui.show_floating_indicator", True):
                self.indicator.show()
        
        self.is_visible = True
        logger.debug("GUIManager components shown")
    
    def hide(self) -> None:
        """
        Hide all GUI components.
        
        Example:
            >>> manager.hide()
        """
        if self.tray:
            self.tray.hide()
        
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.hide()
        else:
            if self.indicator:
                self.indicator.hide()
        
        self.is_visible = False
        logger.debug("GUIManager components hidden")
    
    def show_indicator(self) -> None:
        """
        Show the floating indicator / modern UI.
        
        Example:
            >>> manager.show_indicator()
        """
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.show()
                logger.debug("Modern medical UI shown")
        else:
            if self.indicator:
                self.indicator.show()
                logger.debug("Floating indicator shown")
    
    def hide_indicator(self) -> None:
        """
        Hide the floating indicator / modern UI.
        
        Example:
            >>> manager.hide_indicator()
        """
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.hide()
                logger.debug("Modern medical UI hidden")
        else:
            if self.indicator:
                self.indicator.hide()
                logger.debug("Floating indicator hidden")
    
    def toggle_visibility(self) -> None:
        """
        Toggle visibility of all components.
        
        Example:
            >>> manager.toggle_visibility()
        """
        if self.is_visible:
            self.hide()
        else:
            self.show()
        logger.debug(f"Visibility toggled: {self.is_visible}")
    
    def set_listening(self) -> None:
        """
        Set status to listening.
        
        Example:
            >>> manager.set_listening()
        """
        self.is_listening = True
        self.current_status = "Listening"
        if self.tray:
            self.tray.set_listening()
        
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.set_status("listening")
        else:
            if self.indicator:
                self.indicator.set_listening()
        
        logger.debug("Status set to: Listening")
    
    def set_paused(self) -> None:
        """
        Set status to paused.
        
        Example:
            >>> manager.set_paused()
        """
        self.is_listening = False
        self.current_status = "Paused"
        if self.tray:
            self.tray.set_paused()
        
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.set_status("paused")
        else:
            if self.indicator:
                self.indicator.set_paused()
        
        logger.debug("Status set to: Paused")
    
    def set_sleeping(self) -> None:
        """
        Set status to sleeping.
        
        Example:
            >>> manager.set_sleeping()
        """
        self.is_listening = False
        self.current_status = "Sleeping"
        if self.tray:
            self.tray.set_sleeping()
        
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.set_status("sleeping")
        else:
            if self.indicator:
                self.indicator.set_sleeping()
        
        logger.debug("Status set to: Sleeping")
    
    def set_ready(self) -> None:
        """
        Set status to ready.
        
        Example:
            >>> manager.set_ready()
        """
        self.is_listening = False
        self.current_status = "Ready"
        
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.set_status("ready")
        else:
            if self.indicator:
                self.indicator.set_ready()
        
        logger.debug("Status set to: Ready")
    
    def update_status(self, text: str) -> None:
        """
        Update status text.
        
        Thread-safe using signals.
        
        Args:
            text: Status text to display
            
        Example:
            >>> manager.update_status("Listening for commands...")
        """
        self.signals.status_changed.emit(text)
    
    def show_command_feedback(self, command: str) -> None:
        """
        Display feedback for recognized command.
        
        Thread-safe using signals.
        
        Args:
            command: Command text to display
            
        Example:
            >>> manager.show_command_feedback("three two three")
        """
        self.signals.command_feedback.emit(command)
    
    def toggle_listening(self) -> None:
        """
        Toggle between listening and paused states.
        
        Example:
            >>> manager.toggle_listening()
        """
        if self.is_listening:
            self.set_paused()
            self.signals.listening_toggled.emit(False)
        else:
            self.set_listening()
            self.signals.listening_toggled.emit(True)
        logger.debug(f"Listening toggled: {self.is_listening}")
    
    def show_settings(self) -> None:
        """
        Show settings dialog (modal).
        
        Example:
            >>> manager.show_settings()
        """
        if self.settings_dialog:
            self.settings_dialog.exec()
            logger.debug("Settings dialog shown")
    
    def _on_status_changed(self, text: str) -> None:
        """Handle status change signal"""
        if self.indicator:
            # This can be used for additional status updates
            pass
    
    def _on_command_feedback(self, command: str) -> None:
        """Handle command feedback signal"""
        if self.use_modern_ui:
            if self.modern_ui:
                self.modern_ui.update_feedback(command, "success", "Recognized")
        else:
            if self.indicator:
                self.indicator.update_command(command)
    
    def _on_settings_changed(self, settings: Dict[str, Any]) -> None:
        """Handle settings change from dialog"""
        self._apply_settings()
        self.signals.settings_changed.emit(settings)
        logger.debug(f"Settings changed: {settings}")
    
    def _apply_settings(self) -> None:
        """Apply current settings to GUI components"""
        if not self.config:
            return
        
        try:
            # Apply opacity
            opacity = self.config.get("gui.indicator_opacity", 0.9)
            
            if self.use_modern_ui:
                if self.modern_ui:
                    self.modern_ui.set_opacity(opacity)
            else:
                if self.indicator:
                    self.indicator.set_opacity(opacity)
            
            # Show/hide indicator
            show_indicator = self.config.get("gui.show_floating_indicator", True)
            
            if self.use_modern_ui:
                if self.modern_ui:
                    if show_indicator and self.is_visible:
                        self.modern_ui.show()
                    else:
                        self.modern_ui.hide()
            else:
                if self.indicator:
                    if show_indicator and self.is_visible:
                        self.indicator.show()
                    else:
                        self.indicator.hide()
            
            logger.debug("Settings applied to GUI components")
        
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
    
    def _on_update_timer(self) -> None:
        """Periodic update handler"""
        # Can be used for regular UI updates
        pass
    
    def start_update_timer(self, interval_ms: int = 1000) -> None:
        """
        Start periodic update timer.
        
        Args:
            interval_ms: Update interval in milliseconds
        """
        self.update_timer.setInterval(interval_ms)
        self.update_timer.start()
        logger.debug(f"Update timer started ({interval_ms}ms)")
    
    def stop_update_timer(self) -> None:
        """Stop periodic update timer"""
        self.update_timer.stop()
        logger.debug("Update timer stopped")
    
    def show_notification(self, title: str, message: str) -> None:
        """
        Show system tray notification.
        
        Args:
            title: Notification title
            message: Notification message
            
        Example:
            >>> manager.show_notification("Success", "Settings saved")
        """
        if self.tray:
            self.tray.show_message(title, message)
            logger.debug(f"Notification: {title} - {message}")
    
    def set_indicator_position(self, x: int, y: int) -> None:
        """
        Set floating indicator position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        if self.indicator:
            self.indicator.set_position(x, y)
            logger.debug(f"Indicator positioned at ({x}, {y})")
    
    def get_indicator_position(self) -> tuple:
        """
        Get current floating indicator position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        if self.indicator:
            return self.indicator.get_position()
        return (0, 0)
    
    def cleanup(self) -> None:
        """
        Clean up resources before exit.
        
        Example:
            >>> manager.cleanup()
        """
        try:
            self.stop_update_timer()
            self.stop_session_timer()
            
            if self.use_modern_ui:
                if self.modern_ui:
                    self.modern_ui.close()
            else:
                if self.indicator:
                    self.indicator.close()
            
            if self.settings_dialog:
                self.settings_dialog.close()
            if self.tray:
                self.tray.hide()
            logger.info("GUIManager cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def is_listening_status(self) -> bool:
        """
        Check if currently in listening status.
        
        Returns:
            True if listening
        """
        return self.is_listening
    
    def get_status(self) -> str:
        """
        Get current status string.
        
        Returns:
            Status text
        """
        return self.current_status
    
    def _on_session_timer(self) -> None:
        """Update session time on modern UI"""
        self.session_time_seconds += 1
        if self.use_modern_ui and self.modern_ui:
            self.modern_ui.set_session_time(self.session_time_seconds)
    
    def start_session_timer(self) -> None:
        """Start tracking session elapsed time"""
        self.session_time_seconds = 0
        self.session_timer.setInterval(1000)
        self.session_timer.start()
    
    def stop_session_timer(self) -> None:
        """Stop tracking session elapsed time"""
        self.session_timer.stop()
    
    def set_field_counter(self, current: int, total: int) -> None:
        """Update field counter on modern UI"""
        if self.use_modern_ui and self.modern_ui:
            self.modern_ui.set_field_counter(current, total)
    
    def set_last_entry(self, entry: str) -> None:
        """Update last entry on modern UI"""
        if self.use_modern_ui and self.modern_ui:
            self.modern_ui.set_last_entry(entry)
