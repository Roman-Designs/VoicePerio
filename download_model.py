#!/usr/bin/env python3
"""
ChartAssist - Vosk Model Downloader

Downloads and extracts the Vosk speech recognition model.
Run this script after installing dependencies to set up the speech engine.

Usage:
    python scripts/download_model.py [--model MODEL_NAME]

Available models (English):
    - vosk-model-small-en-us (40MB)  - Fast, good for constrained vocabulary [DEFAULT]
    - vosk-model-en-us-0.22 (1.8GB)  - Most accurate, requires more RAM
    - vosk-model-en-us-0.22-lgraph (128MB) - Balanced accuracy/size
"""

import os
import sys
import zipfile
import argparse
import urllib.request
import shutil
from pathlib import Path

# Model configurations
MODELS = {
    "vosk-model-small-en-us-0.15": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "size_mb": 40,
        "description": "Small model - fast, good for dental vocabulary",
        "recommended": True
    },
    "vosk-model-en-us-0.22": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "size_mb": 1800,
        "description": "Large model - highest accuracy, requires 4GB+ RAM",
        "recommended": False
    },
    "vosk-model-en-us-0.22-lgraph": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip",
        "size_mb": 128,
        "description": "Medium model - balanced accuracy and speed",
        "recommended": False
    }
}

DEFAULT_MODEL = "vosk-model-small-en-us-0.15"


def get_project_root() -> Path:
    """Get the project root directory."""
    # Script is in scripts/, project root is parent
    return Path(__file__).parent.parent


def get_models_dir() -> Path:
    """Get the models directory."""
    return get_project_root() / "models"


def download_with_progress(url: str, dest_path: Path, description: str = "Downloading"):
    """Download a file with progress indication."""
    print(f"{description}...")
    print(f"  URL: {url}")
    print(f"  Destination: {dest_path}")
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded / total_size) * 100)
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            sys.stdout.write(f"\r  Progress: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)")
            sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, dest_path, reporthook=report_progress)
        print("\n  Download complete!")
        return True
    except Exception as e:
        print(f"\n  Error downloading: {e}")
        return False


def extract_zip(zip_path: Path, extract_to: Path):
    """Extract a zip file."""
    print(f"Extracting to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get the root folder name inside the zip
        root_folder = zip_ref.namelist()[0].split('/')[0]
        zip_ref.extractall(extract_to)
    print("  Extraction complete!")
    return extract_to / root_folder


def main():
    parser = argparse.ArgumentParser(
        description="Download Vosk speech recognition model for ChartAssist"
    )
    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()),
        default=DEFAULT_MODEL,
        help=f"Model to download (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models and exit"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if model exists"
    )
    
    args = parser.parse_args()
    
    # List models
    if args.list:
        print("\nAvailable Vosk Models:\n")
        for name, info in MODELS.items():
            rec = " [RECOMMENDED]" if info["recommended"] else ""
            print(f"  {name}{rec}")
            print(f"    Size: {info['size_mb']} MB")
            print(f"    Description: {info['description']}")
            print()
        return 0
    
    # Setup paths
    models_dir = get_models_dir()
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_info = MODELS[args.model]
    model_name = args.model
    
    # Check if already exists
    # The extracted folder might not have the version number
    possible_names = [
        model_name,
        model_name.rsplit('-', 1)[0],  # Without version
        "vosk-model-small-en-us",
        "vosk-model-en-us"
    ]
    
    existing_model = None
    for name in possible_names:
        check_path = models_dir / name
        if check_path.exists() and not args.force:
            existing_model = check_path
            break
    
    if existing_model and not args.force:
        print(f"Model already exists at: {existing_model}")
        print("Use --force to re-download")
        return 0
    
    # Download
    print(f"\n{'='*60}")
    print(f"ChartAssist - Vosk Model Downloader")
    print(f"{'='*60}\n")
    print(f"Model: {model_name}")
    print(f"Size: ~{model_info['size_mb']} MB")
    print(f"Description: {model_info['description']}\n")
    
    zip_path = models_dir / f"{model_name}.zip"
    
    if not download_with_progress(model_info['url'], zip_path, "Downloading model"):
        return 1
    
    # Extract
    extracted_path = extract_zip(zip_path, models_dir)
    
    # Rename to standard name if needed
    standard_name = models_dir / "vosk-model-small-en-us"
    if "small" in model_name and extracted_path != standard_name:
        if standard_name.exists():
            shutil.rmtree(standard_name)
        extracted_path.rename(standard_name)
        extracted_path = standard_name
    
    # Cleanup zip
    print("Cleaning up...")
    zip_path.unlink()
    
    print(f"\n{'='*60}")
    print("Setup Complete!")
    print(f"{'='*60}")
    print(f"\nModel installed at: {extracted_path}")
    print("\nYou can now run ChartAssist:")
    print("  python -m chartassist")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
