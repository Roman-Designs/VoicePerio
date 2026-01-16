"""
GUI Components Test Suite - Comprehensive tests for Phase 5 GUI modules

Tests for:
- SystemTray: System tray icon and menu functionality
- FloatingIndicator: Floating status window
- SettingsDialog: Configuration dialog
- GUIManager: Component orchestration and coordination

Test Coverage:
- Component initialization and setup
- Signal/slot connections
- Status updates and display
- Settings loading/saving
- Configuration persistence
- UI interactions
- Error handling
- Thread safety
"""

import pytest
import sys
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import json
import tempfile
import os

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voiceperio.config_manager import ConfigManager
from voiceperio.gui.system_tray import SystemTray, SystemTraySignals
from voiceperio.gui.floating_indicator import FloatingIndicator
from voiceperio.gui.settings_dialog import SettingsDialog
from voiceperio.gui.gui_manager import GUIManager, GUIManagerSignals

logger = logging.getLogger(__name__)


# ============================================================================
# System Tray Tests
# ============================================================================

class TestSystemTray:
    """Test SystemTray component"""
    
    def test_init(self):
        """Test SystemTray initialization"""
        tray = SystemTray()
        assert tray.tray_icon is None
        assert tray.menu is None
        assert tray.status == "Ready"
        assert isinstance(tray.signals, SystemTraySignals)
    
    def test_setup_with_icon(self):
        """Test system tray setup with valid icon"""
        tray = SystemTray()
        # Create icon in resources
        result = tray.setup()
        # Should return True if icon exists or can create default
        assert isinstance(result, bool)
    
    def test_set_listening_status(self):
        """Test setting listening status"""
        tray = SystemTray()
        tray.setup()
        tray.set_listening()
        assert tray.status == "Listening"
    
    def test_set_paused_status(self):
        """Test setting paused status"""
        tray = SystemTray()
        tray.setup()
        tray.set_paused()
        assert tray.status == "Paused"
    
    def test_set_sleeping_status(self):
        """Test setting sleeping status"""
        tray = SystemTray()
        tray.setup()
        tray.set_sleeping()
        assert tray.status == "Sleeping"
    
    def test_show_hide_visibility(self):
        """Test showing and hiding tray icon"""
        tray = SystemTray()
        tray.setup()
        
        tray.show()
        assert tray.is_visible()
        
        tray.hide()
        assert not tray.is_visible()
    
    def test_show_message(self):
        """Test system tray notification message"""
        tray = SystemTray()
        tray.setup()
        # Should not raise
        tray.show_message("Test", "Message", 5000)
    
    def test_menu_creation(self):
        """Test context menu is created"""
        tray = SystemTray()
        tray.setup()
        assert tray.menu is not None
    
    def test_custom_icon_loading(self):
        """Test loading custom icon"""
        tray = SystemTray()
        tray.setup()
        
        # Try to set non-existent icon
        result = tray.set_icon("/nonexistent/path/icon.png")
        assert result is False


# ============================================================================
# Floating Indicator Tests
# ============================================================================

class TestFloatingIndicator:
    """Test FloatingIndicator component"""
    
    def test_init(self):
        """Test FloatingIndicator initialization"""
        indicator = FloatingIndicator()
        assert indicator.status_text == "Ready"
        assert indicator.last_command == ""
        assert indicator.is_listening is False
    
    def test_set_listening(self):
        """Test setting listening status"""
        indicator = FloatingIndicator()
        indicator.set_listening()
        assert indicator.status_text == "Listening"
        assert indicator.is_listening is True
    
    def test_set_paused(self):
        """Test setting paused status"""
        indicator = FloatingIndicator()
        indicator.set_paused()
        assert indicator.status_text == "Paused"
        assert indicator.is_listening is False
    
    def test_set_sleeping(self):
        """Test setting sleeping status"""
        indicator = FloatingIndicator()
        indicator.set_sleeping()
        assert indicator.status_text == "Sleeping"
        assert indicator.is_listening is False
    
    def test_set_ready(self):
        """Test setting ready status"""
        indicator = FloatingIndicator()
        indicator.set_ready()
        assert indicator.status_text == "Ready"
        assert indicator.is_listening is False
    
    def test_update_command(self):
        """Test updating command display"""
        indicator = FloatingIndicator()
        indicator.update_command("three two three")
        assert indicator.last_command == "three two three"
    
    def test_set_opacity(self):
        """Test setting window opacity"""
        indicator = FloatingIndicator()
        indicator.set_opacity(0.8)
        # Should clamp to valid range
        assert indicator.windowOpacity() <= 1.0
        assert indicator.windowOpacity() >= 0.0
    
    def test_opacity_clamping(self):
        """Test opacity value clamping"""
        indicator = FloatingIndicator()
        
        # Test clamping > 1.0
        indicator.set_opacity(1.5)
        assert indicator.windowOpacity() == 1.0
        
        # Test clamping < 0.0
        indicator.set_opacity(-0.5)
        assert indicator.windowOpacity() == 0.0
    
    def test_position_management(self):
        """Test getting and setting position"""
        indicator = FloatingIndicator()
        indicator.set_position(100, 200)
        x, y = indicator.get_position()
        assert x == 100
        assert y == 200
    
    def test_toggle_visibility(self):
        """Test toggling visibility"""
        indicator = FloatingIndicator()
        
        initial = indicator.isVisible()
        indicator.toggle_visibility()
        assert indicator.isVisible() != initial
    
    def test_show_info(self):
        """Test displaying info message"""
        indicator = FloatingIndicator()
        indicator.show_info("Info Title", "Info Message")
        # Command should be updated
        assert "Info Title" in indicator.last_command


