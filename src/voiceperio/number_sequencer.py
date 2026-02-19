"""
Number Sequencer Module - Handles pocket depth sequence entry
Manages the typing of number sequences with proper delays and field advancement.

Updated for Dentrix Enterprise workflow:
- Each NumberGroup is typed into a single field (e.g., "232" -> types "232")
- Dentrix auto-advances after numeric entry, so no post-entry Enter/Tab is sent
- Supports skip (enter zeros), skip with count (advance N fields)
- Uses Dentrix keyboard shortcuts for navigation

Key Dentrix Enterprise shortcuts used:
- Enter/Page Down: Explicit navigation when requested
- Page Up: Previous field  
- Page Down: Next field
- Home: Go to first position
- Ctrl+S: Save
"""

from typing import List, Optional, TYPE_CHECKING
import time
import logging

if TYPE_CHECKING:
    from .number_grouper import NumberGroup
    from .action_executor import ActionExecutor

logger = logging.getLogger(__name__)


class NumberSequencer:
    """
    Handles entry of pocket depth sequences for Dentrix Enterprise.
    
    New workflow (timing-based grouping):
    1. Receive list of NumberGroup objects (from NumberGrouper)
    2. For each group:
       a. Type the digits (e.g., "232")
       b. Wait briefly for Dentrix auto-advance timing
    
    This replaces the old workflow where Tab was pressed between individual digits.
    Now, each NumberGroup represents ONE field entry, regardless of digit count.
    
    Example: "2, 232, 43, 3" spoken -> 4 field entries:
    - Field 1: "2"
    - Field 2: "232"
    - Field 3: "43"
    - Field 4: "3"
    
    Config:
    - inter_entry_delay_ms: Delay between field entries (default: 50ms)
    - advance_key: Key used for explicit navigation commands (default: "enter")
    """
    
    def __init__(
        self,
        inter_entry_delay_ms: int = 50,
        advance_key: str = "enter"
    ):
        """
        Initialize number sequencer.
        
        Args:
            inter_entry_delay_ms: Delay between field entries in milliseconds
            advance_key: Key for explicit navigation (enter, tab, etc.)
        """
        self.inter_entry_delay_ms = inter_entry_delay_ms
        self.advance_key = advance_key
        self.action_executor: Optional["ActionExecutor"] = None
        
        logger.info(f"NumberSequencer initialized: delay={inter_entry_delay_ms}ms, advance_key={advance_key}")
    
    def set_action_executor(self, executor: "ActionExecutor") -> None:
        """Set the action executor for keystroke injection."""
        self.action_executor = executor
    
    def enter_number_groups(self, groups: List["NumberGroup"]) -> bool:
        """
        Enter a list of NumberGroups, each as a separate field entry.
        
        This is the new primary method for entering pocket depth data.
        Each NumberGroup is typed into one field and Dentrix advances automatically.
        
        Args:
            groups: List of NumberGroup objects from NumberGrouper
            
        Returns:
            True if all entries successful
        """
        if not self.action_executor:
            logger.error("Action executor not set")
            return False
        
        if not groups:
            logger.debug("No number groups to enter")
            return True
        
        try:
            for i, group in enumerate(groups):
                # Type the digit string (e.g., "232", "43", "3")
                if not self.action_executor.type_text(group.digits):
                    return False
                
                # Keep pacing delay to preserve stability in Dentrix input handling
                time.sleep(self.inter_entry_delay_ms / 1000.0)
                
                logger.debug(f"Entered group {i+1}/{len(groups)}: '{group.digits}'")
            
            logger.info(f"Successfully entered {len(groups)} number groups: {[g.digits for g in groups]}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to enter number groups: {e}")
            return False
    
    def enter_single_value(self, value: str) -> bool:
        """
        Enter a single value.
        
        Args:
            value: The digit string to enter
            
        Returns:
            True if successful
        """
        if not self.action_executor:
            logger.error("Action executor not set")
            return False
        
        try:
            if not self.action_executor.type_text(value):
                return False
            time.sleep(self.inter_entry_delay_ms / 1000.0)
            
            logger.debug(f"Entered single value: '{value}'")
            return True
        
        except Exception as e:
            logger.error(f"Failed to enter single value: {e}")
            return False
    
    def skip_with_zeros(self) -> bool:
        """
        Skip current field by entering "000".
        
        This is the "skip" command behavior - enters three zeros
        as a placeholder. Dentrix auto-advances after the numeric entry.
        
        Returns:
            True if successful
        """
        if not self.action_executor:
            logger.error("Action executor not set")
            return False
        
        try:
            # Enter three zeros
            if not self.action_executor.type_text("000"):
                return False
            time.sleep(self.inter_entry_delay_ms / 1000.0)
            
            logger.info("Skipped field with zeros")
            return True
        
        except Exception as e:
            logger.error(f"Failed to skip with zeros: {e}")
            return False
    
    def skip_fields(self, count: int) -> bool:
        """
        Skip multiple fields without entering data.
        
        This is the "skip N" command behavior - just advances
        the cursor N fields without entering any data.
        
        Args:
            count: Number of fields to skip
            
        Returns:
            True if successful
        """
        if not self.action_executor:
            logger.error("Action executor not set")
            return False
        
        if count < 1:
            logger.warning(f"Invalid skip count: {count}")
            return False
        
        try:
            for i in range(count):
                self.action_executor.send_keystroke(self.advance_key)
                time.sleep(self.inter_entry_delay_ms / 1000.0)
            
            logger.info(f"Skipped {count} fields")
            return True
        
        except Exception as e:
            logger.error(f"Failed to skip fields: {e}")
            return False
    
    def go_next(self) -> bool:
        """Advance to next field."""
        if not self.action_executor:
            return False
        return self.action_executor.send_keystroke(self.advance_key)
    
    def go_previous(self) -> bool:
        """Go to previous field (Page Up in Dentrix)."""
        if not self.action_executor:
            return False
        return self.action_executor.send_keystroke("pageup")
    
    def go_home(self) -> bool:
        """Go to first field position (Home in Dentrix)."""
        if not self.action_executor:
            return False
        return self.action_executor.send_keystroke("home")
    
    def save(self) -> bool:
        """Save the current exam (Ctrl+S in Dentrix)."""
        if not self.action_executor:
            return False
        return self.action_executor.send_keystroke("ctrl+s")
    
    # Legacy method for backward compatibility
    def sequence_numbers(self, numbers: List[int]) -> bool:
        """
        Legacy method: Type a sequence of numbers as separate entries.
        
        DEPRECATED: Use enter_number_groups() instead for timing-based grouping.
        
        This method is kept for backward compatibility and still applies
        inter-entry pacing, but does not send post-entry Enter/Tab.
        
        Args:
            numbers: List of numbers to type (0-9)
            
        Returns:
            True if sequence entered successfully
        """
        if not self.action_executor:
            logger.error("Action executor not set")
            return False
        
        try:
            for num in numbers:
                # Type the number
                if not self.action_executor.type_text(str(num)):
                    return False
                
                # Small delay
                time.sleep(self.inter_entry_delay_ms / 1000.0)
                
            logger.info(f"Successfully entered number sequence (legacy): {numbers}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to enter number sequence: {e}")
            return False
