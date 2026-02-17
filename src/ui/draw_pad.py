from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QImage
from PySide6.QtWidgets import QWidget


class DrawPad(QWidget):
    def __init__(self, size=100):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents, True)

        self.img = QImage(self.size(), QImage.Format.Format_ARGB32)
        self.img.fill(Qt.GlobalColor.white)

        self._last = None
        self._drawing = False
        self._pen_width = 12
        self.setMouseTracking(True)

    def clear(self):
        self.img.fill(Qt.GlobalColor.white)
        self._last = None
        self._drawing = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.img)

    def _stroke_to(self, pos: QPointF, pressure: float = 1.0):
        if self._last is None:
            self._last = pos
            return

        pressure = max(0.1, min(1.0, float(pressure)))
        width = self._pen_width * pressure

        painter = QPainter(self.img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(
            Qt.GlobalColor.black,
            width,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.drawLine(self._last, pos)
        painter.end()

        self._last = pos
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drawing = True
            self._last = event.position()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            self._stroke_to(event.position(), pressure=1.0)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drawing = False
            self._last = None
            event.accept()

    def tabletEvent(self, event):
        event_type = event.type()

        if event_type == event.Type.TabletPress:
            self._drawing = True
            self._last = event.position()
            event.accept()
            return

        if event_type == event.Type.TabletMove and self._drawing:
            self._stroke_to(event.position(), pressure=event.pressure())
            event.accept()
            return

        if event_type in (event.Type.TabletRelease, event.Type.TabletLeaveProximity):
            self._drawing = False
            self._last = None
            event.accept()
            return

        event.ignore()