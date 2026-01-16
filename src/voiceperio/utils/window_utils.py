"""
Window Utilities Module - Window management helper functions
Provides utilities for finding and managing windows on Windows platform
"""

import win32gui
import win32con
from typing import Optional, List, Tuple
import logging


logger = logging.getLogger(__name__)


def find_window_by_title(title_pattern: str) -> Optional[int]:
    """
    Find a window by title pattern (partial match).
    
    Args:
        title_pattern: Partial window title to search for
        
    Returns:
        Window handle (hwnd) if found, None otherwise
    """
    found_hwnd = None
    
    def callback(hwnd, lParam):
        nonlocal found_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_pattern.lower() in title.lower():
                found_hwnd = hwnd
                return False  # Stop enumeration
        return True
    
    try:
        win32gui.EnumWindows(callback, None)
        if found_hwnd:
            logger.debug(f"Found window: {title_pattern} (hwnd={found_hwnd})")
        else:
            logger.warning(f"Window not found: {title_pattern}")
        return found_hwnd
    except Exception as e:
        logger.error(f"Error finding window: {e}")
        return None


def get_window_title(hwnd: int) -> Optional[str]:
    """
    Get window title by handle.
    
    Args:
        hwnd: Window handle
        
    Returns:
        Window title or None if error
    """
    try:
        return win32gui.GetWindowText(hwnd)
    except Exception as e:
        logger.error(f"Error getting window title: {e}")
        return None


def get_window_class(hwnd: int) -> Optional[str]:
    """
    Get window class name by handle.
    
    Args:
        hwnd: Window handle
        
    Returns:
        Window class name or None if error
    """
    try:
        return win32gui.GetClassName(hwnd)
    except Exception as e:
        logger.error(f"Error getting window class: {e}")
        return None


def is_window_visible(hwnd: int) -> bool:
    """Check if window is visible"""
    try:
        return win32gui.IsWindowVisible(hwnd)
    except Exception as e:
        logger.error(f"Error checking window visibility: {e}")
        return False


def focus_window(hwnd: int) -> bool:
    """
    Bring window to foreground and focus it.
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful
    """
    try:
        win32gui.SetForeground(hwnd)
        logger.info(f"Focused window (hwnd={hwnd})")
        return True
    except Exception as e:
        logger.error(f"Error focusing window: {e}")
        return False


def list_windows() -> List[Tuple[int, str, str]]:
    """
    List all visible windows.
    
    Returns:
        List of (hwnd, title, class_name) tuples
    """
    windows = []
    
    def callback(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            windows.append((hwnd, title, class_name))
        return True
    
    try:
        win32gui.EnumWindows(callback, None)
    except Exception as e:
        logger.error(f"Error listing windows: {e}")
    
    return windows
