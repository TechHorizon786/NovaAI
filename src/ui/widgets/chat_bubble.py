from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
)


class ChatBubble(QFrame):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(self, role: str, text: str, parent=None) -> None:
        super().__init__(parent)

        self._role = role

        if role == self.ROLE_USER:
            self.setObjectName("BubbleUser")
        else:
            self.setObjectName("BubbleNova")

        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 10, 14, 10)
        self._layout.setSpacing(8)

        self._content_widgets: list[QFrame | QLabel] = []

        self.set_text(text)

    def set_bubble_max_width(self, max_width: int) -> None:
        self.setMaximumWidth(max_width)

    def set_text(self, text: str) -> None:
        self._clear_content()

        # Code blocks (``` ```) only for assistant messages
        if self._role == self.ROLE_ASSISTANT and "```" in text:
            segments = self._split_text_and_code_blocks(text)
            for seg_type, seg_text in segments:
                if seg_type == "text" and not seg_text.strip():
                    continue

                if seg_type == "code":
                    self._layout.addWidget(self._create_code_block(seg_text))
                else:
                    self._layout.addWidget(self._create_text_label(seg_text))
        else:
            self._layout.addWidget(self._create_text_label(text))

        self.adjustSize()

    def _clear_content(self) -> None:
        for w in self._content_widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self._content_widgets.clear()

    def _create_text_label(self, text: str) -> QLabel:
        label = QLabel()
        label.setObjectName("BubbleText")
        label.setWordWrap(True)

        # Markdown only for assistant messages
        if self._role == self.ROLE_ASSISTANT and hasattr(Qt, "MarkdownText"):
            label.setTextFormat(Qt.MarkdownText)
            label.setTextInteractionFlags(
                Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
            )
            label.setOpenExternalLinks(True)
        else:
            label.setTextFormat(Qt.PlainText)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        label.setText(text)
        label.adjustSize()

        self._content_widgets.append(label)
        return label

    def _create_code_block(self, code: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("CodeBlockFrame")
        frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Local styling (main_window QSS touch nahi kar rahe)
        frame.setStyleSheet("""
        QFrame#CodeBlockFrame{
            background:#0F172A;
            border:1px solid #334155;
            border-radius:12px;
        }
        QPushButton#CodeCopyButton{
            background:#1F2937;
            color:#E5E7EB;
            border:none;
            border-radius:10px;
            padding:6px 10px;
            font-weight:600;
        }
        QPushButton#CodeCopyButton:hover{
            background:#334155;
        }
        QPushButton#CodeCopyButton:disabled{
            background:#0B1220;
            color:#94A3B8;
        }
        QScrollArea#CodeScrollArea{
            background:transparent;
            border:none;
        }
        QLabel#CodeBlockText{
            background:transparent;
            color:#E2E8F0;
            font-family:Consolas, "Cascadia Mono", "Courier New";
            font-size:13px;
        }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        copy_btn = QPushButton("Copy")
        copy_btn.setObjectName("CodeCopyButton")
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(
            lambda _=False, c=code, b=copy_btn: self._copy_code(c, b)
        )
        layout.addWidget(copy_btn, 0, Qt.AlignRight)

        # Code label (NO WRAP)
        code_label = QLabel(code)
        code_label.setObjectName("CodeBlockText")
        code_label.setWordWrap(False)  # important: wrap off
        code_label.setTextFormat(Qt.PlainText)
        code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        code_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        code_label.adjustSize()
        # ensure scroll works horizontally
        code_label.setMinimumWidth(code_label.sizeHint().width())

        scroll = QScrollArea()
        scroll.setObjectName("CodeScrollArea")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(False)  # important: allow horizontal scroll
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        scroll.setWidget(code_label)

        # height = lines ke hisaab se (no internal vertical scrolling)
        scroll.setFixedHeight(code_label.sizeHint().height() + 6)

        layout.addWidget(scroll)

        self._content_widgets.append(frame)
        return frame

    def _copy_code(self, code: str, button: QPushButton) -> None:
        cb = QGuiApplication.clipboard()
        if cb is not None:
            cb.setText(code)

        button.setText("Copied")
        button.setDisabled(True)
        QTimer.singleShot(900, lambda: self._reset_copy_button(button))

    def _reset_copy_button(self, button: QPushButton) -> None:
        try:
            button.setText("Copy")
            button.setDisabled(False)
        except RuntimeError:
            return

    def _split_text_and_code_blocks(self, text: str) -> list[tuple[str, str]]:
        """
        Splits content by triple-backtick fenced blocks.

        Returns list of:
          ("text", "...") or ("code", "...")
        """
        lines = text.splitlines()
        segments: list[tuple[str, str]] = []

        in_code = False
        text_buf: list[str] = []
        code_buf: list[str] = []

        for line in lines:
            if line.strip().startswith("```"):
                if in_code:
                    segments.append(("code", "\n".join(code_buf)))
                    code_buf.clear()
                    in_code = False
                else:
                    if text_buf:
                        segments.append(("text", "\n".join(text_buf)))
                        text_buf.clear()
                    in_code = True
                continue

            if in_code:
                code_buf.append(line)
            else:
                text_buf.append(line)

        if in_code:
            segments.append(("code", "\n".join(code_buf)))
        elif text_buf:
            segments.append(("text", "\n".join(text_buf)))

        return segments