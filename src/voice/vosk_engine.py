from __future__ import annotations

import json
import os
import queue
import time
from dataclasses import dataclass
from threading import Event
from typing import Callable


@dataclass(frozen=True)
class VoskConfig:
    model_path: str
    samplerate: int = 16000
    channels: int = 1
    device: int | None = None


class VoskStreamingEngine:
    """
    Offline Speech-to-Text using Vosk + sounddevice (streaming).
    - No Qt dependency.
    - Raises clear errors if dependencies/model missing.
    """

    def __init__(self, config: VoskConfig) -> None:
        self._config = config
        self._validate()

        # Optional deps import here (so app can run without voice deps)
        try:
            import vosk  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "Vosk is not installed. Install with: pip install vosk"
            ) from exc

        self._vosk = vosk
        self._model = vosk.Model(self._config.model_path)

    def _validate(self) -> None:
        if not self._config.model_path or not self._config.model_path.strip():
            raise RuntimeError(
                "VOSK model path missing. Set environment variable VOSK_MODEL_PATH "
                "to your downloaded Vosk model folder."
            )
        if not os.path.isdir(self._config.model_path):
            raise RuntimeError(
                f"Invalid VOSK_MODEL_PATH: '{self._config.model_path}' (folder not found)."
            )

    def listen_stream(
        self,
        stop_event: Event,
        on_partial: Callable[[str], None] | None = None,
        on_final: Callable[[str], None] | None = None,
    ) -> None:
        """
        Blocking call: listens until stop_event is set.
        Calls on_partial/on_final with recognized text.
        """
        try:
            import sounddevice as sd  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "sounddevice is not installed. Install with: pip install sounddevice"
            ) from exc

        recognizer = self._vosk.KaldiRecognizer(self._model, self._config.samplerate)

        q: queue.Queue[bytes] = queue.Queue()

        def _callback(indata, frames, _time, status) -> None:
            # Called in sounddevice thread
            if stop_event.is_set():
                return
            if status:
                # ignore status noise; caller can display if needed later
                pass
            q.put(bytes(indata))

        last_partial = ""
        last_partial_ts = 0.0

        # Raw input to avoid float conversion overhead, dtype int16
        with sd.RawInputStream(
            samplerate=self._config.samplerate,
            blocksize=8000,
            device=self._config.device,
            dtype="int16",
            channels=self._config.channels,
            callback=_callback,
        ):
            while not stop_event.is_set():
                try:
                    data = q.get(timeout=0.15)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result() or "{}")
                    text = (result.get("text") or "").strip()
                    if text and on_final is not None:
                        on_final(text)
                    last_partial = ""
                else:
                    pres = json.loads(recognizer.PartialResult() or "{}")
                    partial = (pres.get("partial") or "").strip()
                    if not partial:
                        continue

                    # throttle partial updates to reduce UI spam
                    now = time.monotonic()
                    if partial != last_partial and (now - last_partial_ts) > 0.10:
                        last_partial = partial
                        last_partial_ts = now
                        if on_partial is not None:
                            on_partial(partial)

        # Flush final when stopping
        try:
            final = json.loads(recognizer.FinalResult() or "{}")
            text = (final.get("text") or "").strip()
            if text and on_final is not None:
                on_final(text)
        except Exception:
            return