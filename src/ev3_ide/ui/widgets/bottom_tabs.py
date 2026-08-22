from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import Signal
from ev3_ide.ui.widgets.console import Console
from ev3_ide.ui.widgets.terminal import Terminal


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