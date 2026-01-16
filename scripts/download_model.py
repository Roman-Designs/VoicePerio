#!/usr/bin/env python3
"""
Download Vosk Model Script

Downloads the Vosk small English model required for speech recognition.
This is a standalone script that can be run before building the application.

Model Info:
- vosk-model-small-en-us: ~40MB, suitable for real-time recognition
- Source: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
- Destination: models/vosk-model-small-en-us/
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional


def get_model_path() -> Path:
    """Get the target model directory path."""
    # Get project root (two levels up from scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    models_dir = project_root / "models"
    return models_dir


def download_file(url: str, destination: Path, chunk_size: int = 8192) -> bool:
    """
    Download a file from URL to destination.
    
    Args:
        url: URL to download from
        destination: Path to save file to
        chunk_size: Size of chunks to download (bytes)
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        print(f"Downloading from {url}...")
        print(f"Destination: {destination}")
        
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"  Progress: {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({percent:.1f}%)")
        
        print("Download completed successfully")
        return True
    
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """
    Extract zip file to destination.
    
    Args:
        zip_path: Path to zip file
        extract_to: Directory to extract to
        
    Returns:
        True if extraction successful, False otherwise
    """
    try:
        print(f"Extracting {zip_path.name}...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        print("Extraction completed successfully")
        return True
    
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        return False


def download_vosk_model() -> bool:
    """
    Download and extract the Vosk model.
    
    Returns:
        True if successful, False otherwise
    """
    # Model details
    MODEL_NAME = "vosk-model-small-en-us"
    MODEL_VERSION = "0.15"
    MODEL_URL = f"https://alphacephei.com/vosk/models/{MODEL_NAME}-{MODEL_VERSION}.zip"
    
    models_dir = get_model_path()
    model_dir = models_dir / MODEL_NAME
    zip_path = models_dir / f"{MODEL_NAME}-{MODEL_VERSION}.zip"
    
    # Create models directory if needed
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    if model_dir.exists() and (model_dir / "am" / "final.mdl").exists():
        print(f"Vosk model already exists at {model_dir}")
        return True
    
    # Check if we need to download
    if model_dir.exists():
        print(f"Model directory exists but appears incomplete: {model_dir}")
        import shutil
        shutil.rmtree(model_dir)
        print("Removed incomplete model directory")
    
    # Download the model
    if not zip_path.exists():
        print(f"Model URL: {MODEL_URL}")
        if not download_file(MODEL_URL, zip_path):
            return False
    else:
        print(f"Model zip already exists: {zip_path}")
    
    # Extract the model
    if not extract_zip(zip_path, models_dir):
        return False
    
    # Rename extracted directory if needed
    extracted_dir = models_dir / f"{MODEL_NAME}-{MODEL_VERSION}"
    if extracted_dir.exists() and extracted_dir != model_dir:
        extracted_dir.rename(model_dir)
        print(f"Renamed extracted directory to {model_dir}")
    
    # Verify model was extracted correctly
    if (model_dir / "am" / "final.mdl").exists():
        print(f"✓ Vosk model successfully installed at {model_dir}")
        
        # Clean up zip file
        try:
            zip_path.unlink()
            print(f"Cleaned up temporary zip file")
        except:
            pass
        
        return True
    else:
        print(f"✗ Model appears incomplete: {model_dir}")
        return False


def main():
    """Main entry point."""
    print("=" * 70)
    print("Vosk Model Download Script")
    print("=" * 70)
    
    models_dir = get_model_path()
    model_dir = models_dir / "vosk-model-small-en-us"
    
    print(f"Target directory: {model_dir}")
    print()
    
    if download_vosk_model():
        print()
        print("=" * 70)
        print("✓ Setup completed successfully!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Install Python dependencies: pip install -r requirements.txt")
        print("2. Run the application: python -m voiceperio")
        return 0
    else:
        print()
        print("=" * 70)
        print("✗ Setup failed!")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
