import sys
from PySide6.QtWidgets import QApplication

from src.app_window import HandwritingWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HandwritingWindow()
    window.show()
    sys.exit(app.exec())