"""
Action Executor Module - Keystroke injection and window control
Handles sending keystrokes to target windows
"""

from typing import List, Optional
import pyautogui
import win32gui
import win32con
import logging


logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Sends keystrokes to target window.
    
    Methods:
    - find_target_window(title_pattern: str) -> bool
    - focus_target_window()
    - send_keystroke(key: str)
    - send_key_combo(keys: List[str])
    - type_text(text: str)
    - type_number_sequence(numbers: List[int])
    
    Uses:
    - win32gui for window finding/focusing
    - pyautogui for keystroke injection
    """
    
    def __init__(self, target_window_title: Optional[str] = None):
        """
        Initialize action executor.
        
        Args:
            target_window_title: Title or partial title of target window
        """
        self.target_window_handle = None
        self.target_window_title = target_window_title
        self.keystroke_delay = 0.05  # 50ms default
    
    def find_target_window(self, title_pattern: str) -> bool:
        """
        Find target window by title pattern.
        
        Args:
            title_pattern: Partial or full window title to search for
            
        Returns:
            True if window found, False otherwise
        """
        try:
            def window_callback(hwnd, lParam):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title_pattern.lower() in title.lower():
                        self.target_window_handle = hwnd
                        return False  # Stop searching
                return True
            
            win32gui.EnumWindows(window_callback, None)
            
            if self.target_window_handle:
                logger.info(f"Found target window: {title_pattern}")
                return True
            else:
                logger.warning(f"Target window not found: {title_pattern}")
                return False
        
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            return False
    
    def focus_target_window(self) -> bool:
        """
        Bring target window to focus.
        
        Returns:
            True if successful
        """
        if not self.target_window_handle:
            logger.warning("No target window set")
            return False
        
        try:
            win32gui.SetForeground(self.target_window_handle)
            logger.info("Target window focused")
            return True
        except Exception as e:
            logger.error(f"Error focusing window: {e}")
            return False
    
    def send_keystroke(self, key: str):
        """
        Send a single keystroke or key combination.
        
        Args:
            key: Key name (e.g., 'enter', 'tab', 'ctrl+s')
        """
        try:
            pyautogui.press(key)
            logger.debug(f"Sent keystroke: {key}")
        except Exception as e:
            logger.error(f"Error sending keystroke {key}: {e}")
    
    def send_key_combo(self, keys: List[str]):
        """
        Send a key combination (multiple keys pressed together).
        
        Args:
            keys: List of keys to press together (e.g., ['ctrl', 's'])
        """
        try:
            pyautogui.hotkey(*keys)
            logger.debug(f"Sent key combo: {'+'.join(keys)}")
        except Exception as e:
            logger.error(f"Error sending key combo: {e}")
    
    def type_text(self, text: str):
        """
        Type text into target window.
        
        Args:
            text: Text to type
        """
        try:
            pyautogui.typewrite(text, interval=self.keystroke_delay)
            logger.debug(f"Typed text: {text}")
        except Exception as e:
            logger.error(f"Error typing text: {e}")
    
    def type_number_sequence(self, numbers: List[int]):
        """
        Type a sequence of numbers with Tab between each.
        
        Args:
            numbers: List of numbers to type
        """
        try:
            for i, num in enumerate(numbers):
                self.type_text(str(num))
                if i < len(numbers) - 1:
                    self.send_keystroke('tab')
            logger.info(f"Typed number sequence: {numbers}")
        except Exception as e:
            logger.error(f"Error typing number sequence: {e}")
