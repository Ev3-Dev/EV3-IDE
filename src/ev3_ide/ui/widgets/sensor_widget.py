from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QProgressBar
)
from PySide6.QtCore import Qt

class SensorWidget(QWidget):
    PORTS = ["S1", "S2", "S3", "S4"]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        grid = QGridLayout()
        grid.setSpacing(4)

        self._name_labels  = {}
        self._value_labels = {}
        self._bars         = {}

        for i, port in enumerate(self.PORTS):
            lbl_port = QLabel(port)
            lbl_name = QLabel("—")
            lbl_val  = QLabel("")
            bar      = QProgressBar()
            bar.setRange(0, 100)
            bar.setFixedHeight(4)
            bar.setTextVisible(False)
            bar.hide()

            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)

            self._name_labels[port]  = lbl_name
            self._value_labels[port] = lbl_val
            self._bars[port]         = bar

            grid.addWidget(lbl_port, i * 2,     0)
            grid.addWidget(lbl_name, i * 2,     1)
            grid.addWidget(lbl_val,  i * 2,     2)
            grid.addWidget(bar,      i * 2 + 1, 0, 1, 3)

        layout.addLayout(grid)
        layout.addStretch()

    def update_sensor(self, port: str, name: str,
                      value: str, bar_value: int = -1):
        if port not in self._name_labels:
            return
        self._name_labels[port].setText(name)
        self._value_labels[port].setText(value)

        bar = self._bars[port]
        if bar_value >= 0:
            bar.setValue(bar_value)
            bar.show()
        else:
            bar.hide()