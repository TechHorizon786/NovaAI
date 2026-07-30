"""Main window for the NOVA AI application."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core import ChatManager
from ui.widgets.chat_area import ChatArea
from ui.widgets.chat_bubble import ChatBubble


class _ResponseWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, chat_manager: ChatManager, message: str) -> None:
        super().__init__()
        self._chat_manager = chat_manager
        self._message = message

    def run(self) -> None:
        try:
            response = self._chat_manager.get_response(self._message) or ""
            self.finished.emit(response)
        except Exception as exc:  # keep UI safe
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("NOVA AI")
        self.resize(900, 600)

        self.chat_manager = ChatManager()

        self._response_thread: QThread | None = None
        self._response_worker: _ResponseWorker | None = None
        self._busy = False

        self._thinking_timer = QTimer(self)
        self._thinking_timer.setInterval(350)
        self._thinking_timer.timeout.connect(self._on_thinking_tick)
        self._thinking_step = 0
        self._thinking_bubble: ChatBubble | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the modern application layout."""

        self.setStyleSheet("""
        QMainWindow{
            background:#0B1120;
        }

        QWidget{
            background:#0B1120;
            color:white;
            font-family:Segoe UI;
            font-size:14px;
        }

        QListWidget{
            background:#111827;
            border:none;
            border-radius:18px;
            padding:12px;
            outline:none;
        }

        QListWidget::item{
            padding:14px;
            border-radius:12px;
            margin:4px 0px;
        }

        QListWidget::item:selected{
            background:#6D5DF6;
            color:white;
        }

        QListWidget::item:hover{
            background:#1F2937;
        }

        QFrame#TopBar{
            background:#111827;
            border-radius:18px;
        }

        QLabel#Title{
            font-size:24px;
            font-weight:700;
            color:white;
            background:transparent;
        }

        QLabel#Subtitle{
            color:#94A3B8;
            font-size:13px;
            background:transparent;
        }

        QFrame#ChatFrame{
            background:#111827;
            border-radius:22px;
        }

        QScrollArea#ChatScroll{
            background:transparent;
            border:none;
        }

        QWidget#ChatViewport{
            background:transparent;
        }

        QWidget#ChatContainer{
            background:transparent;
        }

        QWidget#ChatRow{
            background:transparent;
        }

        QScrollBar:vertical{
            background:transparent;
            width:10px;
            margin:10px 6px 10px 0px;
        }

        QScrollBar::handle:vertical{
            background:#1F2937;
            border-radius:5px;
            min-height:30px;
        }

        QScrollBar::handle:vertical:hover{
            background:#334155;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical{
            height:0px;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical{
            background:transparent;
        }

        QFrame#BubbleUser{
            background:#6D5DF6;
            border-radius:18px;
        }

        QFrame#BubbleNova{
            background:#1F2937;
            border-radius:18px;
        }

        QLabel#BubbleText{
            color:white;
            font-size:15px;
            background:transparent;
        }

        QFrame#InputFrame{
            background:#111827;
            border-radius:20px;
        }

        QLineEdit{
            border:none;
            background:transparent;
            padding:14px;
            font-size:15px;
            color:white;
        }

        QPushButton{
            background:#6D5DF6;
            color:white;
            border:none;
            border-radius:14px;
            padding:12px 26px;
            font-weight:bold;
        }

        QPushButton:hover{
            background:#7C6CFF;
        }

        QPushButton:pressed{
            background:#5A49E8;
        }

        QPushButton:disabled{
            background:#4B5563;
            color:#CBD5E1;
        }
        """)

        central_widget = QWidget()
        central_widget.setMinimumSize(0, 0)
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(20)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMinimumWidth(160)
        self.sidebar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.sidebar.addItems([
            "💬  Chat",
            "🧠  Memory",
            "🎤  Voice",
            "📂  History",
            "⚙️  Settings",
        ])
        root_layout.addWidget(self.sidebar)

        # Right Area
        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")

        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(22, 18, 22, 18)

        title = QLabel("NOVA AI")
        title.setObjectName("Title")

        subtitle = QLabel("Your Personal AI Assistant")
        subtitle.setObjectName("Subtitle")

        top_layout.addWidget(title)
        top_layout.addWidget(subtitle)

        right_layout.addWidget(top_bar)

        # Chat Container
        chat_frame = QFrame()
        chat_frame.setObjectName("ChatFrame")

        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_area = ChatArea()
        chat_layout.addWidget(self.chat_area)

        right_layout.addWidget(chat_frame, 1)

        # Input Area
        input_frame = QFrame()
        input_frame.setObjectName("InputFrame")

        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(12)

        self.message_box = QLineEdit()
        self.message_box.setPlaceholderText("Ask anything...")

        self.send_button = QPushButton("Send")
        self.send_button.setFixedHeight(46)
        self.send_button.setCursor(Qt.PointingHandCursor)

        input_layout.addWidget(self.message_box)
        input_layout.addWidget(self.send_button)

        right_layout.addWidget(input_frame)
        root_layout.addLayout(right_layout)

        # Signals
        self.send_button.clicked.connect(self.send_message)
        self.message_box.returnPressed.connect(self.send_message)

    def send_message(self) -> None:
        """Handle sending a chat message."""
        if self._busy:
            return

        message = self.message_box.text().strip()
        if not message:
            return

        self._set_busy(True)
        self.message_box.clear()

        self.chat_area.add_message(role="user", text=message)

        # Thinking bubble (will be updated with final response)
        self.chat_area.add_message(role="assistant", text="Generating...")
        self._thinking_bubble = self._get_last_bubble()
        self._thinking_step = 0
        self._thinking_timer.start()
        self.chat_area.scroll_to_bottom()

        # Background thread
        thread = QThread(self)
        worker = _ResponseWorker(self.chat_manager, message)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._on_response_ready)
        worker.failed.connect(self._on_response_failed)

        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)

        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        self._response_thread = thread
        self._response_worker = worker
        thread.start()

    def _get_last_bubble(self) -> ChatBubble | None:
        bubbles = self.chat_area.findChildren(ChatBubble)
        return bubbles[-1] if bubbles else None

    def _on_thinking_tick(self) -> None:
        if not self._thinking_bubble:
            return
        self._thinking_step = (self._thinking_step + 1) % 4
        dots = "." * self._thinking_step
        self._thinking_bubble.set_text(f"Generating{dots}")
        self.chat_area.scroll_to_bottom()

    def _on_response_ready(self, response: str) -> None:
        self._thinking_timer.stop()

        if self._thinking_bubble:
            final_text = response.strip() or "No response received."
            self._thinking_bubble.set_text(final_text)

        self._thinking_bubble = None
        self.chat_area.scroll_to_bottom()
        self._set_busy(False)

    def _on_response_failed(self, error: str) -> None:
        self._thinking_timer.stop()

        if self._thinking_bubble:
            self._thinking_bubble.set_text("Sorry, response generate nahi ho paya. Try again.")
        self._thinking_bubble = None

        self.chat_area.scroll_to_bottom()
        self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.send_button.setDisabled(busy)
        self.message_box.setDisabled(busy)
        if not busy:
            self.message_box.setFocus()