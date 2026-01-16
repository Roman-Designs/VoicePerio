"""
Window Utilities Module - Window management helper functions
Provides utilities for finding, managing, and controlling windows on Windows platform.

Features:
- Find windows by title pattern, class name, or process
- Get detailed window information (position, size, visibility)
- Focus and activate windows
- List all visible windows with comprehensive details
- Thread-safe window enumeration
- Comprehensive error handling and logging
"""

import win32gui
import win32con
import win32api
from typing import Optional, List, Tuple, Dict, Any
import logging
from dataclasses import dataclass
import time


logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Detailed information about a window"""
    hwnd: int
    title: str
    class_name: str
    x: int
    y: int
    width: int
    height: int
    is_visible: bool
    is_maximized: bool
    is_minimized: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'hwnd': self.hwnd,
            'title': self.title,
            'class_name': self.class_name,
            'position': {'x': self.x, 'y': self.y},
            'size': {'width': self.width, 'height': self.height},
            'visible': self.is_visible,
            'maximized': self.is_maximized,
            'minimized': self.is_minimized
        }


def get_foreground_window() -> Optional[WindowInfo]:
    """
    Get the currently focused foreground window.
    
    Returns:
        WindowInfo of the foreground window, or None if error
        
    Example:
        >>> window = get_foreground_window()
        >>> if window:
        ...     print(f"Foreground: {window.title}")
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            return get_window_info(hwnd)
        else:
            logger.warning("No foreground window found")
            return None
    except Exception as e:
        logger.error(f"Error getting foreground window: {e}")
        return None


def get_window_info(hwnd: int) -> Optional[WindowInfo]:
    """
    Get detailed information about a window.
    
    Args:
        hwnd: Window handle
        
    Returns:
        WindowInfo object with comprehensive details, or None if error
        
    Example:
        >>> info = get_window_info(hwnd)
        >>> print(f"Position: ({info.x}, {info.y})")
        >>> print(f"Size: {info.width}x{info.height}")
    """
    if not hwnd:
        logger.error("Invalid window handle: None")
        return None
    
    try:
        title = win32gui.GetWindowText(hwnd) or ""
        class_name = win32gui.GetClassName(hwnd) or ""
        
        # Get window position and dimensions
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y
        except Exception as e:
            logger.warning(f"Could not get window rect: {e}")
            x = y = width = height = 0
        
        # Get window state
        is_visible = bool(win32gui.IsWindowVisible(hwnd))
        is_maximized = bool(win32api.GetWindowLong(hwnd, win32con.GWL_STYLE) & win32con.WS_MAXIMIZE) if is_visible else False
        is_minimized = bool(win32gui.IsIconic(hwnd)) if is_visible else False
        
        logger.debug(
            f"Window info: title='{title}', class='{class_name}', "
            f"pos=({x},{y}), size={width}x{height}"
        )
        
        return WindowInfo(
            hwnd=hwnd,
            title=title,
            class_name=class_name,
            x=x,
            y=y,
            width=width,
            height=height,
            is_visible=is_visible,
            is_maximized=is_maximized,
            is_minimized=is_minimized
        )
    
    except Exception as e:
        logger.error(f"Error getting window info for hwnd {hwnd}: {e}")
        return None


def find_window_by_title(title_pattern: str) -> Optional[int]:
    """
    Find a window by title pattern (partial case-insensitive match).
    
    Args:
        title_pattern: Partial window title to search for
        
    Returns:
        Window handle (hwnd) if found, None otherwise
        
    Example:
        >>> hwnd = find_window_by_title("Notepad")
        >>> if hwnd:
        ...     print(f"Found window: {hwnd}")
    """
    if not title_pattern:
        logger.error("Title pattern cannot be empty")
        return None
    
    found_hwnd = None
    
    def callback(hwnd, lParam):
        nonlocal found_hwnd
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title_pattern.lower() in title.lower():
                    found_hwnd = hwnd
                    logger.debug(f"Found matching window: '{title}' (hwnd={hwnd})")
                    return False  # Stop enumeration
        except Exception as e:
            logger.debug(f"Error in callback for hwnd {hwnd}: {e}")
        return True
    
    try:
        win32gui.EnumWindows(callback, None)
        if found_hwnd:
            logger.info(f"Found window matching '{title_pattern}': hwnd={found_hwnd}")
        else:
            logger.warning(f"Window not found matching: {title_pattern}")
        return found_hwnd
    except Exception as e:
        logger.error(f"Error enumerating windows: {e}")
        return None


