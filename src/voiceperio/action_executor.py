"""
Action Executor Module - Keystroke injection and window control
Handles sending keystrokes and key combinations to target windows.

Features:
- Find and focus target windows
- Send individual keystrokes and key combinations
- Type text and number sequences
- Special keystroke mapping (Tab, Enter, Shift, Ctrl, etc.)
- Configurable keystroke delays
- Type validation for perio numbers (0-15)
- Get target window information
- Check if target window is focused
- Comprehensive error handling and logging
"""

from typing import List, Optional, Dict, Tuple, Any
import pyautogui
import win32gui
import win32con
import logging
import time
from .utils import window_utils

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Sends keystrokes to target window.
    
    This class handles all keystroke injection, window finding, and focus
    management for the VoicePerio application. It provides a robust interface
    for typing numbers, sending keyboard commands, and managing window states.
    
    Key Features:
    - Find windows by title pattern
    - Focus and activate target windows
    - Send individual keystrokes and key combinations
    - Type text and number sequences with proper delays
    - Validate perio numbers (0-15 range)
    - Get detailed target window information
    - Check if target window is focused
    - Handle special keys (Tab, Enter, Shift, Ctrl, etc.)
    
    Uses:
    - win32gui for window finding/focusing
    - pyautogui for keystroke injection
    - window_utils for advanced window operations
    """
    
    # Keystroke mapping: common names to pyautogui equivalents
    KEYSTROKE_MAP: Dict[str, str] = {
        # Navigation keys
        'tab': 'tab',
        'enter': 'enter',
        'return': 'enter',
        'space': 'space',
        'escape': 'esc',
        'esc': 'esc',
        'backspace': 'backspace',
        'delete': 'delete',
        'insert': 'insert',
        'home': 'home',
        'end': 'end',
        'pageup': 'pageup',
        'pagedown': 'pagedown',
        
        # Arrow keys
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        
        # Function keys
        'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
        'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
        'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
        
        # Modifier keys (for combinations)
        'ctrl': 'ctrl',
        'shift': 'shift',
        'alt': 'alt',
    }
    
    # Special character mapping for typing
    SPECIAL_CHARS: Dict[str, str] = {
        '@': 'shift+2',
        '#': 'shift+3',
        '$': 'shift+4',
        '%': 'shift+5',
        '^': 'shift+6',
        '&': 'shift+7',
        '*': 'shift+8',
        '(': 'shift+9',
        ')': 'shift+0',
        '-': 'minus',
        '_': 'shift+minus',
        '=': 'equal',
        '+': 'shift+equal',
        '[': 'bracketleft',
        ']': 'bracketright',
        '{': 'shift+bracketleft',
        '}': 'shift+bracketright',
        ';': 'semicolon',
        ':': 'shift+semicolon',
        "'": 'apostrophe',
        '"': 'shift+apostrophe',
        ',': 'comma',
        '.': 'period',
        '/': 'slash',
        '?': 'shift+slash',
        '\\': 'backslash',
        '|': 'shift+backslash',
        '<': 'shift+comma',
        '>': 'shift+period',
        '`': 'grave',
        '~': 'shift+grave',
    }
    
    def __init__(
        self,
        target_window_title: Optional[str] = None,
        keystroke_delay_ms: float = 50.0
    ):
        """
        Initialize action executor.
        
        Args:
            target_window_title: Title or partial title of target window
            keystroke_delay_ms: Delay in milliseconds between keystrokes (default: 50)
        """
        self.target_window_handle: Optional[int] = None
        self.target_window_title = target_window_title
        self.keystroke_delay = keystroke_delay_ms / 1000.0  # Convert to seconds
        
        # Disable pyautogui failsafe for production use
        pyautogui.FAILSAFE = False
        
        logger.info(f"ActionExecutor initialized with delay: {keystroke_delay_ms}ms")
    
    # ==================== WINDOW FINDING & MANAGEMENT ====================
    
    def find_target_window(self, title_pattern: str) -> bool:
        """
        Find target window by title pattern (case-insensitive partial match).
        
        Args:
            title_pattern: Partial or full window title to search for
            
        Returns:
            True if window found, False otherwise
            
        Example:
            >>> executor = ActionExecutor()
            >>> if executor.find_target_window("Dentrix"):
            ...     print("Found Dentrix window")
        """
        if not title_pattern:
            logger.error("Title pattern cannot be empty")
            return False
        
        try:
            self.target_window_handle = window_utils.find_window_by_title(title_pattern)
            
            if self.target_window_handle:
                self.target_window_title = title_pattern
                logger.info(f"Found target window: {title_pattern} (hwnd={self.target_window_handle})")
                return True
            else:
                logger.warning(f"Target window not found: {title_pattern}")
                return False
        
        except Exception as e:
            logger.error(f"Error finding window '{title_pattern}': {e}")
            return False
    
    def focus_target_window(self) -> bool:
        """
        Bring target window to foreground and focus it.
        
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> if executor.focus_target_window():
            ...     print("Window is now focused")
        """
        if not self.target_window_handle:
            logger.warning("Cannot focus: no target window set")
            return False
        
        try:
            return window_utils.focus_window(self.target_window_handle, activate=True)
        except Exception as e:
            logger.error(f"Error focusing window: {e}")
            return False
    
    def get_target_window_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about the target window.
        
        Returns:
            Dictionary with window information, or None if error
            
        Example:
            >>> info = executor.get_target_window_info()
            >>> if info:
            ...     print(f"Window position: ({info['x']}, {info['y']})")
        """
        if not self.target_window_handle:
            logger.warning("Cannot get info: no target window set")
            return None
        
        try:
            window_info = window_utils.get_window_info(self.target_window_handle)
            if window_info:
                return window_info.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting target window info: {e}")
            return None
    
    def is_target_window_focused(self) -> bool:
        """
        Check if the target window is currently focused.
        
        Returns:
            True if target window is focused, False otherwise
            
        Example:
            >>> if executor.is_target_window_focused():
            ...     print("Target window has focus")
        """
        if not self.target_window_handle:
            logger.debug("Cannot check focus: no target window set")
            return False
        
        try:
            return window_utils.is_window_focused(self.target_window_handle)
        except Exception as e:
            logger.error(f"Error checking target window focus: {e}")
            return False
    
    # ==================== KEYSTROKE SENDING ====================
    
    def set_keystroke_delay(self, delay_ms: float) -> None:
        """
        Set the delay between keystrokes.
        
        Args:
            delay_ms: Delay in milliseconds
            
        Example:
            >>> executor.set_keystroke_delay(100)  # 100ms between keys
        """
        self.keystroke_delay = delay_ms / 1000.0
        logger.debug(f"Keystroke delay set to {delay_ms}ms")
    
    def _map_keystroke(self, key: str) -> str:
        """
        Map a keystroke name to pyautogui equivalent.
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'ctrl+s')
            
        Returns:
            Mapped key name for pyautogui
        """
        key_lower = key.lower().strip()
        
        # Check if it's already a valid pyautogui key
        if key_lower in self.KEYSTROKE_MAP:
            return self.KEYSTROKE_MAP[key_lower]
        
        # Check for key combinations
        if '+' in key_lower:
            parts = [p.strip() for p in key_lower.split('+')]
            mapped_parts = []
            for part in parts:
                mapped_parts.append(self.KEYSTROKE_MAP.get(part, part))
            return '+'.join(mapped_parts)
        
        # Return as-is if not found (pyautogui might handle it)
        return key_lower
    
    def send_keystroke(self, key: str) -> bool:
        """
        Send a single keystroke or key combination.
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'ctrl+s')
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> executor.send_keystroke('tab')
            >>> executor.send_keystroke('ctrl+s')
        """
        if not key:
            logger.error("Keystroke key cannot be empty")
            return False
        
        try:
            mapped_key = self._map_keystroke(key)
            
            if '+' in mapped_key:
                # Key combination
                parts = mapped_key.split('+')
                pyautogui.hotkey(*parts)
            else:
                # Single key
                pyautogui.press(mapped_key)
            
            logger.debug(f"Sent keystroke: {key} (mapped: {mapped_key})")
            return True
        
        except Exception as e:
            logger.error(f"Error sending keystroke '{key}': {e}")
            return False
    
    def send_key_combo(self, keys: List[str]) -> bool:
        """
        Send a key combination (multiple keys pressed together).
        
        Args:
            keys: List of keys to press together (e.g., ['ctrl', 's'])
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> executor.send_key_combo(['ctrl', 's'])  # Save
            >>> executor.send_key_combo(['ctrl', 'z'])  # Undo
        """
        if not keys or len(keys) == 0:
            logger.error("Key list cannot be empty")
            return False
        
        try:
            mapped_keys = [self._map_keystroke(k) for k in keys]
            pyautogui.hotkey(*mapped_keys)
            logger.debug(f"Sent key combo: {'+'.join(keys)}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending key combo {keys}: {e}")
            return False
    
    # ==================== TEXT TYPING ====================
    
    def type_text(self, text: str) -> bool:
        """
        Type text into the target window.
        
        Args:
            text: Text to type
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> executor.type_text("Hello World")
        """
        if not text:
            logger.debug("Text is empty, nothing to type")
            return True
        
        try:
            # Use pyautogui with the configured delay
            pyautogui.typewrite(text, interval=self.keystroke_delay)
            logger.debug(f"Typed text: '{text}'")
            return True
        
        except Exception as e:
            logger.error(f"Error typing text '{text}': {e}")
            return False
    
    def type_special_character(self, char: str) -> bool:
        """
        Type a special character that requires Shift or other modifiers.
        
        Args:
            char: Character to type
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> executor.type_special_character('@')
            >>> executor.type_special_character('&')
        """
        if char in self.SPECIAL_CHARS:
            return self.send_keystroke(self.SPECIAL_CHARS[char])
        else:
            # Try to type it directly
            try:
                pyautogui.write(char)
                logger.debug(f"Typed special character: '{char}'")
                return True
            except Exception as e:
                logger.error(f"Error typing special character '{char}': {e}")
                return False
    
    def type_number(self, number: int) -> bool:
        """
        Type a single number (0-15) for periodontal charting.
        
        Args:
            number: Number to type (should be 0-15)
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If number is not in valid range (0-15)
            
        Example:
            >>> executor.type_number(3)
            >>> executor.type_number(15)
        """
        if not isinstance(number, int):
            logger.error(f"Number must be integer, got: {type(number)}")
            return False
        
        if number < 0 or number > 15:
            logger.error(f"Number must be 0-15 for perio charting, got: {number}")
            return False
        
        try:
            text = str(number)
            self.type_text(text)
            logger.debug(f"Typed perio number: {number}")
            return True
        
        except Exception as e:
            logger.error(f"Error typing number {number}: {e}")
            return False
    
    # ==================== NUMBER SEQUENCES ====================
    
    def type_number_sequence(
        self,
        numbers: List[int],
        separator: str = 'tab',
        final_separator: bool = False
    ) -> bool:
        """
        Type a sequence of numbers with a separator between each.
        
        This is the core method for periodontal charting entry.
        For example, typing [3, 2, 3] will enter "3 [Tab] 2 [Tab] 3".
        
        Args:
            numbers: List of numbers to type (0-15)
            separator: Key to press between numbers (default: 'tab')
            final_separator: Whether to press separator after last number
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If any number is not 0-15
            
        Example:
            >>> executor.type_number_sequence([3, 2, 3])  # 3 [Tab] 2 [Tab] 3
            >>> executor.type_number_sequence([4, 3, 3], final_separator=True)
        """
        if not numbers:
            logger.debug("Empty number sequence, nothing to type")
            return True
        
        try:
            # Validate all numbers first
            for num in numbers:
                if not isinstance(num, int):
                    raise ValueError(f"All numbers must be integers, got: {type(num)}")
                if num < 0 or num > 15:
                    raise ValueError(f"Number must be 0-15, got: {num}")
            
            # Type each number with separator
            for i, num in enumerate(numbers):
                # Type the number
                if not self.type_number(num):
                    return False
                
                # Add separator between numbers, or after last if requested
                if i < len(numbers) - 1 or final_separator:
                    if not self.send_keystroke(separator):
                        return False
                    
                    # Small delay after separator
                    time.sleep(self.keystroke_delay * 2)
            
            logger.info(f"Typed number sequence: {numbers} (separator: {separator})")
            return True
        
        except ValueError as e:
            logger.error(f"Invalid number sequence: {e}")
            return False
        except Exception as e:
            logger.error(f"Error typing number sequence {numbers}: {e}")
            return False
    
    # ==================== CONVENIENCE METHODS ====================
    
    def press_enter(self) -> bool:
        """Press Enter key"""
        return self.send_keystroke('enter')
    
    def press_tab(self) -> bool:
        """Press Tab key"""
        return self.send_keystroke('tab')
    
    def press_escape(self) -> bool:
        """Press Escape key"""
        return self.send_keystroke('escape')
    
    def undo(self) -> bool:
        """Execute Ctrl+Z (Undo)"""
        return self.send_key_combo(['ctrl', 'z'])
    
    def save(self) -> bool:
        """Execute Ctrl+S (Save)"""
        return self.send_key_combo(['ctrl', 's'])
    
    def select_all(self) -> bool:
        """Execute Ctrl+A (Select All)"""
        return self.send_key_combo(['ctrl', 'a'])
    
    def copy(self) -> bool:
        """Execute Ctrl+C (Copy)"""
        return self.send_key_combo(['ctrl', 'c'])
    
    def paste(self) -> bool:
        """Execute Ctrl+V (Paste)"""
        return self.send_key_combo(['ctrl', 'v'])
