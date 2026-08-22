from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QFontDatabase
from ev3_ide.core.resources import resource_path


class CodeEditor(QPlainTextEdit):
    _font_id = None
    _font_family = None

    def __init__(self, language=None, parent=None):
        super().__init__(parent)

        self.setObjectName("code_editor")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(self.create_font_from_ttf(resource_path("ui/fonts/IdeMono.ttf")))
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

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