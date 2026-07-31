from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout


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
                # avoid useless empty text widgets
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
        QLabel#CodeBlockText{
            background:transparent;
            color:#E2E8F0;
            font-family:Consolas, "Cascadia Mono", "Courier New";
            font-size:13px;
        }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(0)

        label = QLabel(code)
        label.setObjectName("CodeBlockText")
        label.setWordWrap(True)  # safe wrapping (no horizontal scroll yet)
        label.setTextFormat(Qt.PlainText)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        layout.addWidget(label)

        self._content_widgets.append(frame)
        return frame

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
                    # close code block
                    segments.append(("code", "\n".join(code_buf)))
                    code_buf.clear()
                    in_code = False
                else:
                    # open code block (flush pending text)
                    if text_buf:
                        segments.append(("text", "\n".join(text_buf)))
                        text_buf.clear()
                    in_code = True
                continue

            if in_code:
                code_buf.append(line)
            else:
                text_buf.append(line)

        # flush remaining
        if in_code:
            segments.append(("code", "\n".join(code_buf)))
        elif text_buf:
            segments.append(("text", "\n".join(text_buf)))

        return segments