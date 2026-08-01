from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class Sidebar(QFrame):
    """
    Colorful emoji-based sidebar (as in first version).
    Emits page_selected(key) for MainWindow page switching.
    """

    page_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("Sidebar")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMinimumWidth(220)

        self._buttons: dict[str, QPushButton] = {}
        self._selected_key: str = "chat"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("NOVA AI")
        title.setObjectName("SidebarTitle")

        subtitle = QLabel("Navigation")
        subtitle.setObjectName("SidebarSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        self._add_nav_button(layout, key="chat", text="💬  Chat")
        self._add_nav_button(layout, key="memory", text="🧠  Memory")
        self._add_nav_button(layout, key="voice", text="🎤  Voice")
        self._add_nav_button(layout, key="history", text="📂  History")
        self._add_nav_button(layout, key="settings", text="⚙️  Settings")

        layout.addStretch(1)

        hint = QLabel("More panels coming soon.")
        hint.setObjectName("SidebarHint")
        hint.setAlignment(Qt.AlignLeft)
        layout.addWidget(hint)

        self.set_selected("chat")

    def _add_nav_button(self, layout: QVBoxLayout, *, key: str, text: str) -> None:
        btn = QPushButton(text)
        btn.setObjectName("SidebarNavButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(44)
        btn.setProperty("selected", False)
        btn.clicked.connect(lambda _=False, k=key: self.set_selected(k))

        self._buttons[key] = btn
        layout.addWidget(btn)

    def set_selected(self, key: str) -> None:
        if key not in self._buttons:
            return

        self._selected_key = key

        for k, btn in self._buttons.items():
            btn.setProperty("selected", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

        self.page_selected.emit(key)

    def selected_key(self) -> str:
        return self._selected_key