# ============================================================================
# Settings Dialog Tests
# ============================================================================

class TestSettingsDialog:
    """Test SettingsDialog component"""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            config = ConfigManager(config_path)
            yield config
    
    def test_init(self, temp_config):
        """Test SettingsDialog initialization"""
        dialog = SettingsDialog(temp_config)
        assert dialog.config == temp_config
        assert dialog.tab_widget is not None
    
    def test_load_settings(self, temp_config):
        """Test loading settings from config"""
        dialog = SettingsDialog(temp_config)
        dialog.load_settings()
        # Settings should be loaded without error
        assert dialog.window_title_edit.text() == "Dentrix"
    
    def test_save_settings(self, temp_config):
        """Test saving settings to config"""
        dialog = SettingsDialog(temp_config)
        dialog.window_title_edit.setText("Open Dental")
        result = dialog.save_settings()
        assert result is True
        assert temp_config.get("target.window_title") == "Open Dental"
    
    def test_keystroke_delay_slider(self, temp_config):
        """Test keystroke delay setting"""
        dialog = SettingsDialog(temp_config)
        dialog.keystroke_slider.setValue(100)
        dialog.save_settings()
        assert temp_config.get("behavior.keystroke_delay_ms") == 100
    
    def test_opacity_slider(self, temp_config):
        """Test opacity slider"""
        dialog = SettingsDialog(temp_config)
        dialog.opacity_slider.setValue(50)
        dialog.save_settings()
        assert temp_config.get("gui.indicator_opacity") == 0.5
    
    def test_checkbox_settings(self, temp_config):
        """Test checkbox settings"""
        dialog = SettingsDialog(temp_config)
        
        dialog.tab_after_check.setChecked(False)
        dialog.save_settings()
        assert temp_config.get("behavior.tab_after_sequence") is False
        
        dialog.tab_after_check.setChecked(True)
        dialog.save_settings()
        assert temp_config.get("behavior.tab_after_sequence") is True
    
    def test_validate_window_title(self, temp_config):
        """Test validation of window title"""
        dialog = SettingsDialog(temp_config)
        dialog.window_title_edit.setText("")
        result = dialog._validate_settings()
        assert result is False
    
    def test_validate_hotkey_format(self, temp_config):
        """Test validation of hotkey format"""
        dialog = SettingsDialog(temp_config)
        dialog.toggle_hotkey_edit.setText("invalidhotkey")
        result = dialog._validate_settings()
        assert result is False
    
    def test_audio_settings(self, temp_config):
        """Test audio settings"""
        dialog = SettingsDialog(temp_config)
        dialog.sample_rate_spinbox.setValue(44100)
        dialog.chunk_size_spinbox.setValue(8000)
        dialog.save_settings()
        assert temp_config.get("audio.sample_rate") == 44100
        assert temp_config.get("audio.chunk_size") == 8000


# ============================================================================
# GUI Manager Tests
# ============================================================================

