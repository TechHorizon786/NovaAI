"""Main window for the NOVA AI application."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core import ChatManager
from ui.workers.voice_worker import VoiceWorker
from ui.widgets.chat_area import ChatArea
from ui.widgets.settings_page import SettingsPage
from ui.widgets.sidebar import Sidebar
from ui.widgets.voice_page import VoicePage


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

        self._voice_thread: QThread | None = None
        self._voice_worker: VoiceWorker | None = None
        self._current_page_key: str = "chat"

        self._page_map: dict[str, int] = {}

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

        QToolTip{
            background:#111827;
            color:#E5E7EB;
            border:1px solid #1F2937;
            padding:6px 8px;
            border-radius:10px;
        }

        /* Sidebar */
        QFrame#Sidebar{
            background:#111827;
            border-radius:18px;
            border:1px solid #0F172A;
        }

        QLabel#SidebarTitle{
            font-size:18px;
            font-weight:800;
            color:white;
            background:transparent;
        }

        QLabel#SidebarSubtitle{
            color:#94A3B8;
            font-size:12px;
            background:transparent;
        }

        QLabel#SidebarHint{
            color:#94A3B8;
            font-size:12px;
            background:transparent;
        }

        QPushButton#SidebarNavButton{
            background:transparent;
            color:#E5E7EB;
            border:none;
            border-radius:12px;
            padding:12px 12px;
            text-align:left;
            font-weight:600;
        }

        QPushButton#SidebarNavButton:hover{
            background:#1F2937;
        }

        QPushButton#SidebarNavButton[selected="true"]{
            background:#6D5DF6;
            color:white;
            font-weight:800;
        }

        /* Top bar */
        QFrame#TopBar{
            background:#111827;
            border-radius:18px;
            border:1px solid #0F172A;
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

        /* Chat */
        QFrame#ChatFrame{
            background:#111827;
            border-radius:22px;
            border:1px solid #0F172A;
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

        /* Scrollbars (global) */
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

        QScrollBar:horizontal{
            background:transparent;
            height:10px;
            margin:0px 10px 6px 10px;
        }

        QScrollBar::handle:horizontal{
            background:#1F2937;
            border-radius:5px;
            min-width:30px;
        }

        QScrollBar::handle:horizontal:hover{
            background:#334155;
        }

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal{
            width:0px;
        }

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal{
            background:transparent;
        }

        /* Bubbles */
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

        /* Typing indicator */
        QFrame#TypingIndicator{
            background:#1F2937;
            border-radius:18px;
        }

        QLabel#TypingText{
            color:#E5E7EB;
            font-size:15px;
            background:transparent;
        }

        /* Input */
        QFrame#InputFrame{
            background:#111827;
            border-radius:20px;
            border:1px solid #0F172A;
        }

        QLineEdit{
            border:none;
            background:transparent;
            padding:14px;
            font-size:15px;
            color:white;
            selection-background-color:#334155;
        }

        QLineEdit:disabled{
            color:#94A3B8;
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

        /* Placeholder pages */
        QFrame#PlaceholderPage{
            background:#111827;
            border-radius:22px;
            border:1px solid #0F172A;
        }

        QLabel#PlaceholderTitle{
            font-size:18px;
            font-weight:800;
            background:transparent;
            color:white;
        }

        QLabel#PlaceholderText{
            font-size:13px;
            background:transparent;
            color:#94A3B8;
        }

        /* Shared controls */
        QComboBox#SettingsControl,
        QLineEdit#SettingsControl{
            background:#0B1120;
            border:1px solid #1F2937;
            border-radius:12px;
            padding:10px 10px;
            color:#E5E7EB;
            min-height:18px;
        }

        QComboBox#SettingsControl{
            padding-right:28px;
        }

        QComboBox#SettingsControl::drop-down{
            border:none;
            width:28px;
        }

        QComboBox#SettingsControl QAbstractItemView{
            background:#0B1120;
            color:#E5E7EB;
            border:1px solid #1F2937;
            selection-background-color:#6D5DF6;
            selection-color:white;
            outline:0;
            padding:6px;
        }

        QComboBox#SettingsControl:disabled,
        QLineEdit#SettingsControl:disabled{
            background:#0B1120;
            border:1px solid #111827;
            color:#64748B;
        }

        QCheckBox#SettingsCheck{
            spacing:10px;
            color:#E5E7EB;
        }

        QCheckBox#SettingsCheck::indicator{
            width:18px;
            height:18px;
            border-radius:6px;
            border:1px solid #334155;
            background:#0B1120;
        }

        QCheckBox#SettingsCheck::indicator:checked{
            background:#6D5DF6;
            border:1px solid #6D5DF6;
        }

        QSlider#SettingsSlider::groove:horizontal{
            height:8px;
            background:#0B1120;
            border:1px solid #1F2937;
            border-radius:4px;
        }

        QSlider#SettingsSlider::sub-page:horizontal{
            background:#6D5DF6;
            border-radius:4px;
        }

        QSlider#SettingsSlider::handle:horizontal{
            width:18px;
            margin:-6px 0;
            border-radius:9px;
            background:#E5E7EB;
        }

        QPushButton#SettingsSecondaryButton{
            background:#1F2937;
            color:#E5E7EB;
            border:none;
            border-radius:12px;
            padding:10px 14px;
            font-weight:700;
        }

        QPushButton#SettingsSecondaryButton:hover{
            background:#334155;
        }

        QPushButton#SettingsSecondaryButton:disabled{
            background:#0B1220;
            color:#64748B;
        }

        /* Voice MVP */
        QLabel#VoiceStatusPill{
            background:#0B1120;
            border:1px solid #1F2937;
            border-radius:10px;
            padding:6px 10px;
            color:#94A3B8;
        }

        QLabel#VoicePartialText{
            color:#CBD5E1;
            background:transparent;
        }

        QPlainTextEdit#VoiceTranscript{
            background:#0B1120;
            border:1px solid #1F2937;
            border-radius:12px;
            padding:12px;
            color:#E5E7EB;
            selection-background-color:#334155;
        }

        QPushButton#VoiceStopButton{
            background:#EF4444;
            color:white;
            border:none;
            border-radius:14px;
            padding:12px 22px;
            font-weight:800;
        }

        QPushButton#VoiceStopButton:hover{
            background:#F87171;
        }

        QPushButton#VoiceStopButton:pressed{
            background:#DC2626;
        }
        """)

        central_widget = QWidget()
        central_widget.setMinimumSize(0, 0)
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(20)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_selected.connect(self._on_sidebar_page_selected)
        root_layout.addWidget(self.sidebar)

        # Right Area
        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")

        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(22, 18, 22, 18)

        self._title_label = QLabel("NOVA AI")
        self._title_label.setObjectName("Title")

        self._subtitle_label = QLabel("Chat")
        self._subtitle_label.setObjectName("Subtitle")

        top_layout.addWidget(self._title_label)
        top_layout.addWidget(self._subtitle_label)

        right_layout.addWidget(top_bar)

        # Pages
        self._pages = QStackedWidget()
        self._pages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Chat Page
        chat_page = QWidget()
        chat_page_layout = QVBoxLayout(chat_page)
        chat_page_layout.setContentsMargins(0, 0, 0, 0)
        chat_page_layout.setSpacing(18)

        chat_frame = QFrame()
        chat_frame.setObjectName("ChatFrame")

        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_area = ChatArea()
        chat_layout.addWidget(self.chat_area)

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

        chat_page_layout.addWidget(chat_frame, 1)
        chat_page_layout.addWidget(input_frame)

        # Other pages
        memory_page = self._make_placeholder_page(
            title="Memory",
            text="The memory system UI will appear here. (Planned)",
        )
        history_page = self._make_placeholder_page(
            title="History",
            text="The conversation history UI will appear here. (Planned)",
        )

        self.voice_page = VoicePage()
        self.voice_page.start_listening_requested.connect(self._start_voice_listening)
        self.voice_page.stop_listening_requested.connect(self._stop_voice_listening)
        self.voice_page.use_transcript_requested.connect(self._use_voice_transcript)

        settings_page = SettingsPage()

        self._page_map = {
            "chat": self._pages.addWidget(chat_page),
            "memory": self._pages.addWidget(memory_page),
            "voice": self._pages.addWidget(self.voice_page),
            "history": self._pages.addWidget(history_page),
            "settings": self._pages.addWidget(settings_page),
        }

        right_layout.addWidget(self._pages, 1)
        root_layout.addLayout(right_layout)

        # Signals (chat only)
        self.send_button.clicked.connect(self.send_message)
        self.message_box.returnPressed.connect(self.send_message)

        # Default page
        self._on_sidebar_page_selected("chat")

    def _make_placeholder_page(self, *, title: str, text: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("PlaceholderPage")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        t = QLabel(title)
        t.setObjectName("PlaceholderTitle")

        d = QLabel(text)
        d.setObjectName("PlaceholderText")
        d.setWordWrap(True)

        layout.addWidget(t)
        layout.addWidget(d)
        layout.addStretch(1)
        return frame

    def _on_sidebar_page_selected(self, key: str) -> None:
        # If leaving Voice page, stop listening
        if self._current_page_key == "voice" and key != "voice":
            self._stop_voice_listening()

        self._current_page_key = key

        idx = self._page_map.get(key)
        if idx is None:
            return

        self._pages.setCurrentIndex(idx)

        subtitles = {
            "chat": "Chat",
            "memory": "Memory",
            "voice": "Voice",
            "history": "History",
            "settings": "Settings",
        }
        self._subtitle_label.setText(subtitles.get(key, "NOVA"))

        if key == "chat" and not self._busy:
            self.message_box.setFocus()

    # ---------------- Voice wiring (UI <-> worker) ----------------

    def _start_voice_listening(self) -> None:
        if self._voice_thread is not None:
            return  # already running

        lang = self.voice_page.selected_language_key()

        thread = QThread(self)
        worker = VoiceWorker(language=lang)  # picks VOSK_MODEL_PATH_* based on language
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.started.connect(lambda: self.voice_page.set_listening(True))
        worker.partial.connect(self.voice_page.set_partial_text)
        worker.final.connect(self.voice_page.add_final_text)
        worker.failed.connect(self.voice_page.show_error)

        worker.stopped.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_voice_thread)

        self._voice_thread = thread
        self._voice_worker = worker
        thread.start()

    def _stop_voice_listening(self) -> None:
        if self._voice_worker is None:
            return
        self._voice_worker.stop()

    def _clear_voice_thread(self) -> None:
        self._voice_thread = None
        self._voice_worker = None
        self.voice_page.set_listening(False)

    def _use_voice_transcript(self, text: str, auto_send: bool) -> None:
        # jump to chat
        self.sidebar.set_selected("chat")
        self.message_box.setText(text)
        self.message_box.setFocus()

        if auto_send and not self._busy:
            self.send_message()

    # ---------------- Chat ----------------

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

        self.chat_area.show_typing_indicator()
        self.chat_area.scroll_to_bottom()

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

    def _on_response_ready(self, response: str) -> None:
        self.chat_area.hide_typing_indicator()

        final_text = response.strip() or "No response received."
        self.chat_area.add_message(role="assistant", text=final_text)

        self.chat_area.scroll_to_bottom()
        self._set_busy(False)

    def _on_response_failed(self, error: str) -> None:
        self.chat_area.hide_typing_indicator()

        self.chat_area.add_message(
            role="assistant",
            text="Sorry, I couldn't generate a response. Please try again.",
        )

        self.chat_area.scroll_to_bottom()
        self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.send_button.setDisabled(busy)
        self.message_box.setDisabled(busy)
        if not busy:
            self.message_box.setFocus()

    def closeEvent(self, event) -> None:
        self._stop_voice_listening()
        super().closeEvent(event)