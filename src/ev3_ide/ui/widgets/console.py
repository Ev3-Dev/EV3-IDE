from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QFontDatabase
from ev3_ide.core.resources import resource_path


class Console(QPlainTextEdit):
    _font_id = None
    _font_family = None

    def __init__(self):
        super().__init__()
        self.setObjectName("console")
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)
        self.setFont(self.create_font_from_ttf(resource_path("ui/fonts/IdeMono.ttf")))

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