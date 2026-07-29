from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QRect

class MotorArc(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(36, 20)
        self._value = 0.0  # 0.0 – 1.0

    def set_value(self, v: float):
        self._value = max(0.0, min(1.0, abs(v) / 100))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRect(2, 2, 32, 32)
        pen  = QPen(QColor("#2a2a2a"), 3)
        p.setPen(pen)
        p.drawArc(rect, 0 * 16, 180 * 16)
        pen.setColor(QColor("#185FA5"))
        p.setPen(pen)
        p.drawArc(rect, 0 * 16, int(180 * self._value) * 16)


class MotorWidget(QWidget):
    PORTS = ["A", "B", "C", "D"]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        grid = QGridLayout()
        grid.setSpacing(6)

        self._arcs   = {}
        self._labels = {}

        for i, port in enumerate(self.PORTS):
            lbl_port  = QLabel(port)
            arc       = MotorArc()
            lbl_val   = QLabel("—")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)

            self._arcs[port]   = arc
            self._labels[port] = lbl_val

            grid.addWidget(lbl_port, i, 0)
            grid.addWidget(arc,      i, 1)
            grid.addWidget(lbl_val,  i, 2)

        layout.addLayout(grid)
        layout.addStretch()

    def update_motor(self, port: str, speed: int):
        if port in self._arcs:
            self._arcs[port].set_value(speed)
            self._labels[port].setText(
                f"{speed}%" if speed != 0 else "—"
            )