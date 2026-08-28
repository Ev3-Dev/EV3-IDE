from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QFontDatabase
from ev3_ide.core.resources import resource_path


class Terminal(QPlainTextEdit):
    _font_id = None
    _font_family = None

    command_entered = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("terminal")
        self._prompt = "robot@ev3dev:~$ "
        self.appendPlainText(self._prompt)
        self.setFont(self.create_font_from_ttf(resource_path("ui/fonts/IdeMonoV3.ttf")))

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