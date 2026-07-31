from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout


class TypingIndicator(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("TypingIndicator")
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(0)

        self._label = QLabel("Generating")
        self._label.setObjectName("TypingText")
        self._label.setWordWrap(False)
        self._label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(self._label)

        self._step = 0
        self._timer = QTimer(self)
        self._timer.setInterval(350)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        self._step = (self._step + 1) % 4
        dots = "." * self._step
        self._label.setText(f"Generating{dots}")
        self._label.adjustSize()
        self.adjustSize()

    def set_indicator_max_width(self, max_width: int) -> None:
        self.setMaximumWidth(max_width)

    def stop(self) -> None:
        self._timer.stop()