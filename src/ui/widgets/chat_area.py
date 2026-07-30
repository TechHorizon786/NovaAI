from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.chat_bubble import ChatBubble


class ChatArea(QScrollArea):
    _BUBBLE_WIDTH_RATIO = 0.68
    _BUBBLE_MIN_WIDTH = 260
    _AUTO_SCROLL_THRESHOLD_PX = 40  # user already bottom pe ho to hi autoscroll

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("ChatScroll")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Important: viewport bhi QWidget hai, global QWidget background rule ki wajah se
        # black blocks aa rahe the. ObjectName deke QSS se transparent karenge.
        self.viewport().setObjectName("ChatViewport")

        self._container = QWidget()
        self._container.setObjectName("ChatContainer")

        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(18, 18, 18, 18)
        self._layout.setSpacing(12)

        self._bottom_spacer = QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self._layout.addItem(self._bottom_spacer)

        self.setWidget(self._container)

        self._bubbles: list[ChatBubble] = []
        self._auto_scroll_pending = False

        # Content height change hota hai to scroll range update hota hai.
        # Yahin pe reliable auto-scroll trigger karenge.
        self.verticalScrollBar().rangeChanged.connect(self._on_scroll_range_changed)

    def add_message(self, role: str, text: str) -> None:
        should_auto_scroll = self._is_near_bottom()

        row = QWidget()
        row.setObjectName("ChatRow")

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        is_user = role == ChatBubble.ROLE_USER
        bubble = ChatBubble(role=role, text=text)
        self._bubbles.append(bubble)

        if is_user:
            row_layout.addStretch(1)
            row_layout.addWidget(bubble, 0, Qt.AlignRight)
        else:
            row_layout.addWidget(bubble, 0, Qt.AlignLeft)
            row_layout.addStretch(1)

        insert_index = max(0, self._layout.count() - 1)
        self._layout.insertWidget(insert_index, row)

        self._apply_bubble_widths()

        if should_auto_scroll:
            self._request_scroll_to_bottom(row)

    def _is_near_bottom(self) -> bool:
        vbar = self.verticalScrollBar()
        return vbar.value() >= (vbar.maximum() - self._AUTO_SCROLL_THRESHOLD_PX)

    def _request_scroll_to_bottom(self, target_row: QWidget) -> None:
        self._auto_scroll_pending = True

        # layout settle hone ke baad scroll
        QTimer.singleShot(0, lambda: self._scroll_to_row_and_bottom(target_row))
        # extra safety (kabhi-kabhi maximum late update hota)
        QTimer.singleShot(30, lambda: self._scroll_to_row_and_bottom(target_row))

    def _scroll_to_row_and_bottom(self, target_row: QWidget) -> None:
        # Ensure last row visible + then force bottom
        self.ensureWidgetVisible(target_row, 0, 20)
        self.scroll_to_bottom()

    def _on_scroll_range_changed(self, _min: int, _max: int) -> None:
        if not self._auto_scroll_pending:
            return

        self.scroll_to_bottom()
        QTimer.singleShot(80, self._clear_auto_scroll_pending)

    def _clear_auto_scroll_pending(self) -> None:
        self._auto_scroll_pending = False

    def scroll_to_bottom(self) -> None:
        vbar = self.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._apply_bubble_widths()

    def _apply_bubble_widths(self) -> None:
        viewport_width = self.viewport().width()
        max_width = max(
            self._BUBBLE_MIN_WIDTH,
            int(viewport_width * self._BUBBLE_WIDTH_RATIO),
        )
        for bubble in self._bubbles:
            bubble.set_bubble_max_width(max_width)