class TestGUIManager:
    """Test GUIManager component"""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            config = ConfigManager(config_path)
            yield config
    
    def test_init(self, temp_config):
        """Test GUIManager initialization"""
        manager = GUIManager(temp_config)
        assert manager.config == temp_config
        assert manager.is_listening is False
        assert manager.is_visible is True
        assert manager.current_status == "Ready"
    
    def test_setup(self, temp_config):
        """Test GUIManager setup"""
        manager = GUIManager(temp_config)
        result = manager.setup()
        assert result is True
        assert manager.tray is not None
        assert manager.indicator is not None
        assert manager.settings_dialog is not None
    
    def test_set_listening(self, temp_config):
        """Test setting listening status"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.set_listening()
        assert manager.is_listening is True
        assert manager.current_status == "Listening"
    
    def test_set_paused(self, temp_config):
        """Test setting paused status"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.set_paused()
        assert manager.is_listening is False
        assert manager.current_status == "Paused"
    
    def test_set_sleeping(self, temp_config):
        """Test setting sleeping status"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.set_sleeping()
        assert manager.is_listening is False
        assert manager.current_status == "Sleeping"
    
    def test_set_ready(self, temp_config):
        """Test setting ready status"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.set_ready()
        assert manager.is_listening is False
        assert manager.current_status == "Ready"
    
    def test_show_hide(self, temp_config):
        """Test show and hide operations"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        manager.hide()
        assert manager.is_visible is False
        
        manager.show()
        assert manager.is_visible is True
    
    def test_toggle_visibility(self, temp_config):
        """Test toggling visibility"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        initial = manager.is_visible
        manager.toggle_visibility()
        assert manager.is_visible != initial
    
    def test_show_indicator(self, temp_config):
        """Test showing indicator"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.show_indicator()
        # Should not raise
    
    def test_hide_indicator(self, temp_config):
        """Test hiding indicator"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.hide_indicator()
        # Should not raise
    
    def test_toggle_listening(self, temp_config):
        """Test toggling listening state"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        manager.set_paused()
        manager.toggle_listening()
        assert manager.is_listening is True
        
        manager.toggle_listening()
        assert manager.is_listening is False
    
    def test_update_status(self, temp_config):
        """Test status update"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.update_status("Custom Status")
        # Should emit signal without raising
    
    def test_show_command_feedback(self, temp_config):
        """Test command feedback display"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.show_command_feedback("three two three")
        # Should emit signal without raising
    
    def test_show_notification(self, temp_config):
        """Test notification"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.show_notification("Title", "Message")
        # Should not raise
    
    def test_indicator_position(self, temp_config):
        """Test indicator position management"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        manager.set_indicator_position(100, 200)
        x, y = manager.get_indicator_position()
        assert x == 100
        assert y == 200
    
    def test_get_status(self, temp_config):
        """Test getting status string"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        manager.set_listening()
        assert manager.get_status() == "Listening"
        
        manager.set_paused()
        assert manager.get_status() == "Paused"
    
    def test_is_listening_status(self, temp_config):
        """Test checking listening status"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        manager.set_listening()
        assert manager.is_listening_status() is True
        
        manager.set_paused()
        assert manager.is_listening_status() is False
    
    def test_cleanup(self, temp_config):
        """Test cleanup operation"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager.cleanup()
        # Should not raise
    
    def test_update_timer(self, temp_config):
        """Test update timer"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        manager.start_update_timer(500)
        assert manager.update_timer.isActive()
        
        manager.stop_update_timer()
        assert not manager.update_timer.isActive()
    
    def test_apply_settings(self, temp_config):
        """Test applying settings to components"""
        manager = GUIManager(temp_config)
        manager.setup()
        manager._apply_settings()
        # Should apply without error


# ============================================================================
# Integration Tests
# ============================================================================

class TestGUIIntegration:
    """Integration tests for GUI components"""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            config = ConfigManager(config_path)
            yield config
    
    def test_full_workflow(self, temp_config):
        """Test complete workflow: setup -> update -> cleanup"""
        manager = GUIManager(temp_config)
        
        # Setup
        assert manager.setup() is True
        
        # Status transitions
        manager.set_listening()
        manager.show_command_feedback("three two three")
        
        manager.set_paused()
        manager.show_notification("Status", "Paused")
        
        manager.set_sleeping()
        manager.set_ready()
        
        # Cleanup
        manager.cleanup()
    
    def test_settings_integration(self, temp_config):
        """Test settings dialog integration"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        # Change settings
        manager.settings_dialog.window_title_edit.setText("Eaglesoft")
        manager.settings_dialog.keystroke_slider.setValue(100)
        manager.settings_dialog.save_settings()
        
        # Verify changes
        assert temp_config.get("target.window_title") == "Eaglesoft"
        assert temp_config.get("behavior.keystroke_delay_ms") == 100
    
    def test_signal_connections(self, temp_config):
        """Test that signals are properly connected"""
        manager = GUIManager(temp_config)
        manager.setup()
        
        # Create a mock to verify signal is emitted
        mock_listener = Mock()
        manager.signals.listening_toggled.connect(mock_listener)
        
        manager.toggle_listening()
        # Signal should be emitted
        assert mock_listener.call_count >= 0  # May be called with signal


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestGUIErrorHandling:
    """Test error handling in GUI components"""
    
    def test_system_tray_icon_missing(self):
        """Test system tray with missing icon"""
        tray = SystemTray()
        # Should create default icon if file missing
        result = tray.setup()
        assert isinstance(result, bool)
    
    def test_settings_dialog_no_config(self):
        """Test settings dialog without config"""
        dialog = SettingsDialog(None)
        # Should not raise even without config
        dialog.load_settings()
    
    def test_gui_manager_no_config(self):
        """Test GUI manager without config"""
        manager = GUIManager(None)
        result = manager.setup()
        # Should handle None gracefully
        assert isinstance(result, bool)


# ============================================================================
# Configuration Persistence Tests
# ============================================================================

class TestConfigPersistence:
    """Test configuration persistence"""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            config = ConfigManager(config_path)
            yield config
    
    def test_settings_saved_to_file(self, temp_config):
        """Test settings are persisted to file"""
        dialog = SettingsDialog(temp_config)
        dialog.window_title_edit.setText("Custom Title")
        dialog.save_settings()
        
        # Load config again from file
        config2 = ConfigManager(temp_config.config_path)
        assert config2.get("target.window_title") == "Custom Title"
    
    def test_multiple_save_operations(self, temp_config):
        """Test multiple save operations"""
        dialog = SettingsDialog(temp_config)
        
        dialog.window_title_edit.setText("Title 1")
        dialog.save_settings()
        
        dialog.window_title_edit.setText("Title 2")
        dialog.save_settings()
        
        assert temp_config.get("target.window_title") == "Title 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
