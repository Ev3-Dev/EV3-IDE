from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal

class Toolbar(QWidget):
    run_clicked        = Signal()
    stop_clicked       = Signal()
    upload_clicked     = Signal()
    sync_clicked       = Signal()
    disconnect_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(48)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)

        self.btn_run      = self._button("Run",      "btn-run")
        self.btn_stop     = self._button("Stop",     "btn-stop")
        self.btn_upload   = self._button("Upload",   "btn-default")
        self.btn_sync     = self._button("Sync",     "btn-default")

        self.btn_run.clicked.connect(self.run_clicked)
        self.btn_stop.clicked.connect(self.stop_clicked)
        self.btn_upload.clicked.connect(self.upload_clicked)
        self.btn_sync.clicked.connect(self.sync_clicked)

        layout.addWidget(self.btn_run)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self._separator())
        layout.addWidget(self.btn_upload)
        layout.addWidget(self.btn_sync)
        layout.addStretch()

        # Verbindungsstatus
        self.status_dot   = QLabel("●")
        self.status_label = QLabel("Nicht verbunden")
        self.battery_label = QLabel("")

        self.status_dot.setProperty("class", "status-dot-disconnected")
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_label)
        layout.addWidget(self._separator())
        layout.addWidget(self.battery_label)

    def set_connected(self, host: str, connection_type: str):
        self.status_dot.setProperty("class", "status-dot-connected")
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)
        self.status_label.setText(f"{host}  {connection_type}")

    def set_disconnected(self):
        self.status_dot.setProperty("class", "status-dot-disconnected")
        self.status_dot.style().unpolish(self.status_dot)
        self.status_dot.style().polish(self.status_dot)
        self.status_label.setText("Nicht verbunden")

    def set_battery(self, percent: int):
        self.battery_label.setText(f"🔋 {percent}%")

    def _button(self, text: str, css_class: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", css_class)
        btn.setFixedHeight(32)
        return btn

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        return sep