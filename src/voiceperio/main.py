"""
Main Application Controller - VoicePerio
Wires all components together and manages the main event loop.

This is the core integration module that orchestrates:
- Audio capture from microphone
- Speech recognition via Vosk
- Command parsing and interpretation
- Keystroke injection to target window
- GUI feedback via system tray and floating indicator
- Global hotkey support for app control
"""

import sys
import logging
import threading
import time
import signal
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from enum import Enum
from concurrent import futures

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot

from .config_manager import ConfigManager
from .audio_capture import AudioCapture
from .speech_engine import SpeechEngine
from .command_parser import CommandParser, Command
from .number_sequencer import NumberSequencer
from .action_executor import ActionExecutor
from .gui.gui_manager import GUIManager
from .utils.logger import setup_logging, get_logger

logger = logging.getLogger(__name__)


class AppState(Enum):
    """Application state enumeration"""
    INITIALIZING = "initializing"
    READY = "ready"
    LISTENING = "listening"
    PAUSED = "paused"
    SLEEPING = "sleeping"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"


class VoicePerioSignals(QObject):
    """Signals for VoicePerioApp"""
    
    state_changed = pyqtSignal(str)  # New state
    command_executed = pyqtSignal(str, bool)  # Command text, success
    error_occurred = pyqtSignal(str)  # Error message
    partial_result = pyqtSignal(str)  # Partial speech result


