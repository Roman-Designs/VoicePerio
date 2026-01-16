"""
System Tray Icon - System tray management and menu

Provides system tray icon with context menu for application control.
Allows minimization to taskbar, status display, and quick access to settings.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from pathlib import Path
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class SystemTraySignals(QObject):
    """Signals for SystemTray events"""
    
    show_hide_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    toggle_listening_requested = pyqtSignal()


class SystemTray:
    """
    System tray icon and context menu management.
    
    Features:
    - System tray icon with application logo
    - Show/Hide menu to toggle main window
    - Settings menu to open configuration
    - Exit menu to close application
    - Status indicator (Listening/Paused/Sleeping)
    - Double-click to show/hide main window
    - Right-click for context menu
    
    Example:
        >>> tray = SystemTray(app)
        >>> tray.setup()
        >>> tray.set_listening()
        >>> tray.show_message("Success", "Command executed")
    """
    
    def __init__(self, parent=None):
        """
        Initialize system tray.
        
        Args:
            parent: Parent widget (typically QApplication)
        """
        self.parent = parent
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.menu: Optional[QMenu] = None
        self.signals = SystemTraySignals()
        self.icon_path = Path(__file__).parent / "resources" / "voiceperio.png"
        self.status = "Ready"
        logger.debug(f"SystemTray initialized with icon: {self.icon_path}")
    
    def setup(self) -> bool:
        """
        Initialize system tray icon and menu.
        
        Returns:
            True if setup successful
            
        Example:
            >>> tray = SystemTray(app)
            >>> if tray.setup():
            ...     tray.show()
        """
        try:
            # Create system tray icon
            self.tray_icon = QSystemTrayIcon(self.parent)
            
            # Load and set icon
            if self.icon_path.exists():
                icon = QIcon(str(self.icon_path))
                self.tray_icon.setIcon(icon)
                logger.debug(f"Loaded tray icon from {self.icon_path}")
            else:
                logger.warning(f"Icon file not found: {self.icon_path}")
                # Create a default icon if file not found
                icon = self._create_default_icon()
                self.tray_icon.setIcon(icon)
            
            # Create context menu
            self._create_menu()
            
            # Connect signals
            self.tray_icon.activated.connect(self._on_tray_activated)
            
            logger.info("SystemTray setup completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error setting up system tray: {e}")
            return False
    
    def _create_menu(self) -> None:
        """
        Create context menu with options.
        
        Menu items:
        - Show/Hide
        - Settings
        - Exit
        """
        self.menu = QMenu()
        
        # Show/Hide action
        show_hide_action = self.menu.addAction("Show/Hide")
        show_hide_action.triggered.connect(self._on_show_hide)
        
        # Settings action
        settings_action = self.menu.addAction("Settings")
        settings_action.triggered.connect(self._on_settings)
        
        # Toggle listening action
        self.toggle_action = self.menu.addAction("Pause Listening")
        self.toggle_action.triggered.connect(self._on_toggle_listening)
        
        # Separator
        self.menu.addSeparator()
        
        # Exit action
        exit_action = self.menu.addAction("Exit")
        exit_action.triggered.connect(self._on_exit)
        
        self.tray_icon.setContextMenu(self.menu)
        logger.debug("Context menu created with 5 items")
    
    def show(self) -> None:
        """
        Show the system tray icon.
        
        Example:
            >>> tray.show()
        """
        if self.tray_icon:
            self.tray_icon.show()
            logger.debug("System tray icon shown")
    
    def hide(self) -> None:
        """
        Hide the system tray icon.
        
        Example:
            >>> tray.hide()
        """
        if self.tray_icon:
            self.tray_icon.hide()
            logger.debug("System tray icon hidden")
    
    def set_listening(self) -> None:
        """
        Update tray to show listening status.
        
        Example:
            >>> tray.set_listening()
        """
        self.status = "Listening"
        if self.toggle_action:
            self.toggle_action.setText("Pause Listening")
        self._update_tooltip()
        logger.debug("SystemTray status: Listening")
    
    def set_paused(self) -> None:
        """
        Update tray to show paused status.
        
        Example:
            >>> tray.set_paused()
        """
        self.status = "Paused"
        if self.toggle_action:
            self.toggle_action.setText("Resume Listening")
        self._update_tooltip()
        logger.debug("SystemTray status: Paused")
    
    def set_sleeping(self) -> None:
        """
        Update tray to show sleeping status.
        
        Example:
            >>> tray.set_sleeping()
        """
        self.status = "Sleeping"
        if self.toggle_action:
            self.toggle_action.setText("Wake Up")
        self._update_tooltip()
        logger.debug("SystemTray status: Sleeping")
    
    def _update_tooltip(self) -> None:
        """Update tooltip with current status"""
        if self.tray_icon:
            tooltip = f"VoicePerio - {self.status}"
            self.tray_icon.setToolTip(tooltip)
    
    def show_message(self, title: str, message: str, duration_ms: int = 10000) -> None:
        """
        Show a system tray notification message.
        
        Args:
            title: Notification title
            message: Notification message
            duration_ms: Duration in milliseconds (default: 10000)
            
        Example:
            >>> tray.show_message("Success", "Command executed successfully")
        """
        if self.tray_icon:
            try:
                # Use showMessage which works across platforms
                self.tray_icon.showMessage(
                    title,
                    message,
                    QSystemTrayIcon.MessageIcon.Information,
                    duration_ms
                )
                logger.debug(f"Tray notification: {title} - {message}")
            except Exception as e:
                logger.error(f"Error showing tray message: {e}")
    
    def _on_tray_activated(self, reason) -> None:
        """
        Handle tray icon activation (double-click, single-click, etc).
        
        Args:
            reason: Activation reason
        """
        # Double-click to show/hide
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.signals.show_hide_requested.emit()
            logger.debug("Tray double-click detected")
    
    def _on_show_hide(self) -> None:
        """Handle Show/Hide menu action"""
        self.signals.show_hide_requested.emit()
        logger.debug("Show/Hide action triggered")
    
    def _on_settings(self) -> None:
        """Handle Settings menu action"""
        self.signals.settings_requested.emit()
        logger.debug("Settings action triggered")
    
    def _on_toggle_listening(self) -> None:
        """Handle Toggle Listening menu action"""
        self.signals.toggle_listening_requested.emit()
        logger.debug("Toggle listening action triggered")
    
    def _on_exit(self) -> None:
        """Handle Exit menu action"""
        self.signals.exit_requested.emit()
        logger.debug("Exit action triggered")
    
    @staticmethod
    def _create_default_icon() -> QIcon:
        """
        Create a default icon if logo not found.
        
        Returns:
            QIcon with default appearance
        """
        icon = QIcon()
        # Create a colored pixmap as fallback
        from PyQt6.QtGui import QPixmap
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#2196F3"))  # Blue color
        icon.addPixmap(pixmap)
        return icon
    
    def is_visible(self) -> bool:
        """
        Check if tray icon is visible.
        
        Returns:
            True if visible
        """
        if self.tray_icon:
            return self.tray_icon.isVisible()
        return False
    
    def set_icon(self, icon_path: str) -> bool:
        """
        Set custom icon from file path.
        
        Args:
            icon_path: Path to icon file
            
        Returns:
            True if icon set successfully
        """
        try:
            path = Path(icon_path)
            if path.exists():
                icon = QIcon(str(path))
                if self.tray_icon:
                    self.tray_icon.setIcon(icon)
                logger.debug(f"Custom icon set from {icon_path}")
                return True
            else:
                logger.error(f"Icon file not found: {icon_path}")
                return False
        except Exception as e:
            logger.error(f"Error setting custom icon: {e}")
            return False
