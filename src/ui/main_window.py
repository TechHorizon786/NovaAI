"""Main window for the NOVA AI application."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core import ChatManager


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("NOVA AI")
        self.resize(1400, 850)

        self.chat_manager = ChatManager()

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
        }

        QLabel#Subtitle{
            color:#94A3B8;
            font-size:13px;
        }

        QFrame#ChatFrame{
            background:#111827;
            border-radius:22px;
        }

        QTextEdit{
            background:transparent;
            border:none;
            padding:18px;
            color:white;
            font-size:15px;
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
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(20)

        # ==========================
        # Sidebar
        # ==========================

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)

        self.sidebar.addItems([
            "💬  Chat",
            "🧠  Memory",
            "🎤  Voice",
            "📂  History",
            "⚙️  Settings",
        ])

        root_layout.addWidget(self.sidebar)

        # ==========================
        # Right Area
        # ==========================

        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)

        # ==========================
        # Top Bar
        # ==========================

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

        # ==========================
        # Chat Container
        # ==========================

        chat_frame = QFrame()
        chat_frame.setObjectName("ChatFrame")

        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlaceholderText(
            "Start a conversation with NOVA..."
        )

        chat_layout.addWidget(self.chat_area)

        right_layout.addWidget(chat_frame, 1)

        # ==========================
        # Input Area
        # ==========================

        input_frame = QFrame()
        input_frame.setObjectName("InputFrame")

        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(12)

        self.message_box = QLineEdit()
        self.message_box.setPlaceholderText(
            "Ask anything..."
        )

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

        message = self.message_box.text().strip()

        if not message:
            return

        self.chat_area.append(f"<b>You:</b> {message}")

        response = self.chat_manager.get_response(message)

        if response:
            self.chat_area.append(f"<b>NOVA:</b> {response}")

        self.chat_area.append("")

        self.message_box.clear()