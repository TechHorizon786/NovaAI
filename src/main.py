"""NOVA AI application entry point."""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow


def main() -> None:
    """Start the NOVA AI application."""

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("NOVA AI")
    window.resize(1000, 700)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    