class VoicePerioApp:
    """
    Main controller - wires everything together.
    
    This is the core integration class that coordinates all VoicePerio components:
    - ConfigManager: Configuration persistence
    - AudioCapture: Microphone input streaming
    - SpeechEngine: Vosk-based speech recognition
    - CommandParser: Speech-to-command interpretation
    - NumberSequencer: Pocket depth sequence handling
    - ActionExecutor: Keystroke injection to target window
    - GUIManager: System tray and floating indicator
    
    Lifecycle:
    1. Initialize all components
    2. Register global hotkeys
    3. Start audio processing thread
    4. Enter main Qt event loop
    5. Handle graceful shutdown
    
    Attributes:
        config: Configuration manager instance
        audio_capture: Audio capture instance
        speech_engine: Speech recognition instance
        command_parser: Command parser instance
        action_executor: Keystroke executor instance
        gui_manager: GUI manager instance
        state: Current application state
        is_listening: Whether audio processing is active
    """
    
    # Global hotkey mappings
    DEFAULT_HOTKEYS = {
        "toggle_listening": "ctrl+shift+v",
        "pause": "ctrl+shift+p",
        "sleep": "ctrl+shift+s",
        "wake": "ctrl+shift+w",
        "exit": "ctrl+shift+x"
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the VoicePerio application.
        
        Args:
            config_path: Optional path to config file
        """
        # Core components (initialized in setup)
        self.config: Optional[ConfigManager] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.speech_engine: Optional[SpeechEngine] = None
        self.command_parser: Optional[CommandParser] = None
        self.number_sequencer: Optional[NumberSequencer] = None
        self.action_executor: Optional[ActionExecutor] = None
        self.gui_manager: Optional[GUIManager] = None
        
        # Application state
        self.state = AppState.INITIALIZING
        self.is_listening = False
        self.is_paused = False
        self.is_sleeping = False
        self._shutdown_requested = False
        
        # Threading
        self._audio_thread: Optional[threading.Thread] = None
        self._audio_thread_running = False
        self._lock = threading.RLock()
        
        # Qt application
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Signals
        self.signals = VoicePerioSignals()
        
        # Recovery tracking
        self._error_count = 0
        self._max_errors = 5
        self._last_error_time = 0
        
        # Commands file path
        self.commands_file = Path(__file__).parent / "commands" / "default_commands.json"
        
        logger.info("VoicePerioApp instance created")
    
    def setup(self) -> bool:
        """
        Set up all components in proper order.
        
        Startup sequence:
        1. Load configuration
        2. Initialize GUI
        3. Load Vosk speech model
        4. Initialize audio capture
        5. Initialize action executor
        6. Initialize command parser
        7. Register global hotkeys
        8. Show startup notification
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            logger.info("Starting VoicePerio setup...")
            self.state = AppState.INITIALIZING
            
            # Step 1: Load configuration
            if not self._setup_config():
                return False
            
            # Step 2: Initialize GUI
            if not self._setup_gui():
                return False
            
            # Step 3: Load speech model
            if not self._setup_speech_engine():
                return False
            
            # Step 4: Initialize audio capture
            if not self._setup_audio_capture():
                return False
            
            # Step 5: Initialize action executor
            if not self._setup_action_executor():
                return False
            
            # Step 6: Initialize command parser
            if not self._setup_command_parser():
                return False
            
            # Step 7: Register global hotkeys
            if not self._setup_hotkeys():
                return False
            
            # Show startup notification
            self._show_startup_notification()
            
            # Update state
            self._set_state(AppState.READY)
            
            logger.info("VoicePerio setup completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Setup failed: {e}", exc_info=True)
            self._handle_error(f"Setup failed: {e}")
            return False
    
    def _setup_config(self) -> bool:
        """Set up configuration manager"""
        try:
            self.config = ConfigManager()
            logger.info(f"Configuration loaded from {self.config.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _setup_gui(self) -> bool:
        """Set up GUI manager"""
        try:
            self.gui_manager = GUIManager(self.config, self.app)
            
            if not self.gui_manager.setup():
                logger.error("Failed to setup GUI manager")
                return False
            
            # Connect GUI signals
            self.gui_manager.signals.exit_requested.connect(self.shutdown)
            self.gui_manager.signals.settings_changed.connect(self._on_settings_changed)
            self.gui_manager.signals.listening_toggled.connect(self._on_listening_toggled)
            
            # Show GUI
            self.gui_manager.show()
            self.gui_manager.set_ready()
            
            logger.info("GUI manager initialized")
            return True
        
        except Exception as e:
            logger.error(f"Failed to setup GUI: {e}")
            return False
    
    def _setup_speech_engine(self) -> bool:
        """Set up speech recognition engine"""
        try:
            self.speech_engine = SpeechEngine()
            
            # Find Vosk model
            model_path = self._find_vosk_model()
            if not model_path:
                logger.error("Vosk model not found")
                self._show_error_notification("Speech Model Missing", 
                    "Please download the Vosk model and place it in the models folder.")
                return False
            
            if not self.speech_engine.load_model(str(model_path)):
                logger.error("Failed to load speech model")
                return False
            
            # Set up perio vocabulary for better recognition
            self._setup_speech_grammar()
            
            logger.info("Speech engine initialized")
            return True
        
        except Exception as e:
            logger.error(f"Failed to setup speech engine: {e}")
            return False
    
    def _find_vosk_model(self) -> Optional[Path]:
        """Find the Vosk model directory"""
        # Check multiple possible locations
        possible_paths = [
            Path("models/vosk-model-small-en-us"),
            Path(__file__).parent.parent.parent / "models" / "vosk-model-small-en-us",
            Path("C:/Program Files/VoicePerio/models/vosk-model-small-en-us"),
        ]
        
        # Also check config for custom path
        if self.config:
            custom_path = self.config.get("speech.model_path")
            if custom_path:
                possible_paths.insert(0, Path(custom_path))
        
        for path in possible_paths:
            if path.exists() and (path / "vosk-model-small-en-us/am/final.mdl").exists():
                logger.info(f"Found Vosk model at {path}")
                return path
            elif path.exists() and (path / "am/final.mdl").exists():
                logger.info(f"Found Vosk model at {path}")
                return path
        
        logger.warning("Vosk model not found in any expected location")
        return None
    
    def _setup_speech_grammar(self) -> None:
        """Set up speech recognition grammar with perio vocabulary"""
        try:
            # Build vocabulary from commands
            vocabulary = [
                # Numbers
                "zero", "one", "two", "three", "four", "five", "six", "seven", 
                "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "oh",
                # Indicators
                "bleeding", "bleed", "bop", "suppuration", "pus", "plaque", "calculus", 
                "tartar", "furcation", "furca", "mobility", "mobile", "recession",
                # Navigation
                "next", "previous", "back", "skip", "missing", "upper", "lower", 
                "left", "right", "facial", "buccal", "lingual", "palatal", "quadrant",
                # Actions
                "enter", "okay", "cancel", "escape", "save", "undo", "correction", "scratch",
                # App control
                "wake", "sleep", "pause", "stop", "exit", "voice", "perio",
            ]
            
            self.speech_engine.set_grammar(vocabulary)
            logger.info(f"Speech grammar set with {len(vocabulary)} words")
        
        except Exception as e:
            logger.warning(f"Failed to set speech grammar: {e}")
    
    def _setup_audio_capture(self) -> bool:
        """Set up audio capture"""
        try:
            sample_rate = self.config.get("audio.sample_rate", 16000) if self.config else 16000
            chunk_size = self.config.get("audio.chunk_size", 4000) if self.config else 4000
            channels = self.config.get("audio.channels", 1) if self.config else 1
            
            self.audio_capture = AudioCapture(
                sample_rate=sample_rate,
                chunk_size=chunk_size,
                channels=channels
            )
            
            # Set device if configured
            device_id = self.config.get("audio.device_id") if self.config else None
            if device_id is not None:
                self.audio_capture.set_device(device_id)
            
            logger.info(f"Audio capture initialized: {sample_rate}Hz, {channels} channel(s)")
            return True
        
        except Exception as e:
            logger.error(f"Failed to setup audio capture: {e}")
            return False
    
    def _setup_action_executor(self) -> bool:
        """Set up action executor for keystroke injection"""
        try:
            target_window = self.config.get("target.window_title", "Dentrix") if self.config else "Dentrix"
            keystroke_delay = self.config.get("behavior.keystroke_delay_ms", 50) if self.config else 50
            
            self.action_executor = ActionExecutor(
                target_window_title=target_window,
                keystroke_delay_ms=keystroke_delay
            )
            
            # Try to find target window
            self.action_executor.find_target_window(target_window)
            
            # Setup number sequencer
            tab_after = self.config.get("behavior.tab_after_sequence", True) if self.config else True
            
            self.number_sequencer = NumberSequencer(
                inter_number_delay_ms=keystroke_delay,
                tab_after_sequence=tab_after
            )
            self.number_sequencer.set_action_executor(self.action_executor)
            
            logger.info("Action executor initialized")
            return True
        
        except Exception as e:
            logger.error(f"Failed to setup action executor: {e}")
            return False
    
    def _setup_command_parser(self) -> bool:
        """Set up command parser"""
        try:
            self.command_parser = CommandParser(str(self.commands_file))
            
            if not self.command_parser.commands_db:
                logger.warning("Command database not loaded, using defaults")
            
            logger.info("Command parser initialized")
            return True
        
        except Exception as e:
            logger.error(f"Failed to setup command parser: {e}")
            return False
    
    def _setup_hotkeys(self) -> bool:
        """Set up global hotkeys using keyboard library"""
        try:
            import keyboard
            
            # Get hotkey configurations
            hotkeys = self.DEFAULT_HOTKEYS.copy()
            
            if self.config:
                custom_toggle = self.config.get("hotkey.toggle_listening")
                if custom_toggle:
                    hotkeys["toggle_listening"] = custom_toggle
            
            # Unregister any existing hotkeys first
            try:
                keyboard.unhook_all()
            except:
                pass
            
            # Register hotkeys
            keyboard.add_hotkey(hotkeys["toggle_listening"], self._on_hotkey_toggle)
            keyboard.add_hotkey(hotkeys["pause"], self._on_hotkey_pause)
            keyboard.add_hotkey(hotkeys["sleep"], self._on_hotkey_sleep)
            keyboard.add_hotkey(hotkeys["wake"], self._on_hotkey_wake)
            keyboard.add_hotkey(hotkeys["exit"], self._on_hotkey_exit)
            
            logger.info(f"Global hotkeys registered: {hotkeys}")
            return True
        
        except ImportError:
            logger.warning("keyboard module not available, hotkeys disabled")
            return True
        except Exception as e:
            logger.error(f"Failed to setup hotkeys: {e}")
            return False
    
    def start(self) -> int:
        """
        Start the application.
        
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Setup components
            if not self.setup():
                logger.error("Setup failed, cannot start")
                return 1
            
            # Start listening
            self.start_listening()
            
            # Enter main event loop
            logger.info("Entering main event loop")
            return self.app.exec()
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self.shutdown()
            return 0
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            return 1
    
    def start_listening(self) -> bool:
        """
        Start the audio processing loop.
        
        Returns:
            True if started successfully
        """
        with self._lock:
            if self.is_listening:
                logger.warning("Already listening")
                return True
            
            # Start audio capture
            if not self.audio_capture.start():
                logger.error("Failed to start audio capture")
                return False
            
            # Reset speech engine
            if self.speech_engine:
                self.speech_engine.reset()
            
            # Start audio thread
            self._audio_thread_running = True
            self._audio_thread = threading.Thread(
                target=self._audio_processing_loop,
                daemon=True,
                name="VoicePerio-Audio"
            )
            self._audio_thread.start()
            
            # Update state
            self.is_listening = True
            self.is_paused = False
            self.is_sleeping = False
            self._set_state(AppState.LISTENING)
            
            # Update GUI
            if self.gui_manager:
                self.gui_manager.set_listening()
            
            logger.info("Listening started")
            return True
    
    def stop_listening(self) -> bool:
        """
        Stop the audio processing loop.
        
        Returns:
            True if stopped successfully
        """
        with self._lock:
            if not self.is_listening:
                logger.warning("Not listening")
                return True
            
            # Stop audio thread
            self._audio_thread_running = False
            
            # Stop audio capture
            if self.audio_capture:
                self.audio_capture.stop()
            
            # Update state
            self.is_listening = False
            self._set_state(AppState.PAUSED)
            
            # Update GUI
            if self.gui_manager:
                self.gui_manager.set_paused()
            
            logger.info("Listening stopped")
            return True
    
    def pause(self) -> bool:
        """
        Pause listening (keep thread running but skip processing).
        
        Returns:
            True if paused successfully
        """
        with self._lock:
            self.is_paused = True
            self._set_state(AppState.PAUSED)
            
            if self.gui_manager:
                self.gui_manager.set_paused()
            
            logger.info("Listening paused")
            return True
    
    def resume(self) -> bool:
        """
        Resume listening from paused state.
        
        Returns:
            True if resumed successfully
        """
        with self._lock:
            self.is_paused = False
            
            if self.is_listening:
                self._set_state(AppState.LISTENING)
                if self.gui_manager:
                    self.gui_manager.set_listening()
            
            logger.info("Listening resumed")
            return True
    
    def sleep(self) -> bool:
        """
        Put application in sleep mode (no audio processing).
        
        Returns:
            True if sleep successful
        """
        with self._lock:
            self.is_sleeping = True
            self._set_state(AppState.SLEEPING)
            
            if self.gui_manager:
                self.gui_manager.set_sleeping()
            
            logger.info("Application sleeping")
            return True
    
    def wake(self) -> bool:
        """
        Wake application from sleep mode.
        
        Returns:
            True if wake successful
        """
        with self._lock:
            self.is_sleeping = False
            
            if self.is_listening:
                self._set_state(AppState.LISTENING)
                if self.gui_manager:
                    self.gui_manager.set_listening()
            else:
                self._set_state(AppState.READY)
                if self.gui_manager:
                    self.gui_manager.set_ready()
            
            logger.info("Application woken")
            return True
    
    def shutdown(self) -> None:
        """
        Graceful shutdown of the application.
        
        Shutdown sequence:
        1. Stop audio processing
        2. Unregister hotkeys
        3. Cleanup GUI
        4. Stop audio capture
        5. Unload speech model
        6. Save configuration
        7. Log cleanup
        """
        if self.state == AppState.SHUTTING_DOWN:
            return
        
        logger.info("Initiating shutdown...")
        self._set_state(AppState.SHUTTING_DOWN)
        self._shutdown_requested = True
        
        try:
            # Stop audio thread
            self._audio_thread_running = False
            
            if self._audio_thread and self._audio_thread.is_alive():
                self._audio_thread.join(timeout=2.0)
            
            # Unregister hotkeys
            try:
                import keyboard
                keyboard.unhook_all()
            except:
                pass
            
            # Cleanup GUI
            if self.gui_manager:
                self.gui_manager.cleanup()
            
            # Stop audio capture
            if self.audio_capture:
                self.audio_capture.stop()
            
            # Save configuration
            if self.config:
                self.config.save()
            
            logger.info("Shutdown completed successfully")
        
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
        
        finally:
            # Exit Qt application
            self.app.quit()
    
    def _audio_processing_loop(self) -> None:
        """Main audio processing loop (runs in separate thread)"""
        logger.info("Audio processing thread started")
        
        while self._audio_thread_running:
            try:
                # Skip if paused or sleeping
                if self.is_paused or self.is_sleeping:
                    time.sleep(0.1)
                    continue
                
                # Get audio chunk
                if not self.audio_capture or not self.audio_capture.is_running:
                    time.sleep(0.1)
                    continue
                
                audio_chunk = self.audio_capture.get_audio_chunk()
                if not audio_chunk:
                    time.sleep(0.01)
                    continue
                
                # Process through speech engine
                if self.speech_engine:
                    result = self.speech_engine.process_audio(audio_chunk)
                    
                    if result:
                        # Emit partial result for GUI feedback
                        partial = self.speech_engine.get_partial()
                        if partial:
                            self.signals.partial_result.emit(partial)
                        
                        # Parse and execute command
                        self._process_recognized_text(result)
                
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                self._handle_error(f"Audio processing error: {e}")
                time.sleep(0.5)  # Back off on error
        
        logger.info("Audio processing thread stopped")
    
    def _process_recognized_text(self, text: str) -> None:
        """Process recognized speech text"""
        try:
            if not text or not self.command_parser:
                return
            
            # Parse command
            command = self.command_parser.parse(text)
            if not command:
                return
            
            # Execute command
            success = self._execute_command(command)
            
            # Show feedback
            if self.gui_manager:
                self.gui_manager.show_command_feedback(text)
            
            # Emit signal
            self.signals.command_executed.emit(text, success)
            
            logger.info(f"Executed command: {command}")
        
        except Exception as e:
            logger.error(f"Error processing recognized text: {e}")
            self._handle_error(f"Command processing error: {e}")
    
    def _execute_command(self, command: Command) -> bool:
        """
        Execute a parsed command.
        
        Args:
            command: Parsed Command object
            
        Returns:
            True if execution successful
        """
        try:
            action_type = command.action
            
            # Handle different command types
            if action_type == "number_sequence":
                return self._execute_number_sequence(command)
            elif action_type == "single_number":
                return self._execute_single_number(command)
            elif action_type == "indicator":
                return self._execute_indicator(command)
            elif action_type == "navigation":
                return self._execute_navigation(command)
            elif action_type == "typed_action":
                return self._execute_typed_action(command)
            elif action_type == "app_control":
                return self._execute_app_control(command)
            else:
                logger.warning(f"Unknown command type: {action_type}")
                return False
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return False
    
    def _execute_number_sequence(self, command: Command) -> bool:
        """Execute number sequence command (e.g., 'three two three' -> 3 [Tab] 2 [Tab] 3)"""
        numbers = command.params.get("numbers", [])
        if not numbers:
            return False
        
        return self.number_sequencer.sequence_numbers(numbers)
    
    def _execute_single_number(self, command: Command) -> bool:
        """Execute single number command"""
        numbers = command.params.get("numbers", [])
        if not numbers:
            return False
        
        return self.number_sequencer.sequence_numbers(numbers)
    
    def _execute_indicator(self, command: Command) -> bool:
        """Execute perio indicator command"""
        indicator = command.params.get("indicator", "")
        indicator_action = command.params.get("indicator_action", "keystroke")
        key = command.params.get("key", "")
        class_num = command.params.get("class", None)
        
        if indicator_action == "keystroke" and key:
            if class_num and indicator in ["furcation", "mobility"]:
                # Handle class-based indicators
                return self.action_executor.send_keystroke(key) and \
                       self.action_executor.type_text(str(class_num))
            return self.action_executor.send_keystroke(key)
        
        elif indicator_action == "multi_keystroke" and key:
            return self.action_executor.send_keystroke(key)
        
        return False
    
    def _execute_navigation(self, command: Command) -> bool:
        """Execute navigation command"""
        nav_action = command.params.get("nav_action", "keystroke")
        key = command.params.get("key", "")
        quadrant = command.params.get("quadrant", None)
        side = command.params.get("side", "")
        
        if nav_action == "keystroke" and key:
            return self.action_executor.send_keystroke(key)
        elif nav_action == "jump_quadrant" and quadrant:
            # Quadrant jumps - typically involves multiple key presses
            # This is a placeholder; actual implementation depends on the target software
            logger.info(f"Quadrant jump to {quadrant} (not yet implemented)")
            return True
        elif nav_action == "switch_side" and side:
            # Side switching - typically involves specific key sequences
            logger.info(f"Side switch to {side} (not yet implemented)")
            return True
        
        return False
    
    def _execute_typed_action(self, command: Command) -> bool:
        """Execute typed action command (enter, save, undo, etc.)"""
        action_type = command.params.get("action_type", "keystroke")
        key = command.params.get("key", "")
        
        if action_type == "keystroke" and key:
            return self.action_executor.send_keystroke(key)
        
        return False
    
    def _execute_app_control(self, command: Command) -> bool:
        """Execute app control command (wake, sleep, stop)"""
        cmd = command.params.get("command", "")
        
        if cmd == "wake":
            self.wake()
            return True
        elif cmd == "sleep":
            self.sleep()
            return True
        elif cmd == "stop":
            self.shutdown()
            return True
        
        return False
    
    def _set_state(self, new_state: AppState) -> None:
        """Set application state and emit signal"""
        self.state = new_state
        self.signals.state_changed.emit(new_state.value)
        logger.debug(f"State changed to: {new_state.value}")
    
    def _handle_error(self, error_msg: str) -> None:
        """Handle errors with recovery logic"""
        current_time = time.time()
        
        # Track error frequency
        if current_time - self._last_error_time < 10:
            self._error_count += 1
        else:
            self._error_count = 1
        
        self._last_error_time = current_time
        
        # Emit error signal
        self.signals.error_occurred.emit(error_msg)
        
        # Show GUI notification
        if self.gui_manager:
            self.gui_manager.show_notification("Error", error_msg)
        
        # Check for too many errors
        if self._error_count >= self._max_errors:
            logger.error(f"Too many errors ({self._error_count}), entering error state")
            self._set_state(AppState.ERROR)
            self.stop_listening()
    
    def _show_startup_notification(self) -> None:
        """Show startup notification"""
        if self.gui_manager:
            self.gui_manager.show_notification(
                "VoicePerio Started",
                "VoicePerio is ready. Press Ctrl+Shift+V to toggle listening."
            )
    
    def _show_error_notification(self, title: str, message: str) -> None:
        """Show error notification"""
        if self.gui_manager:
            self.gui_manager.show_notification(title, message)
    
    def _on_settings_changed(self, settings: Dict[str, Any]) -> None:
        """Handle settings changes from GUI"""
        logger.info(f"Settings changed: {settings}")
        
        # Update action executor settings
        if "keystroke_delay_ms" in settings and self.action_executor:
            self.action_executor.set_keystroke_delay(settings["keystroke_delay_ms"])
        
        # Update number sequencer settings
        if "tab_after_sequence" in settings and self.number_sequencer:
            self.number_sequencer.tab_after_sequence = settings["tab_after_sequence"]
        
        # Update target window
        if "window_title" in settings and self.action_executor:
            self.action_executor.find_target_window(settings["window_title"])
    
    def _on_listening_toggled(self, is_listening: bool) -> None:
        """Handle listening toggle from GUI"""
        if is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    # Hotkey handlers (called from keyboard thread)
    def _on_hotkey_toggle(self) -> None:
        """Handle toggle listening hotkey"""
        logger.debug("Hotkey: Toggle listening")
        self.app.postEvent(self.app, _ToggleListeningEvent())
    
    def _on_hotkey_pause(self) -> None:
        """Handle pause hotkey"""
        logger.debug("Hotkey: Pause")
        if self.is_paused:
            self.resume()
        else:
            self.pause()
    
    def _on_hotkey_sleep(self) -> None:
        """Handle sleep hotkey"""
        logger.debug("Hotkey: Sleep")
        self.sleep()
    
    def _on_hotkey_wake(self) -> None:
        """Handle wake hotkey"""
        logger.debug("Hotkey: Wake")
        self.wake()
    
    def _on_hotkey_exit(self) -> None:
        """Handle exit hotkey"""
        logger.debug("Hotkey: Exit")
        self.shutdown()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current application status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "state": self.state.value,
            "is_listening": self.is_listening,
            "is_paused": self.is_paused,
            "is_sleeping": self.is_sleeping,
            "error_count": self._error_count,
            "target_window": self.action_executor.target_window_title if self.action_executor else None,
        }


class _ToggleListeningEvent:
    """Custom event for toggle listening (thread-safe)"""
    pass


def main() -> int:
    """
    Entry point for the VoicePerio application.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Setup logging
    setup_logging(
        log_level=logging.INFO,
        log_file=None,  # Can be set to a file path
        console_output=True
    )
    
    logger.info("=" * 60)
    logger.info("VoicePerio - Voice-Controlled Periodontal Charting Assistant")
    logger.info("=" * 60)
    
    try:
        app = VoicePerioApp()
        return app.start()
    
    except Exception as e:
        logger.error(f"Fatal application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
