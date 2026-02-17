import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout

from src.ocr_inference import OCRModel
from src.platform.factory import create_platform_actions
from src.ui.draw_pad import DrawPad


class HandwritingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chinese Handwriting Input")
        self.setObjectName("HandwritingWindow")
        self.setStyleSheet("QWidget#HandwritingWindow { background-color: #A8A8A8; }")

        self.ocr = OCRModel()
        self.platform_actions = create_platform_actions()
        self.temp_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "char.png")

        self.pad = DrawPad(size=200)
        self.status = QLabel("Draw a character. Press q to estimate, e to erase.")

        self.candidate_buttons = []
        candidate_row = QHBoxLayout()
        for index in range(5):
            button = QPushButton(f"{index + 1}: -")
            button.setEnabled(False)
            button.clicked.connect(lambda _checked=False, i=index: self.choose_candidate(i))
            self.candidate_buttons.append(button)
            candidate_row.addWidget(button)

        self.candidates = []

        btn_estimate = QPushButton("Estimate (q)")
        btn_estimate.clicked.connect(self.estimate)

        btn_clear = QPushButton("Erase (e)")
        btn_clear.clicked.connect(self.erase)

        controls = QHBoxLayout()
        controls.addWidget(btn_estimate)
        controls.addWidget(btn_clear)

        layout = QVBoxLayout(self)
        layout.addWidget(self.pad, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        layout.addLayout(candidate_row)
        layout.addLayout(controls)

        self.shortcut_estimate = QShortcut(QKeySequence("q"), self)
        self.shortcut_estimate.activated.connect(self.estimate)
        self.shortcut_erase = QShortcut(QKeySequence("e"), self)
        self.shortcut_erase.activated.connect(self.erase)

        for index in range(5):
            shortcut = QShortcut(QKeySequence(str(index + 1)), self)
            shortcut.activated.connect(lambda i=index: self.choose_candidate(i))

    def erase(self):
        self.pad.clear()
        self.candidates = []
        self._render_candidates()
        self.status.setText("Canvas erased. Draw a new character.")

    def estimate(self):
        saved = self.pad.img.save(self.temp_image_path)
        if not saved:
            self.status.setText("Failed to save drawing for OCR.")
            return

        self.candidates = self.ocr.predict_ranked(self.temp_image_path, limit=5)
        self._render_candidates()

        if not self.candidates:
            self.status.setText("No character detected. Try drawing more clearly.")
            return

        preview = " ".join(
            [f"{idx + 1}:{item['text']}" for idx, item in enumerate(self.candidates)]
        )
        self.status.setText(f"Candidates: {preview}")

    def _render_candidates(self):
        for index, button in enumerate(self.candidate_buttons):
            if index < len(self.candidates):
                candidate = self.candidates[index]
                text = candidate["text"]
                score = candidate["score"]
                button.setText(f"{index + 1}: {text} ({score:.2f})")
                button.setEnabled(True)
            else:
                button.setText(f"{index + 1}: -")
                button.setEnabled(False)

    def choose_candidate(self, index):
        if index >= len(self.candidates):
            return

        self.platform_actions.update_last_target_app()
        selected_char = self.candidates[index]["text"]
        success, message = self.platform_actions.insert_text_and_return(selected_char)
        self.status.setText(message)
        return success