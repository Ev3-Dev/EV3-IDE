from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase
from ev3_ide.core.resources import resource_path


class Terminal(QPlainTextEdit):
    _font_id = None
    _font_family = None

    command_entered = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("terminal")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(self.create_font_from_ttf(resource_path("ui/fonts/IdeMonoV3.ttf")))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

        self._prompt = "robot@ev3dev:~$ "
        self.appendPlainText(self._prompt)

        # Smoothes Scrollen
        self.friction = 0.80
        self.sensitivity = 0.01
        self.velocity = 0.0
        self.precise_value = float(self.verticalScrollBar().value())
        self.timer = QTimer(self)
        self.timer.setInterval(8)
        self.timer.timeout.connect(self.physics_tick)
        self.verticalScrollBar().valueChanged.connect(self.sync_on_manual_scroll)

    @classmethod
    def create_font_from_ttf(cls, ttf_path, size=10):
        if cls._font_family is None:
            cls._font_id = QFontDatabase.addApplicationFont(ttf_path)
            if cls._font_id == -1:
                return QFont()
            font_families = QFontDatabase.applicationFontFamilies(cls._font_id)
            if not font_families:
                return QFont()
            cls._font_family = font_families[0]
        return QFont(cls._font_family, size)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            text  = self.toPlainText()
            cmd   = text.split(self._prompt)[-1].strip()
            if cmd:
                self.command_entered.emit(cmd)
            self.appendPlainText(self._prompt)
        else:
            super().keyPressEvent(event)

    # -------- Scrollen --------
    def sync_on_manual_scroll(self, value):
        if not self.timer.isActive():
            self.precise_value = float(value)
            self.velocity = 0.0

    def wheelEvent(self, event):
        steps = event.angleDelta().y()
        self.velocity += -(steps * self.sensitivity)
        if not self.timer.isActive():
            self.timer.start()
        event.accept()

    def physics_tick(self):
        scrollbar = self.verticalScrollBar()
        self.velocity *= self.friction
        if abs(self.velocity) < 0.1:
            self.velocity = 0.0
            self.timer.stop()
            return
        self.precise_value += self.velocity
        if self.precise_value < scrollbar.minimum():
            self.precise_value = float(scrollbar.minimum())
            self.velocity = 0.0
        elif self.precise_value > scrollbar.maximum():
            self.precise_value = float(scrollbar.maximum())
            self.velocity = 0.0
        scrollbar.setValue(int(round(self.precise_value)))