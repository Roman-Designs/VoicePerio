"""
Number Sequencer Module - Handles pocket depth sequence entry
Manages the typing of number sequences with proper delays and tab handling
"""

from typing import List, Optional
import time
import logging


logger = logging.getLogger(__name__)


class NumberSequencer:
    """
    Handles entry of pocket depth sequences.
    
    Workflow:
    1. Receive numbers [3, 2, 3]
    2. Type "3", press Tab
    3. Type "2", press Tab  
    4. Type "3"
    5. Optionally press Tab to advance to next site
    
    Config:
    - inter_number_delay: 50ms
    - tab_after_sequence: True/False
    - advance_key: "tab" (configurable)
    """
    
    def __init__(
        self,
        inter_number_delay_ms: int = 50,
        tab_after_sequence: bool = True,
        advance_key: str = "tab"
    ):
        """
        Initialize number sequencer.
        
        Args:
            inter_number_delay_ms: Delay between number entries in milliseconds
            tab_after_sequence: Whether to press Tab after sequence
            advance_key: Key to press between numbers (tab, space, etc.)
        """
        self.inter_number_delay_ms = inter_number_delay_ms
        self.tab_after_sequence = tab_after_sequence
        self.advance_key = advance_key
        self.action_executor = None
    
    def set_action_executor(self, executor):
        """Set the action executor for keystroke injection"""
        self.action_executor = executor
    
    def sequence_numbers(self, numbers: List[int]) -> bool:
        """
        Type a sequence of numbers with proper delays.
        
        Args:
            numbers: List of numbers to type (0-15)
            
        Returns:
            True if sequence entered successfully
        """
        if not self.action_executor:
            logger.error("Action executor not set")
            return False
        
        try:
            for i, num in enumerate(numbers):
                # Type the number
                self.action_executor.type_text(str(num))
                
                # Press advance key between numbers (not after last)
                if i < len(numbers) - 1:
                    time.sleep(self.inter_number_delay_ms / 1000.0)
                    self.action_executor.send_keystroke(self.advance_key)
            
            # Optionally press Tab after entire sequence
            if self.tab_after_sequence and len(numbers) > 0:
                time.sleep(self.inter_number_delay_ms / 1000.0)
                self.action_executor.send_keystroke("tab")
            
            logger.info(f"Successfully entered number sequence: {numbers}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to enter number sequence: {e}")
            return False
