import os
import sys
import argparse

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from PySide6.QtWidgets import QApplication

from src.app_window import HandwritingWindow

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Chinese Handwriting Recognition Window for text entry")

    parser.add_argument("--version", "-v", action="store_true", help="Get the software version")

    args = parser.parse_args()

    if args.version:
        print("Version 0.1")
        sys.exit(0)
    else:
        app = QApplication(sys.argv)
        window = HandwritingWindow()
        window.show()
        sys.exit(app.exec())
