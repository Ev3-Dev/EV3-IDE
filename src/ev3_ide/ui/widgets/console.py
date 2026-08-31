from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QFontDatabase
from PySide6.QtCore import QTimer
from ev3_ide.core.resources import resource_path


class Console(QPlainTextEdit):
    _font_id = None
    _font_family = None

    def __init__(self):
        super().__init__()
        self.setObjectName("console")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)
        self.setFont(self.create_font_from_ttf(resource_path("ui/fonts/IdeMonoV3.ttf")))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

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

    def append_line(self, text: str, kind: str = "output"):
        colors = {
            "output":  "#ffffff",
            "success": "#639922",
            "error":   "#e24b4a",
            "info":    "#185FA5",
        }
        color  = colors.get(kind, "#ffffff")
        fmt    = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text + "\n", fmt)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

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