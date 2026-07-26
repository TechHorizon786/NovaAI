"""Main window for the NOVA AI application."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("NOVA AI")
        self.resize(1200, 750)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the main user interface."""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Sidebar
        sidebar = QListWidget()
        sidebar.setFixedWidth(220)
        sidebar.addItems([
            "💬 Chat",
            "🧠 Memory",
            "🎤 Voice",
            "⚙️ Settings",
        ])

        # Right Side
        right_layout = QVBoxLayout()

        title = QLabel("NOVA AI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size:24px;font-weight:bold;padding:10px;"
        )

        chat_area = QTextEdit()
        chat_area.setReadOnly(True)
        chat_area.setPlaceholderText(
            "AI conversation will appear here..."
        )

        input_layout = QHBoxLayout()

        message_box = QLineEdit()
        message_box.setPlaceholderText("Type your message...")

        send_button = QPushButton("Send")

        input_layout.addWidget(message_box)
        input_layout.addWidget(send_button)

        right_layout.addWidget(title)
        right_layout.addWidget(chat_area)
        right_layout.addLayout(input_layout)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(right_layout)