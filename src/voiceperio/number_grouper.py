"""
Number Grouper Module - Timing-based grouping of spoken numbers

This module solves the key challenge of differentiating between numbers spoken
quickly together (as a single field entry) vs. numbers spoken with pauses
(as separate field entries).

Example: "2, 232, 43, 3, 231" spoken as:
- "two" [pause] "two three two" [pause] "four three" [pause] "three" [pause] "two three one"
Should produce: ["2", "232", "43", "3", "231"] - five separate field entries

The algorithm uses word-level timing data from Vosk to detect pauses between
number words. Words spoken within the threshold are grouped together.
"""

from typing import List, Optional, Dict, Any, NamedTuple
from dataclasses import dataclass
import logging
from rapidfuzz import fuzz
from difflib import SequenceMatcher

from .speech_engine import TimedWord, RecognitionResult

logger = logging.getLogger(__name__)


# Number word to digit mapping
# Single-digit words map to "0"–"9"; double-digit words (10–19) map to "10"–"19".
WORD_TO_DIGIT: Dict[str, str] = {
    # Single digits
    "zero": "0",
    "oh": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    # Double digits (10–19) — require Dentrix numpad minus protocol
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
}

# Set of digit strings that represent double-digit perio values (10–19).
# Used by NumberGroup.requires_minus_protocol and group_numbers() boundary logic.
_DOUBLE_DIGIT_VALUES: frozenset = frozenset(
    {"10", "11", "12", "13", "14", "15", "16", "17", "18", "19"}
)


@dataclass
class NumberGroup:
    """
    Represents a group of numbers spoken together as one field entry.
    
    Attributes:
        digits: The combined digit string (e.g., "232")
        words: The original TimedWord objects
        start_time: Start time of first word
        end_time: End time of last word
    """
    digits: str
    words: List[TimedWord]
    start_time: float
    end_time: float
    
    @property
    def value(self) -> str:
        """Get the digit string value."""
        return self.digits
    
    @property
    def as_int(self) -> Optional[int]:
        """Get as integer if valid, else None."""
        try:
            return int(self.digits)
        except ValueError:
            return None
    
    @property
    def requires_minus_protocol(self) -> bool:
        """
        Return True when this group must be entered via the Dentrix numpad
        minus-key protocol (i.e. the value is a double-digit depth 10–19).

        Per Dentrix docs: press numpad '-' then the units digit to enter
        depths of 10 mm or greater.
        """
        return self.digits in _DOUBLE_DIGIT_VALUES
    
    def __repr__(self) -> str:
        return f"NumberGroup('{self.digits}', {self.start_time:.2f}-{self.end_time:.2f}s)"


@dataclass
class ParsedCommand:
    """
    Represents a parsed voice command from recognition result.
    
    Can be either:
    - Number groups (for field entry)
    - A navigation/action command
    """
    command_type: str  # "numbers", "navigation", "skip", "skip_count", "save", "home", etc.
    number_groups: List[NumberGroup] = None  # For "numbers" type
    params: Dict[str, Any] = None  # For commands with parameters
    raw_text: str = ""
    
    def __post_init__(self):
        if self.number_groups is None:
            self.number_groups = []
        if self.params is None:
            self.params = {}


