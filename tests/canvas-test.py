import sys
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QImage, QColor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout


class DrawPad(QWidget):
    def __init__(self, size=100):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_StaticContents, True)

        self.img = QImage(self.size(), QImage.Format_ARGB32)
        self.img.fill(Qt.white)

        self._last = None
        self._drawing = False
        self._pen_width = 1  # base thickness for handwriting

        # Enables tablet events on many platforms
        self.setMouseTracking(True)

    def clear(self):
        self.img.fill(Qt.white)
        self._last = None
        self._drawing = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawImage(0, 0, self.img)

    def _stroke_to(self, pos: QPointF, pressure: float = 1.0):
        if self._last is None:
            self._last = pos
            return

        # Pressure usually 0..1 on supported devices; clamp just in case
        pressure = max(0.1, min(1.0, float(pressure)))

        width = self._pen_width * pressure

        painter = QPainter(self.img)
        painter.setRenderHint(QPainter.Antialiasing, True)

        pen = QPen(Qt.black, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        painter.drawLine(self._last, pos)
        painter.end()

        self._last = pos
        self.update()

    # ---- Mouse fallback (works with trackpad/mouse; many pens emulate mouse) ----
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drawing = True
            self._last = e.position()
            e.accept()

    def mouseMoveEvent(self, e):
        if self._drawing and (e.buttons() & Qt.LeftButton):
            self._stroke_to(e.position(), pressure=1.0)
            e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drawing = False
            self._last = None
            e.accept()

    # ---- True tablet/stylus events (pressure, etc.) when supported ----
    def tabletEvent(self, e):
        t = e.type()

        if t == e.Type.TabletPress:
            self._drawing = True
            self._last = e.position()
            e.accept()
            return

        if t == e.Type.TabletMove and self._drawing:
            self._stroke_to(e.position(), pressure=e.pressure())
            e.accept()
            return

        if t in (e.Type.TabletRelease, e.Type.TabletLeaveProximity):
            self._drawing = False
            self._last = None
            e.accept()
            return

        e.ignore()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Input (PySide6)")

        self.pad = DrawPad(size=100)
        self.status = QLabel("Draw a character. (Mouse or stylus)")

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.pad.clear)

        btn_save = QPushButton("Save PNG")
        btn_save.clicked.connect(self.save_png)

        row = QHBoxLayout()
        row.addWidget(btn_clear)
        row.addWidget(btn_save)

        layout = QVBoxLayout(self)
        layout.addWidget(self.pad, alignment=Qt.AlignCenter)
        layout.addWidget(self.status)
        layout.addLayout(row)

    def save_png(self):
        # Saves exactly the pad content (white background)
        ok = self.pad.img.save("char.png")
        self.status.setText("Saved char.png" if ok else "Save failed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())

