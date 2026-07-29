from PySide6.QtWidgets import QTabWidget, QPlainTextEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor

class Console(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setObjectName("console")
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)
        self.setFont(QFont("Monospace", 11))

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


class Terminal(QPlainTextEdit):
    command_entered = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("terminal")
        self._prompt = "robot@ev3dev:~$ "
        self.appendPlainText(self._prompt)

    def keyPressEvent(self, event):
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key.Key_Return:
            text  = self.toPlainText()
            cmd   = text.split(self._prompt)[-1].strip()
            if cmd:
                self.command_entered.emit(cmd)
            self.appendPlainText(self._prompt)
        else:
            super().keyPressEvent(event)


class BottomTabs(QTabWidget):
    command_entered = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("bottom_tabs")
        self.setDocumentMode(True)

        self.console  = Console()
        self.terminal = Terminal()
        self.terminal.command_entered.connect(self.command_entered)

        self.addTab(self.console,  "Console")
        self.addTab(self.terminal, "Terminal")