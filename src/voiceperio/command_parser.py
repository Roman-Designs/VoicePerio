"""
Command Parser Module - Speech to command interpretation
Converts recognized speech text to executable commands
"""

from typing import Optional, List, Dict, Any
import json
import logging
from rapidfuzz import fuzz


logger = logging.getLogger(__name__)


class Command:
    """
    Represents a recognized command.
    
    Attributes:
        action: Type of action (e.g., "number_sequence", "keystroke", "indicator")
        params: Dictionary of command parameters
    """
    
    def __init__(self, action: str, **kwargs: Any) -> None:
        """
        Initialize command.
        
        Args:
            action: Type of action
            **kwargs: Command parameters
        """
        self.action: str = action
        self.params: Dict[str, Any] = kwargs
    
    def __repr__(self) -> str:
        """Return string representation of command."""
        return f"Command(action={self.action}, params={self.params})"


class CommandParser:
    """
    Interprets recognized speech as perio commands.
    
    Converts recognized speech text into actionable commands for periodontal charting.
    Handles number sequences, perio indicators, navigation, actions, and app control.
    
    Key Logic:
    - Detect number sequences: "three two three" → [3, 2, 3]
    - Detect single numbers: "four" → [4]
    - Detect indicators: "bleeding" → {action: "keystroke", key: "b"}
    - Detect navigation: "next" → {action: "keystroke", key: "tab"}
    
    Attributes:
        commands_db: Dictionary containing all command definitions from JSON
        word_to_number: Mapping of word strings to numeric values
    """
    
    def __init__(self, commands_file: Optional[str] = None) -> None:
        """
        Initialize command parser.
        
        Args:
            commands_file: Path to JSON file with command definitions
        """
        self.commands_db: Dict[str, Any] = {}
        self.word_to_number: Dict[str, int] = {}
        
        if commands_file:
            self.load_commands(commands_file)
    
    def load_commands(self, filepath: str) -> bool:
        """
        Load command definitions from JSON file.
        
        Initializes internal word-to-number mapping from the numbers section
        of the commands database.
        
        Args:
            filepath: Path to commands.json
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                self.commands_db = json.load(f)
            
            # Build word-to-number mapping
            if 'numbers' in self.commands_db:
                self.word_to_number = self.commands_db['numbers']
            
            logger.info(f"Loaded commands from {filepath} with {len(self.word_to_number)} number mappings")
            return True
        except Exception as e:
            logger.error(f"Failed to load commands: {e}")
            return False
    
    def parse(self, text: str) -> Optional[Command]:
        """
        Parse recognized speech text into a command.
        
        Main routing method that identifies the type of command and returns
        an appropriate Command object. Tries to match the text against:
        1. Number sequences (e.g., "three two three")
        2. Single numbers (e.g., "four")
        3. Perio indicators (e.g., "bleeding")
        4. Navigation commands (e.g., "next")
        5. Actions (e.g., "enter")
        6. App control (e.g., "stop")
        
        Args:
            text: Recognized speech text
            
        Returns:
            Command object or None if not recognized
        """
        text = text.strip().lower()
        
        if not text:
            logger.warning("Empty text provided to parse")
            return None
        
        logger.debug(f"Parsing text: '{text}'")
        
        # Try to parse as number sequence or single number
        if self.is_number_sequence(text):
            numbers = self.extract_numbers(text)
            if numbers:
                action_type = "number_sequence" if len(numbers) > 1 else "single_number"
                cmd = Command(
                    action=action_type,
                    numbers=numbers
                )
                logger.info(f"Parsed as {action_type}: {numbers}")
                return cmd
        
        # Try to parse as perio indicator
        indicator = self._parse_indicator(text)
        if indicator:
            return indicator
        
        # Try to parse as navigation command
        navigation = self._parse_navigation(text)
        if navigation:
            return navigation
        
        # Try to parse as action
        action = self._parse_action(text)
        if action:
            return action
        
        # Try to parse as app control
        app_control = self._parse_app_control(text)
        if app_control:
            return app_control
        
        logger.warning(f"Could not parse text: '{text}'")
        return None
    
    def is_number_sequence(self, text: str) -> bool:
        """
        Check if text is a sequence of numbers.
        
        Validates that text contains primarily number words and that the sequence
        length is 1-6 numbers (typical perio pocket depth format: 1 to 6 sites).
        
        Args:
            text: Text to check
            
        Returns:
            True if text is primarily numbers with valid sequence length, False otherwise
        """
        text = text.strip().lower()
        
        if not text or not self.word_to_number:
            return False
        
        # Split text into tokens
        words = text.split()
        
        # Check if all words are valid number words
        number_words = [w for w in words if w in self.word_to_number]
        
        # Valid sequence if all words are numbers and count is 1-6
        is_valid = (
            len(number_words) == len(words) and
            1 <= len(number_words) <= 6
        )
        
        logger.debug(f"is_number_sequence('{text}'): {is_valid} (found {len(number_words)} numbers)")
        return is_valid
    
    def extract_numbers(self, text: str) -> List[int]:
        """
        Extract numbers from text.
        
        Converts number words to integer values using the word-to-number mapping.
        Maintains order of numbers as spoken. Handles single and multiple numbers.
        
        Args:
            text: Text containing number words (e.g., "three two three")
            
        Returns:
            List of extracted integers (e.g., [3, 2, 3]) or empty list if no numbers found
        """
        text = text.strip().lower()
        numbers: List[int] = []
        
        if not text or not self.word_to_number:
            logger.warning(f"Cannot extract numbers: text='{text}', mapping available={bool(self.word_to_number)}")
            return numbers
        
        # Split text into words and convert to numbers
        words = text.split()
        for word in words:
            if word in self.word_to_number:
                numbers.append(self.word_to_number[word])
            else:
                logger.debug(f"Word '{word}' not recognized as number")
        
        logger.debug(f"Extracted numbers from '{text}': {numbers}")
        return numbers
    
    def _parse_indicator(self, text: str) -> Optional[Command]:
        """
        Parse perio indicator command.
        
        Matches text against perio indicator commands (bleeding, suppuration, etc.)
        using fuzzy matching to handle speech variations.
        
        Args:
            text: Recognized speech text
            
        Returns:
            Command object or None if not recognized as indicator
        """
        if 'perio_indicators' not in self.commands_db:
            return None
        
        indicators = self.commands_db['perio_indicators']
        
        # Build list of all indicator names and aliases
        candidates: Dict[str, str] = {}  # Candidate text -> indicator name
        for indicator_name, indicator_data in indicators.items():
            candidates[indicator_name] = indicator_name
            if 'aliases' in indicator_data:
                for alias in indicator_data['aliases']:
                    candidates[alias] = indicator_name
        
        # Try fuzzy match
        match = self.fuzzy_match(text, list(candidates.keys()), threshold=80)
        
        if match:
            indicator_name = candidates[match]
            indicator_data = indicators[indicator_name]
            
            # Check for class-based indicators (furcation, mobility)
            class_key = self._extract_class(text)
            
            cmd_params: Dict[str, Any] = {
                'indicator': indicator_name,
                'indicator_action': indicator_data.get('action', 'keystroke'),
                'key': indicator_data.get('key')
            }
            
            if class_key and 'classes' in indicator_data:
                cmd_params['class'] = class_key
            
            logger.info(f"Parsed indicator: {indicator_name}")
            return Command(action='indicator', **cmd_params)
        
        return None
    
    def _parse_navigation(self, text: str) -> Optional[Command]:
        """
        Parse navigation command.
        
        Matches text against navigation commands (next, previous, quadrant jumps, etc.)
        using fuzzy matching to handle speech variations.
        
        Args:
            text: Recognized speech text
            
        Returns:
            Command object or None if not recognized as navigation
        """
        if 'navigation' not in self.commands_db:
            return None
        
        navigation_cmds = self.commands_db['navigation']
        
        # Build list of all navigation names and aliases
        candidates: Dict[str, str] = {}  # Candidate text -> command name
        for cmd_name, cmd_data in navigation_cmds.items():
            candidates[cmd_name] = cmd_name
            if 'aliases' in cmd_data:
                for alias in cmd_data['aliases']:
                    candidates[alias] = cmd_name
        
        # Try fuzzy match
        match = self.fuzzy_match(text, list(candidates.keys()), threshold=80)
        
        if match:
            cmd_name = candidates[match]
            cmd_data = navigation_cmds[cmd_name]
            
            cmd_params: Dict[str, Any] = {
                'command': cmd_name,
                'nav_action': cmd_data.get('action', 'keystroke'),
            }
            
            # Add action-specific parameters
            for key in ['key', 'quadrant', 'side']:
                if key in cmd_data:
                    cmd_params[key] = cmd_data[key]
            
            logger.info(f"Parsed navigation: {cmd_name}")
            return Command(action='navigation', **cmd_params)
        
        return None
    
    def _parse_action(self, text: str) -> Optional[Command]:
        """
        Parse action command (enter, cancel, save, undo).
        
        Matches text against action commands using fuzzy matching to handle
        speech variations.
        
        Args:
            text: Recognized speech text
            
        Returns:
            Command object or None if not recognized as action
        """
        if 'actions' not in self.commands_db:
            return None
        
        actions = self.commands_db['actions']
        
        # Build list of all action names and aliases
        candidates: Dict[str, str] = {}  # Candidate text -> action name
        for action_name, action_data in actions.items():
            candidates[action_name] = action_name
            if 'aliases' in action_data:
                for alias in action_data['aliases']:
                    candidates[alias] = action_name
        
        # Try fuzzy match
        match = self.fuzzy_match(text, list(candidates.keys()), threshold=80)
        
        if match:
            action_name = candidates[match]
            action_data = actions[action_name]
            
            cmd_params: Dict[str, Any] = {
                'action_name': action_name,
                'action_type': action_data.get('action', 'keystroke'),
                'key': action_data.get('key')
            }
            
            logger.info(f"Parsed action: {action_name}")
            return Command(action='typed_action', **cmd_params)
        
        return None
    
    def _parse_app_control(self, text: str) -> Optional[Command]:
        """
        Parse app control command (wake, sleep, stop).
        
        Matches text against app control commands using fuzzy matching to handle
        multi-word commands like "voice perio wake".
        
        Args:
            text: Recognized speech text
            
        Returns:
            Command object or None if not recognized as app control
        """
        if 'app_control' not in self.commands_db:
            return None
        
        app_control_cmds = self.commands_db['app_control']
        
        # Build list of all app control names and aliases
        candidates: Dict[str, str] = {}  # Candidate text -> command name
        for cmd_name, cmd_data in app_control_cmds.items():
            candidates[cmd_name] = cmd_name
            if 'aliases' in cmd_data:
                for alias in cmd_data['aliases']:
                    candidates[alias] = cmd_name
        
        # Try fuzzy match
        match = self.fuzzy_match(text, list(candidates.keys()), threshold=80)
        
        if match:
            cmd_name = candidates[match]
            cmd_data = app_control_cmds[cmd_name]
            
            cmd_params: Dict[str, Any] = {
                'command': cmd_data.get('command', cmd_name)
            }
            
            logger.info(f"Parsed app control: {cmd_name}")
            return Command(action='app_control', **cmd_params)
        
        return None
    
    def _extract_class(self, text: str) -> Optional[int]:
        """
        Extract class number from text for class-based indicators.
        
        Looks for class indicators (one, two, three) in text for commands
        like "furcation one" or "mobility three".
        
        Args:
            text: Recognized speech text
            
        Returns:
            Class number (1, 2, 3) or None if not found
        """
        text = text.lower()
        
        # Look for class indicators in order
        for word in text.split():
            if word in self.word_to_number:
                num = self.word_to_number[word]
                if 1 <= num <= 3:
                    return num
        
        return None
    
    def fuzzy_match(self, text: str, candidates: List[str], threshold: int = 80) -> Optional[str]:
        """
        Find best matching candidate using fuzzy string matching.
        
        Uses RapidFuzz library for efficient string similarity matching.
        Handles speech variations and typos gracefully.
        
        Args:
            text: Input text to match
            candidates: List of candidate strings to match against
            threshold: Match score threshold (0-100), default 80
            
        Returns:
            Best matching candidate string or None if score below threshold
        """
        if not text or not candidates:
            return None
        
        best_match: Optional[str] = None
        best_score = 0.0
        
        for candidate in candidates:
            score = float(fuzz.ratio(text, candidate))
            if score > best_score and score >= threshold:
                best_match = candidate
                best_score = score
        
        if best_match:
            logger.debug(f"Fuzzy match '{text}' -> '{best_match}' (score={best_score})")
        
        return best_match
