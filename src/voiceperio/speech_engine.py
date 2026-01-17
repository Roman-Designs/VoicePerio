"""
Speech Engine Module - Vosk wrapper for offline speech recognition
Handles speech-to-text conversion using Vosk

Enhanced to provide word-level timing data for timing-based number grouping.
This allows differentiation between "232" (spoken quickly as one entry) and
"2 3 2" (spoken with pauses as separate entries).
"""

from vosk import Model, KaldiRecognizer
from typing import Optional, List, Dict, Any, NamedTuple
import json
import logging

logger = logging.getLogger(__name__)


class TimedWord(NamedTuple):
    """Represents a recognized word with timing information."""
    word: str
    start: float  # Start time in seconds
    end: float    # End time in seconds
    confidence: float = 1.0


class RecognitionResult:
    """
    Enhanced recognition result with word-level timing.
    
    Attributes:
        text: Full recognized text
        words: List of TimedWord objects with timing data
        is_final: Whether this is a final (complete) result
    """
    
    def __init__(
        self, 
        text: str = "", 
        words: "Optional[List[TimedWord]]" = None, 
        is_final: bool = False
    ):
        self.text = text
        self.words: List[TimedWord] = words if words is not None else []
        self.is_final = is_final
    
    def __repr__(self) -> str:
        return f"RecognitionResult(text='{self.text}', words={len(self.words)}, is_final={self.is_final})"


class SpeechEngine:
    """
    Vosk wrapper for offline speech recognition.
    
    Enhanced to provide word-level timing data for timing-based grouping.
    When processing audio, returns RecognitionResult objects that include
    both the recognized text and timing information for each word.
    
    Methods:
    - load_model(path: str)
    - process_audio(chunk: bytes) -> Optional[RecognitionResult]
    - get_partial() -> str
    - set_grammar(words: List[str])  # Constrain to perio vocabulary
    """
    
    def __init__(self):
        """Initialize speech engine"""
        self.model = None
        self.recognizer = None
        self.partial_result = ""
        self.last_result: Optional[RecognitionResult] = None
        self.grammar = None
        logger.debug("SpeechEngine initialized")
    
    def load_model(self, path: str) -> bool:
        """
        Load Vosk model from path.
        
        Args:
            path: Path to Vosk model directory
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            self.model = Model(path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            # Enable word-level timing data - CRITICAL for timing-based grouping
            self.recognizer.SetWords(True)
            logger.info(f"Loaded Vosk model from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            return False
    
    def process_audio(self, chunk: bytes) -> Optional[RecognitionResult]:
        """
        Process audio chunk and return recognition result if available.
        
        Args:
            chunk: Audio data as bytes
            
        Returns:
            RecognitionResult with text and word-level timing, or None if not yet complete
        """
        if not self.recognizer:
            logger.warning("Recognizer not initialized")
            return None
        
        try:
            # Feed audio to recognizer
            if self.recognizer.AcceptWaveform(chunk):
                # Complete result available
                result_json = self.recognizer.Result()
                return self._parse_result_enhanced(result_json, is_final=True)
            else:
                # Partial result available - update partial but don't return
                result_json = self.recognizer.PartialResult()
                self._parse_partial(result_json)
                return None
        
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None
    
    def process_audio_text(self, chunk: bytes) -> Optional[str]:
        """
        Process audio chunk and return just the recognized text (legacy interface).
        
        Args:
            chunk: Audio data as bytes
            
        Returns:
            Recognized text or None if recognition not yet complete
        """
        result = self.process_audio(chunk)
        if result and result.is_final:
            return result.text
        return None
    
    def _parse_result_enhanced(self, result_json: str, is_final: bool = False) -> Optional[RecognitionResult]:
        """
        Parse Vosk JSON result and extract text with word-level timing.
        
        Args:
            result_json: JSON result from Vosk
            is_final: Whether this is a final result
            
        Returns:
            RecognitionResult with timing data
        """
        try:
            result_dict = json.loads(result_json)
            
            words: List[TimedWord] = []
            text = ""
            
            if 'result' in result_dict:
                # Full result with word-level timing
                for word_data in result_dict['result']:
                    word = TimedWord(
                        word=word_data.get('word', ''),
                        start=word_data.get('start', 0.0),
                        end=word_data.get('end', 0.0),
                        confidence=word_data.get('conf', 1.0)
                    )
                    words.append(word)
                
                text = ' '.join(w.word for w in words)
            elif 'text' in result_dict:
                # Simple text result (no timing)
                text = result_dict['text']
            
            if text:
                self.partial_result = text
                result = RecognitionResult(text=text, words=words, is_final=is_final)
                self.last_result = result
                logger.debug(f"Parsed result: {text} ({len(words)} words with timing)")
                return result
            
            return None
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON result: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing result: {e}")
            return None
    
    def _parse_partial(self, result_json: str) -> None:
        """
        Parse partial result for display purposes.
        
        Args:
            result_json: JSON partial result from Vosk
        """
        try:
            result_dict = json.loads(result_json)
            if 'partial' in result_dict:
                self.partial_result = result_dict['partial']
                logger.debug(f"Partial result: {self.partial_result}")
        except Exception as e:
            logger.error(f"Error parsing partial result: {e}")
    

    
    def get_partial(self) -> str:
        """
        Get partial recognition result (what was heard so far).
        
        Returns:
            Partial recognition text
        """
        return self.partial_result
    
    def set_grammar(self, words: Optional[List[str]] = None) -> bool:
        """
        Constrain speech recognition to specific vocabulary.
        
        Note: Vosk doesn't support dynamic grammar like some other engines.
        The vocabulary is constrained by the model itself. This method
        is kept for API compatibility but SetWords(True) is used to enable
        word-level timing data, which is more useful for our purposes.
        
        Args:
            words: List of words (stored for reference, not enforced by Vosk)
            
        Returns:
            True (always succeeds as this is now a no-op for Vosk)
        """
        if not self.recognizer:
            logger.warning("Recognizer not initialized")
            return False
        
        try:
            # Store grammar for reference (Vosk doesn't enforce it)
            self.grammar = words
            
            # Ensure word-level timing is enabled (critical for timing-based grouping)
            self.recognizer.SetWords(True)
            
            if words:
                logger.info(f"Vocabulary reference set with {len(words)} words (Vosk uses model vocabulary)")
            else:
                logger.info("Vocabulary reference cleared")
            
            return True
        
        except Exception as e:
            logger.error(f"Error setting grammar: {e}")
            return False
    
    def reset(self):
        """Reset the recognizer state for new recognition cycle."""
        if self.recognizer:
            try:
                self.partial_result = ""
                self.last_result = None
                logger.debug("Recognizer state reset")
            except Exception as e:
                logger.error(f"Error resetting recognizer: {e}")
    
    def get_last_result(self) -> Optional[RecognitionResult]:
        """
        Get the last complete recognition result with timing data.
        
        Returns:
            Last RecognitionResult or None
        """
        return self.last_result
