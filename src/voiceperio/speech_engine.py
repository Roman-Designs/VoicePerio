"""
Speech Engine Module - Vosk wrapper for offline speech recognition
Handles speech-to-text conversion using Vosk
"""

from vosk import Model, KaldiRecognizer
from typing import Optional, List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class SpeechEngine:
    """
    Vosk wrapper for offline speech recognition.
    
    Methods:
    - load_model(path: str)
    - process_audio(chunk: bytes) -> Optional[str]
    - get_partial() -> str
    - set_grammar(words: List[str])  # Constrain to perio vocabulary
    """
    
    def __init__(self):
        """Initialize speech engine"""
        self.model = None
        self.recognizer = None
        self.partial_result = ""
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
            self.recognizer.SetWords(None)  # Reset any previous words/grammar
            logger.info(f"Loaded Vosk model from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            return False
    
    def process_audio(self, chunk: bytes) -> Optional[str]:
        """
        Process audio chunk and return recognized text if available.
        
        Args:
            chunk: Audio data as bytes
            
        Returns:
            Recognized text or None if recognition not yet complete
        """
        if not self.recognizer:
            logger.warning("Recognizer not initialized")
            return None
        
        try:
            # Feed audio to recognizer
            if self.recognizer.AcceptWaveform(chunk):
                # Complete result available
                result = self.recognizer.Result()
                self._parse_result(result, complete=True)
                return self.partial_result
            else:
                # Partial result available
                result = self.recognizer.PartialResult()
                self._parse_result(result, complete=False)
                return None
        
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None
    
    def _parse_result(self, result_json: str, complete: bool = False):
        """
        Parse Vosk JSON result and extract recognized text.
        
        Args:
            result_json: JSON result from Vosk
            complete: Whether this is a complete (True) or partial (False) result
        """
        try:
            result_dict = json.loads(result_json)
            
            if complete:
                # Complete result
                if 'result' in result_dict:
                    # Multiple words recognized
                    text = ' '.join([w['result'] for w in result_dict['result']])
                    self.partial_result = text
                    logger.debug(f"Complete result: {text}")
                else:
                    logger.debug("No complete result available")
            else:
                # Partial result
                if 'partial' in result_dict:
                    self.partial_result = result_dict['partial']
                    logger.debug(f"Partial result: {self.partial_result}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON result: {e}")
        except Exception as e:
            logger.error(f"Error parsing result: {e}")
    
    def get_partial(self) -> str:
        """
        Get partial recognition result (what was heard so far).
        
        Returns:
            Partial recognition text
        """
        return self.partial_result
    
    def set_grammar(self, words: Optional[List[str]] = None) -> bool:
        """
        Constrain speech recognition to specific words (grammar).
        
        Args:
            words: List of words to recognize (None to reset to default)
            
        Returns:
            True if grammar set successfully
        """
        if not self.recognizer:
            logger.warning("Recognizer not initialized")
            return False
        
        try:
            if words is None:
                # Reset to default recognition
                self.recognizer.SetWords(None)
                self.grammar = None
                logger.info("Grammar reset to default")
            else:
                # Set words for recognition
                # Vosk uses a simple word list format
                grammar_str = json.dumps(words)
                self.recognizer.SetWords(json.loads(grammar_str))
                self.grammar = words
                logger.info(f"Set grammar with {len(words)} words")
            
            return True
        
        except Exception as e:
            logger.error(f"Error setting grammar: {e}")
            return False
    
    def reset(self):
        """Reset the recognizer state for new recognition cycle."""
        if self.recognizer:
            try:
                self.partial_result = ""
                logger.debug("Recognizer state reset")
            except Exception as e:
                logger.error(f"Error resetting recognizer: {e}")