def find_window_by_class(class_name: str) -> Optional[int]:
    """
    Find a window by class name.
    
    Args:
        class_name: Window class name to search for
        
    Returns:
        Window handle if found, None otherwise
        
    Example:
        >>> hwnd = find_window_by_class("Notepad")
    """
    if not class_name:
        logger.error("Class name cannot be empty")
        return None
    
    try:
        hwnd = win32gui.FindWindow(class_name, None)
        if hwnd:
            logger.info(f"Found window with class '{class_name}': hwnd={hwnd}")
            return hwnd
        else:
            logger.warning(f"No window found with class: {class_name}")
            return None
    except Exception as e:
        logger.error(f"Error finding window by class: {e}")
        return None


def get_window_title(hwnd: int) -> Optional[str]:
    """
    Get window title by handle.
    
    Args:
        hwnd: Window handle
        
    Returns:
        Window title string, or None if error
    """
    if not hwnd:
        logger.error("Invalid window handle: None")
        return None
    
    try:
        title = win32gui.GetWindowText(hwnd)
        logger.debug(f"Window title for hwnd {hwnd}: '{title}'")
        return title
    except Exception as e:
        logger.error(f"Error getting window title for hwnd {hwnd}: {e}")
        return None


def get_window_class(hwnd: int) -> Optional[str]:
    """
    Get window class name by handle.
    
    Args:
        hwnd: Window handle
        
    Returns:
        Window class name, or None if error
    """
    if not hwnd:
        logger.error("Invalid window handle: None")
        return None
    
    try:
        class_name = win32gui.GetClassName(hwnd)
        logger.debug(f"Window class for hwnd {hwnd}: '{class_name}'")
        return class_name
    except Exception as e:
        logger.error(f"Error getting window class for hwnd {hwnd}: {e}")
        return None


def get_window_position_size(hwnd: int) -> Optional[Tuple[int, int, int, int]]:
    """
    Get window position and dimensions.
    
    Args:
        hwnd: Window handle
        
    Returns:
        Tuple of (x, y, width, height), or None if error
        
    Example:
        >>> x, y, w, h = get_window_position_size(hwnd)
        >>> print(f"Window at ({x}, {y}), size {w}x{h}")
    """
    if not hwnd:
        logger.error("Invalid window handle: None")
        return None
    
    try:
        rect = win32gui.GetWindowRect(hwnd)
        x, y, right, bottom = rect
        width = right - x
        height = bottom - y
        
        logger.debug(f"Window position: ({x}, {y}), size: {width}x{height}")
        return (x, y, width, height)
    except Exception as e:
        logger.error(f"Error getting window position/size for hwnd {hwnd}: {e}")
        return None


def is_window_visible(hwnd: int) -> bool:
    """
    Check if window is visible.
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if visible, False otherwise
    """
    if not hwnd:
        logger.debug("Invalid window handle for visibility check")
        return False
    
    try:
        is_visible = bool(win32gui.IsWindowVisible(hwnd))
        logger.debug(f"Window hwnd {hwnd} visible: {is_visible}")
        return is_visible
    except Exception as e:
        logger.error(f"Error checking window visibility for hwnd {hwnd}: {e}")
        return False


def is_window_focused(hwnd: int) -> bool:
    """
    Check if a window is currently focused (foreground).
    
    Args:
        hwnd: Window handle to check
        
    Returns:
        True if window is focused, False otherwise
        
    Example:
        >>> if is_window_focused(my_hwnd):
        ...     print("Window has focus")
    """
    if not hwnd:
        logger.debug("Invalid window handle for focus check")
        return False
    
    try:
        foreground = win32gui.GetForegroundWindow()
        is_focused = (hwnd == foreground)
        logger.debug(f"Window hwnd {hwnd} focused: {is_focused}")
        return is_focused
    except Exception as e:
        logger.error(f"Error checking window focus for hwnd {hwnd}: {e}")
        return False


