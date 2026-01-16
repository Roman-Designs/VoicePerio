"""
Configuration Manager - Application configuration handling
Manages loading and saving configuration from/to JSON files
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging
import copy


logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Application configuration management.
    
    Handles:
    - Loading config from file
    - Saving config changes
    - Default configuration values
    - User preferences (audio device, window title, etc.)
    """
    
    DEFAULT_CONFIG = {
        "audio": {
            "device_id": None,
            "sample_rate": 16000,
            "chunk_size": 4000,
            "channels": 1
        },
        "behavior": {
            "tab_after_sequence": True,
            "keystroke_delay_ms": 50,
            "auto_advance_tooth": False
        },
        "target": {
            "window_title": "Dentrix",
            "auto_focus": True
        },
        "gui": {
            "show_floating_indicator": True,
            "indicator_opacity": 0.9,
            "show_command_feedback": True
        },
        "hotkey": {
            "toggle_listening": "ctrl+shift+v"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Path to config file (default: %APPDATA%/VoicePerio/config.json)
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            appdata = os.getenv('APPDATA')
            config_file = 'config.json'
            self.config_path = Path(appdata) / 'VoicePerio' / config_file if appdata else Path(config_file)
        
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.load()
    
    def load(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if loaded successfully
        """
        if not self.config_path.exists():
            logger.info(f"Config file not found: {self.config_path}")
            self.save()  # Create default config
            return True
        
        try:
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
            
            # Merge with defaults
            self.config = self._deep_merge(self.DEFAULT_CONFIG, user_config)
            logger.info(f"Loaded config from {self.config_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if saved successfully
        """
        try:
            # Create directory if needed
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Saved config to {self.config_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get config value by dot-separated path.
        
        Args:
            key_path: Path like "audio.device_id"
            default: Default value if key not found
            
        Returns:
            Config value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set config value by dot-separated path.
        
        Args:
            key_path: Path like "audio.device_id"
            value: Value to set
            
        Returns:
            True if set successfully
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        return self.save()
    
    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """
        Deep merge override dict into base dict.
        
        Args:
            base: Base configuration
            override: Configuration to merge
            
        Returns:
            Merged configuration
        """
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
