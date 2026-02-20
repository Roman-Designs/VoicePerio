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
import os
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
from .speech_engine import SpeechEngine, RecognitionResult
from .command_parser import CommandParser, Command
from .number_grouper import NumberGrouper, ParsedCommand, NumberGroup
from .number_sequencer import NumberSequencer
from .action_executor import ActionExecutor
from .audio_feedback import AudioFeedbackManager
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
        self.number_grouper: Optional[NumberGrouper] = None
        self.number_sequencer: Optional[NumberSequencer] = None
        self.action_executor: Optional[ActionExecutor] = None
        self.audio_feedback: Optional[AudioFeedbackManager] = None
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

            # Step 6: Initialize audio feedback
            if not self._setup_audio_feedback():
                return False
            
            # Step 7: Initialize command parser
            if not self._setup_command_parser():
                return False
            
            # Step 8: Register global hotkeys
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
        possible_paths = []

        # 1. Config override (highest priority)
        if self.config:
            custom_path = self.config.get("speech.model_path")
            if custom_path:
                possible_paths.append(Path(custom_path))

        # 2. Explicit env var set by portable launcher
        env_path = os.environ.get('VOSK_MODEL_PATH')
        if env_path:
            possible_paths.append(Path(env_path))

        # 3. Relative to this file: app/src/voiceperio/main.py
        #    Go up 4 levels to reach the USB/portable root, then into models/
        try:
            usb_root = Path(__file__).resolve().parent.parent.parent.parent
            possible_paths.append(usb_root / "models" / "vosk-model-small-en-us")
        except Exception:
            pass

        # 4. Relative to CWD (works when launched from the portable root via .bat)
        possible_paths.append(Path("models") / "vosk-model-small-en-us")

        # 5. Standard installed location
        possible_paths.append(Path("C:/Program Files/VoicePerio/models/vosk-model-small-en-us"))

        for path in possible_paths:
            if path.exists() and (path / "am" / "final.mdl").exists():
                logger.info(f"Found Vosk model at {path}")
                return path

        logger.warning(f"Vosk model not found. Searched: {[str(p) for p in possible_paths]}")
        return None
    
    def _setup_speech_grammar(self) -> None:
        """Set up speech recognition grammar with perio vocabulary"""
        try:
            # Build vocabulary from commands
            vocabulary = [
                # Numbers — single digits
                "zero", "one", "two", "three", "four", "five", "six", "seven", 
                "eight", "nine", "oh",
                # Numbers — double digits (10–19, Dentrix numpad minus protocol)
                "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                "sixteen", "seventeen", "eighteen", "nineteen",
                # Indicators
                "bleeding", "bleed", "bop", "suppuration", "pus", "plaque", "calculus", 
                "tartar", "furcation", "furca", "mobility", "mobile", "recession",
                # Navigation
                "next", "previous", "back", "skip", "missing", "upper", "lower", 
                "left", "right", "facial", "buccal", "lingual", "palatal", "quadrant",
                # Actions
                "enter", "okay", "cancel", "escape", "save", "undo", "correction", "scratch", "clear",
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
            
            # Setup number grouper (for timing-based number grouping)
            pause_threshold = self.config.get("behavior.pause_threshold_ms", 300) if self.config else 300
            self.number_grouper = NumberGrouper(
                pause_threshold_ms=pause_threshold
            )
            
            # Setup number sequencer (for field entry).
            # Note: advance_key is only used by NumberSequencer.skip_fields() to follow
            # Dentrix's navigation script path (Enter).  go_next() always sends Page Down
            # (the Dentrix keyboard shortcut for the explicit Next button) regardless of
            # this setting, so changing advance_key does NOT affect the "next" voice command.
            advance_key = self.config.get("behavior.advance_key", "enter") if self.config else "enter"
            self.number_sequencer = NumberSequencer(
                inter_entry_delay_ms=keystroke_delay,
                advance_key=advance_key
            )
            self.number_sequencer.set_action_executor(self.action_executor)
            
            logger.info("Action executor and number processing initialized")
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

    def _setup_audio_feedback(self) -> bool:
        """Set up optional audio feedback after successful Dentrix entry."""
        try:
            mode = self.config.get("behavior.audio_feedback_mode", "off") if self.config else "off"
            readback_rate = self.config.get("behavior.readback_rate", 3) if self.config else 3
            readback_max_chars = self.config.get("behavior.readback_max_chars", 32) if self.config else 32

            self.audio_feedback = AudioFeedbackManager(
                mode=mode,
                readback_rate=readback_rate,
                readback_max_chars=readback_max_chars,
            )

            logger.info(
                "Audio feedback initialized: "
                f"mode={mode}, readback_rate={readback_rate}, readback_max_chars={readback_max_chars}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to setup audio feedback: {e}")
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
            # On locked-down corporate Windows, low-level keyboard hooks may be denied.
            # Hotkeys are a convenience feature — the app works fine without them.
            logger.warning(
                f"Could not register global hotkeys (may require admin rights on this machine): {e}. "
                "Use the system tray menu to control VoicePerio instead."
            )
            return True  # Non-fatal
    
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

            # Stop feedback worker
            if self.audio_feedback:
                self.audio_feedback.shutdown()
            
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
                    
                    if result and result.is_final:
                        # Emit partial result for GUI feedback
                        partial = self.speech_engine.get_partial()
                        if partial:
                            self.signals.partial_result.emit(partial)
                        
                        # Process recognition result through number grouper
                        self._process_recognition_result(result)
                
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                self._handle_error(f"Audio processing error: {e}")
                time.sleep(0.5)  # Back off on error
        
        logger.info("Audio processing thread stopped")
    
    def _process_recognition_result(self, result: RecognitionResult) -> None:
        """
        Process recognition result using the new timing-based number grouper.
        
        This replaces the old _process_recognized_text method with improved
        handling for timing-based number grouping.
        """
        try:
            if not result or not result.text:
                return
            
            # Use number grouper to parse the recognition result
            feedback_text = None
            if self.number_grouper:
                parsed = self.number_grouper.parse_recognition(result)
                success = self._execute_parsed_command(parsed)
                if success:
                    feedback_text = self._feedback_text_for_parsed_command(parsed)
            else:
                # Fallback to old command parser
                if self.command_parser:
                    command = self.command_parser.parse(result.text)
                    if command:
                        success = self._execute_command(command)
                        if success:
                            feedback_text = self._feedback_text_for_legacy_command(command)
                    else:
                        success = False
                else:
                    success = False

            if success and feedback_text and self.audio_feedback:
                self.audio_feedback.play_success(feedback_text)
            
            # Show feedback
            if self.gui_manager:
                self.gui_manager.show_command_feedback(result.text)
            
            # Emit signal
            self.signals.command_executed.emit(result.text, success)
            
            logger.info(f"Processed recognition: '{result.text}' -> success={success}")
        
        except Exception as e:
            logger.error(f"Error processing recognition result: {e}")
            self._handle_error(f"Command processing error: {e}")
    
    def _process_recognized_text(self, text: str) -> None:
        """
        Legacy method for processing recognized text (backward compatibility).
        
        DEPRECATED: Use _process_recognition_result instead.
        """
        # Create a simple RecognitionResult without timing data
        result = RecognitionResult(text=text, words=[], is_final=True)
        self._process_recognition_result(result)
    
    def _execute_parsed_command(self, parsed: ParsedCommand) -> bool:
        """
        Execute a parsed command from the NumberGrouper.
        
        This is the new command execution path that handles timing-based
        number grouping.
        
        Args:
            parsed: ParsedCommand from NumberGrouper
            
        Returns:
            True if execution successful
        """
        try:
            cmd_type = parsed.command_type
            
            if cmd_type == "numbers":
                # Enter number groups (timing-based)
                if self.number_sequencer and parsed.number_groups:
                    return self.number_sequencer.enter_number_groups(parsed.number_groups)
                return False
            
            elif cmd_type == "next":
                # Advance to next field
                if self.number_sequencer:
                    return self.number_sequencer.go_next()
                return False
            
            elif cmd_type == "previous":
                # Go to previous field
                if self.number_sequencer:
                    return self.number_sequencer.go_previous()
                return False
            
            elif cmd_type == "skip":
                # Skip with zeros (000)
                if self.number_sequencer:
                    return self.number_sequencer.skip_with_zeros()
                return False
            
            elif cmd_type == "skip_count":
                # Skip N fields
                count = parsed.params.get("count", 1)
                if self.number_sequencer:
                    return self.number_sequencer.skip_fields(count)
                return False
            
            elif cmd_type == "home":
                # Go to first position
                if self.number_sequencer:
                    return self.number_sequencer.go_home()
                return False
            
            elif cmd_type == "save":
                # Save the exam
                if self.number_sequencer:
                    return self.number_sequencer.save()
                return False
            
            elif cmd_type == "clear":
                # Clear current selection (Delete key in Dentrix)
                if self.action_executor:
                    return self.action_executor.send_keystroke("delete")
                return False
            
            elif cmd_type == "indicator":
                # Handle perio indicators (bleeding, suppuration, etc.)
                indicator = parsed.params.get("indicator", "")
                return self._execute_indicator_from_parsed(indicator)
            
            elif cmd_type == "empty" or cmd_type == "unrecognized":
                logger.debug(f"Unrecognized or empty command: '{parsed.raw_text}'")
                return False
            
            else:
                # Fallback to old command parser for unknown types
                logger.debug(f"Unknown parsed command type: {cmd_type}, trying legacy parser")
                if self.command_parser:
                    command = self.command_parser.parse(parsed.raw_text)
                    if command:
                        return self._execute_command(command)
                return False
        
        except Exception as e:
            logger.error(f"Error executing parsed command: {e}")
            return False
    
    def _execute_indicator_from_parsed(self, indicator: str) -> bool:
        """Execute indicator from parsed command."""
        if not self.action_executor:
            return False
        
        # Map indicators to Dentrix keys
        indicator_keys = {
            "bleeding": "b",
            "suppuration": "s",
            "plaque": "a",
            "calculus": "c",
            "furcation": "g",
            "mobility": "m",
            "bone_loss": "l",
            "recession": "r",
        }
        
        key = indicator_keys.get(indicator)
        if key:
            return self.action_executor.send_keystroke(key)
        return False
    
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

    def _feedback_text_for_parsed_command(self, parsed: ParsedCommand) -> Optional[str]:
        """Create concise readback text for timing-based parser commands."""
        if not parsed:
            return None

        if parsed.command_type == "numbers":
            groups = [self._digits_for_readback(group.digits) for group in (parsed.number_groups or [])]
            groups = [g for g in groups if g]
            return ", ".join(groups) if groups else None

        if parsed.command_type == "skip":
            return "0 0 0"

        if parsed.command_type == "indicator":
            indicator = parsed.params.get("indicator", "") if parsed.params else ""
            return indicator.replace("_", " ") if indicator else None

        return None

    def _feedback_text_for_legacy_command(self, command: Command) -> Optional[str]:
        """Create concise readback text for legacy parser commands."""
        if not command:
            return None

        if command.action in ("number_sequence", "single_number"):
            numbers = command.params.get("numbers", [])
            if not numbers:
                return None
            return " ".join(str(num) for num in numbers)

        if command.action == "indicator":
            indicator = command.params.get("indicator", "")
            return indicator.replace("_", " ") if indicator else None

        return None

    @staticmethod
    def _digits_for_readback(digits: str) -> str:
        """Format compact digits for quick speech readback."""
        return " ".join(ch for ch in (digits or "") if ch.isdigit())
    
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
        
        # Update number sequencer delay
        if "keystroke_delay_ms" in settings and self.number_sequencer:
            self.number_sequencer.inter_entry_delay_ms = settings["keystroke_delay_ms"]
        
        # Update number grouper pause threshold
        if "pause_threshold_ms" in settings and self.number_grouper:
            self.number_grouper.set_pause_threshold(settings["pause_threshold_ms"])
        
        # Update advance key
        if "advance_key" in settings and self.number_sequencer:
            self.number_sequencer.advance_key = settings["advance_key"]
        
        # Update target window
        if "window_title" in settings and self.action_executor:
            self.action_executor.find_target_window(settings["window_title"])

        if self.audio_feedback:
            self.audio_feedback.update_settings(
                mode=settings.get("audio_feedback_mode"),
                readback_rate=settings.get("readback_rate"),
                readback_max_chars=settings.get("readback_max_chars"),
            )
    
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
    # Determine log file location
    import os
    from pathlib import Path
    
    # Use %APPDATA% for log file (not console output when running as GUI)
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    voiceperio_dir = Path(appdata) / 'VoicePerio'
    voiceperio_dir.mkdir(parents=True, exist_ok=True)
    log_file = voiceperio_dir / 'voiceperio.log'
    
    # Detect whether we have a real console attached (portable .bat launch = yes, windowed .exe = no)
    import sys as _sys
    _has_console = False
    try:
        if _sys.stdout is not None:
            _sys.stdout.fileno()
            _has_console = True
    except Exception:
        pass

    # Setup logging — enable console output when running from .bat so errors are visible
    setup_logging(
        log_level=logging.INFO,
        log_file=str(log_file),
        console_output=_has_console
    )

    if _has_console:
        print(f"VoicePerio starting... Log file: {log_file}")
    
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