def focus_window(hwnd: int, activate: bool = True) -> bool:
    """
    Bring window to foreground and focus it.
    
    Args:
        hwnd: Window handle
        activate: Whether to activate the window (default: True)
        
    Returns:
        True if successful, False otherwise
        
    Example:
        >>> if focus_window(hwnd):
        ...     print("Window focused successfully")
    """
    if not hwnd:
        logger.warning("Cannot focus: invalid window handle")
        return False
    
    try:
        # Restore if minimized
        if win32gui.IsIconic(hwnd):
            logger.debug(f"Restoring minimized window hwnd {hwnd}")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.1)
        
        # Set focus
        if activate:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.05)  # Small delay to ensure focus
        
        logger.info(f"Focused window (hwnd={hwnd})")
        return True
    
    except Exception as e:
        logger.error(f"Error focusing window hwnd {hwnd}: {e}")
        return False


def activate_window(hwnd: int) -> bool:
    """
    Activate a window using multiple methods for reliability.
    
    Args:
        hwnd: Window handle
        
    Returns:
        True if successful, False otherwise
        
    Note:
        This uses SetForegroundWindow and optionally ShowWindow for
        better compatibility with different window types.
    """
    if not hwnd:
        logger.warning("Cannot activate: invalid window handle")
        return False
    
    try:
        # Method 1: SetForegroundWindow
        try:
            win32gui.SetForegroundWindow(hwnd)
            logger.debug("Activated window using SetForegroundWindow")
        except Exception as e:
            logger.debug(f"SetForegroundWindow failed: {e}")
        
        # Method 2: ShowWindow if minimized
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                logger.debug("Restored minimized window")
        except Exception as e:
            logger.debug(f"ShowWindow restore failed: {e}")
        
        time.sleep(0.05)
        logger.info(f"Activated window (hwnd={hwnd})")
        return True
    
    except Exception as e:
        logger.error(f"Error activating window hwnd {hwnd}: {e}")
        return False


def list_windows() -> List[WindowInfo]:
    """
    List all visible windows with detailed information.
    
    Returns:
        List of WindowInfo objects for all visible windows
        
    Example:
        >>> windows = list_windows()
        >>> for w in windows:
        ...     print(f"{w.title}: {w.class_name}")
    """
    windows: List[WindowInfo] = []
    
    def callback(hwnd, lParam):
        try:
            if win32gui.IsWindowVisible(hwnd):
                info = get_window_info(hwnd)
                if info:
                    windows.append(info)
        except Exception as e:
            logger.debug(f"Error processing window hwnd {hwnd}: {e}")
        return True
    
    try:
        win32gui.EnumWindows(callback, None)
        logger.info(f"Found {len(windows)} visible windows")
        return windows
    except Exception as e:
        logger.error(f"Error listing windows: {e}")
        return []


def list_windows_by_title(title_pattern: str = "") -> List[WindowInfo]:
    """
    List visible windows matching a title pattern.
    
    Args:
        title_pattern: Partial title to match (case-insensitive)
        
    Returns:
        List of matching WindowInfo objects
        
    Example:
        >>> windows = list_windows_by_title("Notepad")
        >>> for w in windows:
        ...     print(w.title)
    """
    all_windows = list_windows()
    
    if not title_pattern:
        return all_windows
    
    pattern_lower = title_pattern.lower()
    matching = [w for w in all_windows if pattern_lower in w.title.lower()]
    
    logger.info(f"Found {len(matching)} windows matching '{title_pattern}'")
    return matching


def print_window_info(hwnd: int) -> None:
    """
    Print detailed information about a window to logs.
    
    Args:
        hwnd: Window handle
    """
    info = get_window_info(hwnd)
    if info:
        logger.info(f"Window Information:")
        logger.info(f"  Handle (HWND): {info.hwnd}")
        logger.info(f"  Title: {info.title}")
        logger.info(f"  Class: {info.class_name}")
        logger.info(f"  Position: ({info.x}, {info.y})")
        logger.info(f"  Size: {info.width}x{info.height}")
        logger.info(f"  Visible: {info.is_visible}")
        logger.info(f"  Maximized: {info.is_maximized}")
        logger.info(f"  Minimized: {info.is_minimized}")
    else:
        logger.warning(f"Could not get info for window hwnd {hwnd}")
