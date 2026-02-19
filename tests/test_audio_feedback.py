"""Tests for audio feedback behavior."""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voiceperio.audio_feedback import AudioFeedbackManager


def test_invalid_mode_defaults_to_off():
    manager = AudioFeedbackManager(mode="invalid")
    assert manager.mode == "off"


def test_readback_text_is_trimmed_to_limit():
    manager = AudioFeedbackManager(mode="readback", readback_max_chars=10)
    assert manager._prepare_readback_text("1234567890123") == "1234567890"


def test_play_success_uses_chime_in_chime_mode(monkeypatch):
    manager = AudioFeedbackManager(mode="chime")
    chime_mock = Mock()
    monkeypatch.setattr(manager, "_play_chime", chime_mock)

    manager.play_success("2 3 2")
    chime_mock.assert_called_once()


def test_play_success_uses_readback_queue_in_readback_mode(monkeypatch):
    manager = AudioFeedbackManager(mode="readback")
    enqueue_mock = Mock(return_value=True)
    monkeypatch.setattr(manager, "_enqueue_readback", enqueue_mock)

    manager.play_success("2 3 2")
    enqueue_mock.assert_called_once_with("2 3 2")
