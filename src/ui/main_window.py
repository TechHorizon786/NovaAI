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

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlaceholderText(
            "AI conversation will appear here..."
        )

        input_layout = QHBoxLayout()

        self.message_box = QLineEdit()
        self.message_box.setPlaceholderText("Type your message...")

        self.send_button = QPushButton("Send")

        input_layout.addWidget(self.message_box)
        input_layout.addWidget(self.send_button)

        right_layout.addWidget(title)
        right_layout.addWidget(self.chat_area)
        right_layout.addLayout(input_layout)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(right_layout)

        # Signals
        self.send_button.clicked.connect(self.send_message)
        self.message_box.returnPressed.connect(self.send_message)

    def send_message(self) -> None:
        """Handle sending a chat message."""

        message = self.message_box.text().strip()

        if not message:
            return

        self.chat_area.append(f"<b>You:</b> {message}")
        self.chat_area.append(
            "<b>NOVA:</b> AI integration coming soon..."
        )
        self.chat_area.append("")

        self.message_box.clear()