class NumberGrouper:
    """
    Groups spoken numbers based on timing gaps between words.
    
    The key insight is that when someone says "two three two" quickly,
    the gaps between words are small (~50-150ms). When they pause before
    the next entry, the gap is larger (~300-600ms+).
    
    Configuration:
    - pause_threshold_ms: Gap duration that indicates a new field entry (default: 300ms)
    - min_pause_ms: Minimum gap to consider (below this, always group together)
    
    Example workflow:
    1. Receive RecognitionResult with word-level timing
    2. Identify which words are numbers
    3. Group consecutive numbers by timing gaps
    4. Return list of NumberGroups for field entry
    """
    
    # Default configuration
    DEFAULT_PAUSE_THRESHOLD_MS = 300  # Gap > 300ms = new field
    DEFAULT_MIN_PAUSE_MS = 100  # Gap < 100ms = definitely same field
    
    def __init__(
        self,
        pause_threshold_ms: float = DEFAULT_PAUSE_THRESHOLD_MS,
        min_pause_ms: float = DEFAULT_MIN_PAUSE_MS
    ):
        """
        Initialize number grouper.
        
        Args:
            pause_threshold_ms: Gap threshold to start new group (milliseconds)
            min_pause_ms: Minimum gap to consider for grouping decisions
        """
        self.pause_threshold = pause_threshold_ms / 1000.0  # Convert to seconds
        self.min_pause = min_pause_ms / 1000.0
        
        # Command word detection
        self.navigation_words = {"next", "previous", "back", "prev"}
        self.skip_words = {"skip", "missing"}
        self.action_words = {"save", "home", "bleeding", "suppuration", "pus", 
                           "plaque", "calculus", "furcation", "mobility", "recession",
                           "clear"}
        
        # Phonetic confusion mappings for speech recognition errors
        self.phonetic_confusions = {
            # Single-digit homophones / common mishearings
            'for': ['four'],
            'four': ['for'],
            'to': ['two', 'too'],
            'two': ['to', 'too'],
            'too': ['to', 'two'],
            'won': ['one'],
            'one': ['won'],
            'ate': ['eight'],
            'eight': ['ate'],
            'sex': ['six'],
            'six': ['sex'],
            'niner': ['nine'],
            'nine': ['niner'],
            'fife': ['five'],
            'five': ['fife', 'fiv'],
            'fiv': ['five', 'fife'],
            # Double-digit mishearings (10–19)
            'ten': ['ten'],
            'elven': ['eleven'],
            'eleven': ['eleven', 'elven'],
            'twelv': ['twelve'],
            'twelve': ['twelve', 'twelv'],
            'thirten': ['thirteen'],
            'thirteen': ['thirteen', 'thirten'],
            'forteen': ['fourteen'],
            'fourteen': ['fourteen', 'forteen'],
            'fiveteen': ['fifteen'],
            'fifteen': ['fifteen', 'fiveteen'],
            'sixten': ['sixteen'],
            'sixteen': ['sixteen', 'sixten'],
            'eightteen': ['eighteen'],
            'eighteen': ['eighteen', 'eightteen'],
            'ninteen': ['nineteen'],
            'nineteen': ['nineteen', 'ninteen'],
        }
        
        logger.info(f"NumberGrouper initialized: threshold={pause_threshold_ms}ms")
    
    def set_pause_threshold(self, threshold_ms: float) -> None:
        """
        Set the pause threshold for grouping.
        
        Args:
            threshold_ms: New threshold in milliseconds
        """
        self.pause_threshold = threshold_ms / 1000.0
        logger.info(f"Pause threshold set to {threshold_ms}ms")
    
    def parse_recognition(self, result: RecognitionResult) -> ParsedCommand:
        """
        Parse a recognition result into a command.
        
        This is the main entry point. Analyzes the recognition result and
        determines if it's:
        - A series of number groups for field entry
        - A navigation command (next, previous)
        - A skip command (with optional count)
        - An action command (save, home, etc.)
        
        Args:
            result: RecognitionResult with word-level timing
            
        Returns:
            ParsedCommand indicating what action to take
        """
        if not result or not result.text:
            return ParsedCommand(command_type="empty", raw_text="")
        
        text_lower = result.text.lower().strip()
        words = result.words if result.words else []
        
        logger.debug(f"Parsing recognition: '{text_lower}' ({len(words)} words)")
        
        # Check for navigation commands first
        if self._is_navigation_command(text_lower):
            return self._parse_navigation(text_lower)
        
        # Check for skip command (with possible count)
        if self._is_skip_command(text_lower):
            return self._parse_skip(text_lower, words)
        
        # Check for action commands
        if self._is_action_command(text_lower):
            return self._parse_action(text_lower)
        
        # Otherwise, try to parse as numbers
        number_groups = self.group_numbers(words)
        
        if number_groups:
            return ParsedCommand(
                command_type="numbers",
                number_groups=number_groups,
                raw_text=result.text
            )
        
        # Fallback: unrecognized
        logger.debug(f"Unrecognized command: '{text_lower}'")
        return ParsedCommand(command_type="unrecognized", raw_text=result.text)
    
    def match_number_word(self, word: str, threshold: int = 75) -> Optional[str]:
        """
        Match a word to a number word using fuzzy matching.
        
        Handles speech recognition errors:
        - "four" heard as "for"
        - "two" heard as "to"
        - etc.
        
        Args:
            word: Word to match
            threshold: Match score threshold (0-100)
            
        Returns:
            Matched number word or None if no good match
        """
        word_lower = word.lower()
        
        # First try exact match
        if word_lower in WORD_TO_DIGIT:
            return word_lower
        
        # Check phonetic confusions
        if word_lower in self.phonetic_confusions:
            for variant in self.phonetic_confusions[word_lower]:
                if variant in WORD_TO_DIGIT:
                    logger.debug(f"Phonetic match: '{word}' -> '{variant}'")
                    return variant
        
        # Try fuzzy matching
        best_match: Optional[str] = None
        best_score = 0.0
        
        for num_word in WORD_TO_DIGIT.keys():
            score = float(fuzz.ratio(word_lower, num_word))
            if score > best_score and score >= threshold:
                best_match = num_word
                best_score = score
        
        if best_match:
            logger.debug(f"Fuzzy matched '{word}' -> '{best_match}' (score={best_score:.1f})")
            return best_match
        
        return None
    
    def group_numbers(self, words: List[TimedWord]) -> List[NumberGroup]:
        """
        Group number words based on timing gaps.
        
        Uses fuzzy matching to handle speech recognition errors where:
        - "four" is heard as "for"
        - "two" is heard as "to"
        - etc.
        
        Args:
            words: List of TimedWord objects from speech recognition
            
        Returns:
            List of NumberGroup objects, each representing one field entry
        """
        if not words:
            return []
        
        # Filter to number words (using fuzzy matching for robustness)
        number_words = []
        for w in words:
            matched_word = self.match_number_word(w.word, threshold=75)
            if matched_word:
                # Create a new TimedWord with the corrected word
                number_words.append(TimedWord(
                    word=matched_word,
                    start=w.start,
                    end=w.end,
                    confidence=w.confidence
                ))
        
        if not number_words:
            return []
        
        groups: List[NumberGroup] = []
        current_group_words: List[TimedWord] = []
        
        for i, curr_word in enumerate(number_words):
            curr_digit = WORD_TO_DIGIT.get(curr_word.word.lower(), "")
            is_double_digit = curr_digit in _DOUBLE_DIGIT_VALUES
            
            if is_double_digit:
                # Double-digit words (ten–nineteen) are ALWAYS their own group.
                # Flush whatever was accumulating before this word.
                if current_group_words:
                    groups.append(self._create_group(current_group_words))
                    current_group_words = []
                # Emit the double-digit word as its own standalone group.
                groups.append(self._create_group([curr_word]))
                logger.debug(f"Double-digit boundary: '{curr_word.word}' -> '{curr_digit}' (own group)")
            else:
                if not current_group_words:
                    # Starting a fresh group
                    current_group_words.append(curr_word)
                else:
                    prev_word = number_words[i - 1]
                    # Calculate gap between end of previous word and start of current
                    gap = curr_word.start - prev_word.end
                    
                    logger.debug(f"Gap between '{prev_word.word}' and '{curr_word.word}': {gap*1000:.0f}ms")
                    
                    if gap >= self.pause_threshold:
                        # Large gap - start new group
                        groups.append(self._create_group(current_group_words))
                        current_group_words = [curr_word]
                    else:
                        # Small gap - add to current group
                        current_group_words.append(curr_word)
        
        # Don't forget the last group
        if current_group_words:
            groups.append(self._create_group(current_group_words))
        
        logger.info(f"Grouped {len(number_words)} number words into {len(groups)} groups: {groups}")
        return groups
    
    def _create_group(self, words: List[TimedWord]) -> NumberGroup:
        """
        Create a NumberGroup from a list of words.
        
        Args:
            words: List of TimedWord objects to combine
            
        Returns:
            NumberGroup with combined digits
        """
        digits = ""
        for w in words:
            digit = WORD_TO_DIGIT.get(w.word.lower(), "")
            digits += digit
        
        return NumberGroup(
            digits=digits,
            words=words,
            start_time=words[0].start if words else 0.0,
            end_time=words[-1].end if words else 0.0
        )
    
    def group_numbers_simple(self, text: str) -> List[NumberGroup]:
        """
        Simple grouping without timing (fallback for when timing data unavailable).
        
        This treats each space-separated number word as a separate entry.
        Use this only when timing data is not available.
        
        Args:
            text: Recognized text
            
        Returns:
            List of NumberGroup objects (one per number word)
        """
        words = text.lower().split()
        groups: List[NumberGroup] = []
        
        for word in words:
            if word in WORD_TO_DIGIT:
                digit = WORD_TO_DIGIT[word]
                groups.append(NumberGroup(
                    digits=digit,
                    words=[],
                    start_time=0.0,
                    end_time=0.0
                ))
        
        return groups
    
    def _is_navigation_command(self, text: str) -> bool:
        """Check if text is a navigation command."""
        words = set(text.split())
        return bool(words & self.navigation_words)
    
    def _is_skip_command(self, text: str) -> bool:
        """Check if text is a skip command."""
        words = text.split()
        return any(w in self.skip_words for w in words)
    
    def _is_action_command(self, text: str) -> bool:
        """Check if text is an action command."""
        words = set(text.split())
        return bool(words & self.action_words)
    
    def _parse_navigation(self, text: str) -> ParsedCommand:
        """Parse navigation command."""
        if "next" in text:
            return ParsedCommand(command_type="next", raw_text=text)
        elif "previous" in text or "back" in text or "prev" in text:
            return ParsedCommand(command_type="previous", raw_text=text)
        
        return ParsedCommand(command_type="navigation", raw_text=text)
    
    def _parse_skip(self, text: str, words: List[TimedWord]) -> ParsedCommand:
        """
        Parse skip command, extracting count if present.
        
        "skip" -> skip with zeros (000) and advance
        "skip five" -> advance 5 fields without entering data
        """
        # Look for a number following "skip"
        text_words = text.split()
        skip_count = None
        
        for i, word in enumerate(text_words):
            if word in self.skip_words:
                # Check if next word is a number
                if i + 1 < len(text_words):
                    next_word = text_words[i + 1]
                    if next_word in WORD_TO_DIGIT:
                        skip_count = int(WORD_TO_DIGIT[next_word])
                        break
        
        if skip_count is not None:
            return ParsedCommand(
                command_type="skip_count",
                params={"count": skip_count},
                raw_text=text
            )
        else:
            # Plain skip - enter zeros and advance
            return ParsedCommand(
                command_type="skip",
                raw_text=text
            )
    
    def _parse_action(self, text: str) -> ParsedCommand:
        """Parse action command."""
        if "save" in text:
            return ParsedCommand(command_type="save", raw_text=text)
        elif "home" in text:
            return ParsedCommand(command_type="home", raw_text=text)
        elif "bleeding" in text or "bleed" in text:
            return ParsedCommand(command_type="indicator", params={"indicator": "bleeding"}, raw_text=text)
        elif "suppuration" in text or "pus" in text:
            return ParsedCommand(command_type="indicator", params={"indicator": "suppuration"}, raw_text=text)
        elif "plaque" in text:
            return ParsedCommand(command_type="indicator", params={"indicator": "plaque"}, raw_text=text)
        elif "calculus" in text:
            return ParsedCommand(command_type="indicator", params={"indicator": "calculus"}, raw_text=text)
        elif "furcation" in text:
            return ParsedCommand(command_type="indicator", params={"indicator": "furcation"}, raw_text=text)
        elif "mobility" in text:
            return ParsedCommand(command_type="indicator", params={"indicator": "mobility"}, raw_text=text)
        elif "recession" in text:
            return ParsedCommand(command_type="indicator", params={"indicator": "recession"}, raw_text=text)
        elif "clear" in text:
            return ParsedCommand(command_type="clear", raw_text=text)
        
        return ParsedCommand(command_type="action", raw_text=text)
