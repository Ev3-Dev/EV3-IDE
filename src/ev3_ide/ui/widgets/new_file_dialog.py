from PySide6.QtWidgets import QMenu, QStyleFactory
from PySide6.QtGui import QAction, QIcon


class NewMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Neu")
        self.setObjectName("new_menu")

        self.file_action = QAction("📄 File", self)

        self.directory_action = QAction("📁 Directory", self)

        self.addAction(self.file_action)
        self.addAction(self.directory_action)
