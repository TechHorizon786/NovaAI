from __future__ import annotations

import os
from threading import Event

from PySide6.QtCore import QObject, Signal

from voice.vosk_engine import VoskConfig, VoskStreamingEngine


class VoiceWorker(QObject):
    started = Signal()
    stopped = Signal()
    partial = Signal(str)
    final = Signal(str)
    failed = Signal(str)

    def __init__(
        self,
        *,
        language: str = "en",
        model_path: str | None = None,
        device: int | None = None,
    ) -> None:
        super().__init__()
        self._stop_event = Event()
        self._language = (language or "en").strip().lower()

        if model_path is None:
            model_path = self._pick_model_path_from_env(self._language)

        self._config = VoskConfig(
            model_path=model_path or "",
            device=device,
        )

    def _pick_model_path_from_env(self, language: str) -> str:
        # Prefer dedicated language vars; fallback to generic
        if language in ("hi", "hindi"):
            return (
                os.getenv("VOSK_MODEL_PATH_HI", "").strip()
                or os.getenv("VOSK_MODEL_PATH", "").strip()
            )

        # default english
        return (
            os.getenv("VOSK_MODEL_PATH_EN", "").strip()
            or os.getenv("VOSK_MODEL_PATH", "").strip()
        )

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        try:
            engine = VoskStreamingEngine(self._config)
            self.started.emit()

            engine.listen_stream(
                stop_event=self._stop_event,
                on_partial=lambda t: self.partial.emit(t),
                on_final=lambda t: self.final.emit(t),
            )

            self.stopped.emit()
        except Exception as exc:
            self.failed.emit(str(exc))
            self.stopped.emit()