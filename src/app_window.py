import os
import tempfile

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout

from src.ocr_inference import OCRModel
from src.platform.factory import create_platform_actions
from src.ui.draw_pad import DrawPad

# deals with permission issues
import string
import random

def generate_random_string(n):
    """Generates a random string of length n containing letters and digits."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=n))

class HandwritingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("中文手写输入")
        self._set_window_icon()
        self.setObjectName("HandwritingWindow")
        self.setStyleSheet("QWidget#HandwritingWindow { background-color: #A8A8A8; }")

        self.ocr = OCRModel()
        self.platform_actions = create_platform_actions()

        file_entropy = generate_random_string(6)
        self.temp_image_path = os.path.join(tempfile.gettempdir(), f"hw_chinese_char{file_entropy}.png")

        self.pad = DrawPad(size=200)
        self.status = QLabel(
            "点击您正在输入文字的窗口，然后再点击返回此窗口。\n"
            "1）画出字符，2）按 Q 键识别笔迹，3）按数字键选择候选字。\n"
            "输入有误时可按 E 键清空画布，或使用退格删除上一个字符。"
        )

        self.candidate_buttons = []
        candidate_row = QHBoxLayout()
        for index in range(5):
            button = QPushButton(f"{index + 1}: -")
            button.setEnabled(False)
            button.clicked.connect(lambda _checked=False, i=index: self.choose_candidate(i))
            self.candidate_buttons.append(button)
            candidate_row.addWidget(button)

        self.candidates = []

        btn_estimate = QPushButton("开始笔迹推断 (Q)")
        btn_estimate.clicked.connect(self.estimate)

        btn_clear = QPushButton("清空写作画布 (E)")
        btn_clear.clicked.connect(self.erase)

        btn_backspace = QPushButton("退格")
        btn_backspace.clicked.connect(self.backspace)

        btn_newline = QPushButton("换行")
        btn_newline.clicked.connect(self.newline)

        btn_full_stop = QPushButton("。")
        btn_full_stop.clicked.connect(self.insert_full_stop)

        controls = QHBoxLayout()
        controls.addWidget(btn_estimate)
        controls.addWidget(btn_clear)
        controls.addWidget(btn_backspace)
        controls.addWidget(btn_newline)
        controls.addWidget(btn_full_stop)

        layout = QVBoxLayout(self)
        layout.addWidget(self.pad, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        layout.addLayout(candidate_row)
        layout.addLayout(controls)

        self.shortcut_estimate = QShortcut(QKeySequence("q"), self)
        self.shortcut_estimate.activated.connect(self.estimate)
        self.shortcut_erase = QShortcut(QKeySequence("e"), self)
        self.shortcut_erase.activated.connect(self.erase)
        self.shortcut_backspace = QShortcut(QKeySequence(Qt.Key.Key_Backspace), self)
        self.shortcut_backspace.activated.connect(self.backspace)
        self.shortcut_newline = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.shortcut_newline.activated.connect(self.newline)
        self.shortcut_newline_enter = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        self.shortcut_newline_enter.activated.connect(self.newline)

        for index in range(5):
            shortcut = QShortcut(QKeySequence(str(index + 1)), self)
            shortcut.activated.connect(lambda i=index: self.choose_candidate(i))

    def erase(self):
        self.pad.clear()
        self.candidates = []
        self._render_candidates()
        self.status.setText("画布已清空，请重新书写字符。")

    def estimate(self):
        saved = self.pad.img.save(self.temp_image_path)
        if not saved:
            self.status.setText("保存笔迹图像失败，无法进行识别。")
            return

        self.candidates = self.ocr.predict_ranked(self.temp_image_path, limit=5)
        self._render_candidates()

        if not self.candidates:
            self.status.setText("未检测到字符，请写得更清晰后重试。")
            return

        preview = " ".join(
            [f"{idx + 1}:{item['text']}" for idx, item in enumerate(self.candidates)]
        )
        self.status.setText(f"候选结果：{preview}")

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

    def backspace(self):
        self.platform_actions.update_last_target_app()
        success, message = self.platform_actions.backspace_and_return()
        self.status.setText(message)
        return success

    def newline(self):
        self.platform_actions.update_last_target_app()
        success, message = self.platform_actions.newline_and_return()
        self.status.setText(message)
        return success

    def insert_full_stop(self):
        self.platform_actions.update_last_target_app()
        success, message = self.platform_actions.insert_text_and_return("。")
        self.status.setText(message)
        return success

    def _set_window_icon(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_candidates = [
            os.path.join(base_dir, "assets", "icons", "app_icon.jpg"),
            os.path.join(base_dir, "icon.jpg"),
        ]

        for icon_path in icon_candidates:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
