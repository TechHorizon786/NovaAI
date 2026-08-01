from __future__ import annotations

from PySide6.QtCore import QRegularExpression, QTimer, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextOption,
)
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class AutoHeightMarkdownView(QTextBrowser):
    """
    Read-only markdown renderer with auto-height (no scrollbars).
    Edge-case polish:
      - last element bottom gap fix
      - long unbroken text wrap
      - reliable height sync on resize/reflow
      - wheel event passthrough (parent scroll)
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName("BubbleMarkdown")
        self.setReadOnly(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setUndoRedoEnabled(False)
        self.setFocusPolicy(Qt.NoFocus)

        # No internal scrollbars (height auto-adjust)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Make sure long tokens wrap instead of forcing horizontal overflow
        self.setWordWrapMode(QTextOption.WrapAnywhere)

        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
        )

        self.document().setDocumentMargin(0)

        # Font polish
        f = QFont("Segoe UI")
        f.setPointSize(10)
        self.setFont(f)

        # Widget-level styling
        self.setStyleSheet("""
        QTextBrowser#BubbleMarkdown{
            background:transparent;
            border:none;
            padding:0px;
            margin:0px;
            color:#E5E7EB;
            selection-background-color:#334155;
        }
        """)

        # Document CSS (typography + edge-case polish)
        self.document().setDefaultStyleSheet("""
        * {
            font-family: "Segoe UI";
            font-size: 14px;
            line-height: 1.45;
            color: #E5E7EB;
        }

        p { margin: 0 0 8px 0; }
        ul, ol { margin: 0 0 8px 18px; padding: 0; }
        li { margin: 0 0 4px 0; }

        h1, h2, h3 {
            font-weight: 700;
            margin: 8px 0 6px 0;
        }
        h1 { font-size: 18px; }
        h2 { font-size: 16px; }
        h3 { font-size: 15px; }

        a { color: #A78BFA; text-decoration: none; }
        a:hover { text-decoration: underline; }

        code {
            background: #111827;
            padding: 1px 5px;
            border-radius: 6px;
            color: #E2E8F0;
            font-family: Consolas, "Cascadia Mono", "Courier New";
            font-size: 13px;
        }

        /* Handle non-fenced markdown code blocks (indented) gracefully */
        pre {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px;
            margin: 0 0 8px 0;
            white-space: pre-wrap; /* avoid horizontal overflow */
            word-wrap: break-word;
        }
        pre code{
            background: transparent;
            padding: 0;
            border-radius: 0;
        }

        blockquote {
            margin: 0 0 8px 0;
            padding: 0 0 0 10px;
            border-left: 3px solid #334155;
            color: #CBD5E1;
        }

        hr {
            border: none;
            height: 1px;
            background: #334155;
            margin: 10px 0;
        }

        /* Remove extra bottom gap */
        p:last-child,
        ul:last-child,
        ol:last-child,
        pre:last-child,
        blockquote:last-child {
            margin-bottom: 0;
        }
        li:last-child { margin-bottom: 0; }
        """)

        # Auto-height updates when layout changes
        layout = self.document().documentLayout()
        layout.documentSizeChanged.connect(self._sync_height_to_document)

    def set_markdown_text(self, md: str) -> None:
        self.setMarkdown((md or "").strip())
        self._sync_height_to_document()

    def wheelEvent(self, event) -> None:
        # Let parent scroll area handle scrolling
        event.ignore()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_height_to_document()

    def _sync_height_to_document(self, *_args) -> None:
        # Ensure document width matches current viewport width (reflow then correct height)
        vp = self.viewport()
        if vp is not None:
            self.document().setTextWidth(max(1.0, float(vp.width())))

        size = self.document().size()
        h = int(size.height()) + 2  # small padding to avoid clipping
        if h < 1:
            h = 1
        self.setFixedHeight(h)


class BasicCodeHighlighter(QSyntaxHighlighter):
    """
    Lightweight syntax highlighting (no external deps).
    Supports: python / js / json (basic) + generic strings/numbers/comments.
    """

    def __init__(self, document, language: str | None = None) -> None:
        super().__init__(document)
        self._language = (language or "").strip().lower()

        self._fmt_keyword = self._make_format("#A78BFA", bold=True)   # purple
        self._fmt_builtin = self._make_format("#60A5FA")              # blue
        self._fmt_string = self._make_format("#34D399")               # green
        self._fmt_number = self._make_format("#FBBF24")               # amber
        self._fmt_comment = self._make_format("#94A3B8", italic=True) # slate
        self._fmt_def = self._make_format("#F472B6", bold=True)       # pink

        self._common_rules: list[tuple[QRegularExpression, QTextCharFormat]] = [
            (QRegularExpression(r'"([^"\\]|\\.)*"'), self._fmt_string),
            (QRegularExpression(r"'([^'\\]|\\.)*'"), self._fmt_string),
            (QRegularExpression(r"\b\d+(\.\d+)?\b"), self._fmt_number),
        ]

        self._python_rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._js_rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._json_rules: list[tuple[QRegularExpression, QTextCharFormat]] = []

        py_keywords = [
            "False", "None", "True", "and", "as", "assert", "async", "await", "break",
            "class", "continue", "def", "del", "elif", "else", "except", "finally",
            "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
            "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
        ]
        py_builtins = [
            "print", "len", "range", "str", "int", "float", "dict", "list", "set",
            "tuple", "open", "enumerate", "zip", "map", "filter", "sum", "min", "max",
            "any", "all", "isinstance", "type", "super",
        ]

        js_keywords = [
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "finally", "for",
            "function", "if", "import", "in", "instanceof", "let", "new", "return",
            "super", "switch", "this", "throw", "try", "typeof", "var", "void", "while",
            "with", "yield", "await", "async",
        ]
        js_builtins = [
            "console", "log", "JSON", "Math", "Date", "Promise", "Set", "Map",
            "Array", "Object", "String", "Number", "Boolean",
        ]

        json_keywords = ["true", "false", "null"]

        self._python_rules.extend(
            [(QRegularExpression(rf"\b{k}\b"), self._fmt_keyword) for k in py_keywords]
        )
        self._python_rules.extend(
            [(QRegularExpression(rf"\b{k}\b"), self._fmt_builtin) for k in py_builtins]
        )
        self._python_rules.extend(
            [(QRegularExpression(r"\bdef\s+([A-Za-z_]\w*)"), self._fmt_def)]
        )
        self._python_rules.extend([(QRegularExpression(r"#.*$"), self._fmt_comment)])

        self._js_rules.extend(
            [(QRegularExpression(rf"\b{k}\b"), self._fmt_keyword) for k in js_keywords]
        )
        self._js_rules.extend(
            [(QRegularExpression(rf"\b{k}\b"), self._fmt_builtin) for k in js_builtins]
        )
        self._js_rules.extend(
            [(QRegularExpression(r"\bfunction\s+([A-Za-z_]\w*)"), self._fmt_def)]
        )
        self._js_rules.extend([(QRegularExpression(r"//.*$"), self._fmt_comment)])

        self._json_rules.extend(
            [(QRegularExpression(rf"\b{k}\b"), self._fmt_keyword) for k in json_keywords]
        )
        self._json_rules.extend(
            [(QRegularExpression(r'"([^"\\]|\\.)*"\s*:'), self._fmt_def)]
        )

    def _make_format(
        self, color_hex: str, *, bold: bool = False, italic: bool = False
    ) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))
        if bold:
            fmt.setFontWeight(QFont.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def highlightBlock(self, text: str) -> None:
        for rx, fmt in self._common_rules:
            it = rx.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)

        lang = self._language
        rules: list[tuple[QRegularExpression, QTextCharFormat]] = []

        if lang in ("py", "python"):
            rules = self._python_rules
        elif lang in ("js", "javascript", "ts", "typescript"):
            rules = self._js_rules
        elif lang in ("json",):
            rules = self._json_rules

        for rx, fmt in rules:
            it = rx.globalMatch(text)
            while it.hasNext():
                m = it.next()
                if m.lastCapturedIndex() >= 1 and m.captured(1):
                    start = m.capturedStart(1)
                    length = len(m.captured(1))
                else:
                    start = m.capturedStart()
                    length = m.capturedLength()
                self.setFormat(start, length, fmt)


class ChatBubble(QFrame):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    CODE_BLOCK_MAX_HEIGHT_PX = 300

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

        self._content_widgets: list[QWidget] = []

        self.set_text(text)

    def set_bubble_max_width(self, max_width: int) -> None:
        self.setMaximumWidth(max_width)

    def set_text(self, text: str) -> None:
        self._clear_content()

        if self._role == self.ROLE_ASSISTANT and "```" in text:
            segments = self._split_text_and_code_blocks(text)
            for seg_type, seg_text, seg_lang in segments:
                if seg_type == "text" and not seg_text.strip():
                    continue

                if seg_type == "code":
                    self._layout.addWidget(self._create_code_block(seg_text, seg_lang))
                else:
                    self._layout.addWidget(self._create_text_widget(seg_text))
        else:
            self._layout.addWidget(self._create_text_widget(text))

        self.adjustSize()

    def _clear_content(self) -> None:
        for w in self._content_widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self._content_widgets.clear()

    def _create_text_widget(self, text: str) -> QWidget:
        if self._role == self.ROLE_ASSISTANT:
            view = AutoHeightMarkdownView()
            view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            view.set_markdown_text(text)

            self._content_widgets.append(view)
            return view

        label = QLabel()
        label.setObjectName("BubbleText")
        label.setWordWrap(True)
        label.setTextFormat(Qt.PlainText)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        label.setText(text)
        label.adjustSize()

        self._content_widgets.append(label)
        return label

    def _create_code_block(self, code: str, language: str | None) -> QFrame:
        frame = QFrame()
        frame.setObjectName("CodeBlockFrame")
        frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

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
        QPlainTextEdit#CodeEditor{
            background:transparent;
            border:none;
            color:#E2E8F0;
            selection-background-color:#334155;
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

        editor = QPlainTextEdit()
        editor.setObjectName("CodeEditor")
        editor.setReadOnly(True)
        editor.setUndoRedoEnabled(False)
        editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        editor.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        editor.setFrameShape(QFrame.NoFrame)
        editor.document().setDocumentMargin(0)
        editor.setPlainText(code)

        BasicCodeHighlighter(editor.document(), language=language)

        metrics = QFontMetrics(editor.font())
        line_h = metrics.lineSpacing()
        line_count = max(1, code.count("\n") + 1)
        content_h = (line_count * line_h) + 14
        visible_h = min(content_h, self.CODE_BLOCK_MAX_HEIGHT_PX)
        editor.setFixedHeight(visible_h)

        layout.addWidget(editor)

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

    def _split_text_and_code_blocks(
        self, text: str
    ) -> list[tuple[str, str, str | None]]:
        """
        Splits content by triple-backtick fenced blocks.

        Supports optional language tag:
          ```python
          ...
          ```

        Returns:
          ("text", "...", None) or ("code", "...", "python")
        """
        lines = text.splitlines()
        segments: list[tuple[str, str, str | None]] = []

        in_code = False
        current_lang: str | None = None
        text_buf: list[str] = []
        code_buf: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                fence_lang = stripped[3:].strip() or None

                if in_code:
                    segments.append(("code", "\n".join(code_buf), current_lang))
                    code_buf.clear()
                    in_code = False
                    current_lang = None
                else:
                    if text_buf:
                        segments.append(("text", "\n".join(text_buf), None))
                        text_buf.clear()
                    in_code = True
                    current_lang = fence_lang
                continue

            if in_code:
                code_buf.append(line)
            else:
                text_buf.append(line)

        if in_code:
            segments.append(("code", "\n".join(code_buf), current_lang))
        elif text_buf:
            segments.append(("text", "\n".join(text_buf), None))

        return segments