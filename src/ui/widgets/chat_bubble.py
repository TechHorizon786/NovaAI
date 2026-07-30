from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout


class ChatBubble(QFrame):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(self, role: str, text: str, parent=None) -> None:
        super().__init__(parent)

        if role == self.ROLE_USER:
            self.setObjectName("BubbleUser")
        else:
            self.setObjectName("BubbleNova")

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(0)

        self._label = QLabel(text)
        self._label.setObjectName("BubbleText")
        self._label.setWordWrap(True)
        self._label.setTextFormat(Qt.PlainText)
        self._label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(self._label)

    def set_bubble_max_width(self, max_width: int) -> None:
        self.setMaximumWidth(max_width)

    def set_text(self, text: str) -> None:
        self._label.setText(text)
        self._label.adjustSize()
        self.adjustSize()