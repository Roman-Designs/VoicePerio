"""
Audio feedback for successful Dentrix data entry.

Modes:
- off: disabled
- chime: lightweight success chime
- readback: short spoken confirmation (async)
"""

from __future__ import annotations

import logging
import queue
import re
import sys
import threading
from typing import Optional

logger = logging.getLogger(__name__)


class AudioFeedbackManager:
    """Handles optional chime/readback feedback without blocking charting."""

    VALID_MODES = {"off", "chime", "readback"}

    def __init__(
        self,
        mode: str = "off",
        readback_rate: int = 3,
        readback_max_chars: int = 32,
    ) -> None:
        self._lock = threading.RLock()
        self.mode = self._normalize_mode(mode)
        self.readback_rate = int(readback_rate)
        self.readback_max_chars = max(8, int(readback_max_chars))

        self._speech_queue: "queue.Queue[str]" = queue.Queue(maxsize=6)
        self._speech_thread: Optional[threading.Thread] = None
        self._speech_running = False
        self._speech_available: Optional[bool] = None

    def update_settings(
        self,
        mode: Optional[str] = None,
        readback_rate: Optional[int] = None,
        readback_max_chars: Optional[int] = None,
    ) -> None:
        """Update feedback settings at runtime."""
        with self._lock:
            if mode is not None:
                self.mode = self._normalize_mode(mode)
            if readback_rate is not None:
                self.readback_rate = int(readback_rate)
            if readback_max_chars is not None:
                self.readback_max_chars = max(8, int(readback_max_chars))

    def play_success(self, text: str) -> None:
        """Play success feedback based on current mode."""
        mode = self.mode

        if mode == "off":
            return

        if mode == "chime":
            self._play_chime()
            return

        readback_text = self._prepare_readback_text(text)
        if not readback_text:
            self._play_chime()
            return

        if not self._enqueue_readback(readback_text):
            # Fallback to an immediate chime if speech isn't available.
            self._play_chime()

    def shutdown(self) -> None:
        """Stop background speech worker."""
        if not self._speech_thread:
            return

        self._speech_running = False
        try:
            self._speech_queue.put_nowait("")
        except queue.Full:
            pass

        if self._speech_thread.is_alive():
            self._speech_thread.join(timeout=1.0)

    def _normalize_mode(self, mode: str) -> str:
        mode_lower = (mode or "").strip().lower()
        return mode_lower if mode_lower in self.VALID_MODES else "off"

    def _prepare_readback_text(self, text: str) -> str:
        clean = re.sub(r"\s+", " ", (text or "").strip())
        if not clean:
            return ""

        if len(clean) > self.readback_max_chars:
            clean = clean[: self.readback_max_chars].rstrip()

        return clean

    def _play_chime(self) -> None:
        try:
            if sys.platform.startswith("win"):
                import winsound

                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                # Best-effort fallback for non-Windows dev environments.
                sys.stdout.write("\a")
                sys.stdout.flush()
        except Exception as exc:
            logger.debug(f"Could not play chime: {exc}")

    def _enqueue_readback(self, text: str) -> bool:
        if not self._ensure_speech_worker():
            return False

        try:
            self._speech_queue.put_nowait(text)
            return True
        except queue.Full:
            try:
                self._speech_queue.get_nowait()
            except queue.Empty:
                pass

            try:
                self._speech_queue.put_nowait(text)
                return True
            except queue.Full:
                return False

    def _ensure_speech_worker(self) -> bool:
        if self._speech_available is False:
            return False

        if self._speech_thread and self._speech_thread.is_alive():
            return True

        if not sys.platform.startswith("win"):
            self._speech_available = False
            return False

        self._speech_running = True
        self._speech_thread = threading.Thread(
            target=self._speech_worker,
            daemon=True,
            name="VoicePerio-AudioFeedback",
        )
        self._speech_thread.start()
        return True

    def _speech_worker(self) -> None:
        voice = None
        pythoncom = None

        try:
            import pythoncom  # type: ignore
            import win32com.client  # type: ignore

            pythoncom.CoInitialize()
            voice = win32com.client.Dispatch("SAPI.SpVoice")
            self._speech_available = True
            logger.debug("SAPI speech worker initialized")
        except Exception as exc:
            self._speech_available = False
            self._speech_running = False
            logger.warning(f"Readback unavailable, falling back to chime: {exc}")
            return

        try:
            while self._speech_running:
                try:
                    text = self._speech_queue.get(timeout=0.25)
                except queue.Empty:
                    continue

                if not text:
                    continue

                try:
                    voice.Rate = int(self.readback_rate)
                    voice.Speak(text)
                except Exception as exc:
                    logger.debug(f"Speech readback failed: {exc}")
        finally:
            if pythoncom:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
