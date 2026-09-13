from PySide6.QtWidgets import QMenu, QStyleFactory
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt


class NewMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Neu")
        self.setObjectName("new_menu")

        self.file_action = QAction("Datei", self)
        self.directory_action = QAction("Ordner", self)

        self.addAction(self.file_action)
        self.addAction(self.directory_action)
