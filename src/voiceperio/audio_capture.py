"""
Audio Capture Module - Microphone input streaming
Handles audio capture from microphone using sounddevice
"""

import sounddevice as sd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AudioCapture:
    """
    Streams audio from microphone to speech engine.
    
    Config:
    - sample_rate: 16000 (Vosk requirement)
    - chunk_size: 4000 samples
    - channels: 1 (mono)
    
    Methods:
    - list_devices() -> List[Dict]
    - set_device(device_id: int)
    - start()
    - stop()
    - get_audio_chunk() -> bytes
    """
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 4000, channels: int = 1):
        """
        Initialize audio capture.
        
        Args:
            sample_rate: Sample rate in Hz (Vosk requires 16000)
            chunk_size: Number of samples per chunk
            channels: Number of audio channels (1 = mono)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.device_id = None
        self.stream = None
        self.is_running = False
        logger.debug(f"AudioCapture initialized: sample_rate={sample_rate}, chunk_size={chunk_size}")
    
    def list_devices(self) -> List[Dict]:
        """
        List all available audio devices.
        
        Returns:
            List of device dictionaries with id, name, and info
        """
        try:
            devices = sd.query_devices()
            device_list = []
            
            for idx, device in enumerate(devices):
                device_dict = {
                    'id': idx,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                }
                device_list.append(device_dict)
                logger.debug(f"Device {idx}: {device['name']} ({device['max_input_channels']} channels)")
            
            logger.info(f"Found {len(device_list)} audio devices")
            return device_list
        
        except Exception as e:
            logger.error(f"Error listing audio devices: {e}")
            return []
    
    def set_device(self, device_id: int) -> bool:
        """
        Set the audio device to use.
        
        Args:
            device_id: Device ID to use
            
        Returns:
            True if device is valid, False otherwise
        """
        try:
            devices = sd.query_devices()
            if 0 <= device_id < len(devices):
                self.device_id = device_id
                logger.info(f"Set audio device to {device_id}: {devices[device_id]['name']}")
                return True
            else:
                logger.error(f"Invalid device ID: {device_id}")
                return False
        except Exception as e:
            logger.error(f"Error setting audio device: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start audio capture stream.
        
        Returns:
            True if stream started successfully, False otherwise
        """
        if self.is_running:
            logger.warning("Audio stream already running")
            return True
        
        try:
            self.stream = sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                dtype=np.int16
            )
            self.stream.start()
            self.is_running = True
            logger.info("Audio capture stream started")
            return True
        
        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")
            self.is_running = False
            return False
    
    def stop(self) -> bool:
        """
        Stop audio capture stream.
        
        Returns:
            True if stream stopped successfully, False otherwise
        """
        if not self.is_running or not self.stream:
            logger.warning("Audio stream not running")
            return True
        
        try:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.is_running = False
            logger.info("Audio capture stream stopped")
            return True
        
        except Exception as e:
            logger.error(f"Error stopping audio stream: {e}")
            return False
    
    def get_audio_chunk(self) -> Optional[bytes]:
        """
        Get next audio chunk from stream.
        
        Returns:
            Bytes of audio data or None if stream not running
            
        Raises:
            RuntimeError: If stream is not running
        """
        if not self.is_running or not self.stream:
            return None
        
        try:
            # Read audio chunk from stream
            audio_data, overflowed = self.stream.read(self.chunk_size)
            
            if overflowed:
                logger.warning("Audio buffer overflow - some audio data was lost")
            
            # Convert numpy array to bytes (int16 format for Vosk)
            audio_bytes = audio_data.astype(np.int16).tobytes()
            return audio_bytes
        
        except Exception as e:
            logger.error(f"Error reading audio chunk: {e}")
            return None
