from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Signal

class FileTree(QTreeWidget):
    file_opened = Signal(str)  # Gibt remote Pfad zurück

    def __init__(self):
        super().__init__()
        self.setObjectName("file_tree")
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.itemDoubleClicked.connect(self._on_double_click)

    def load_tree(self, tree: dict, parent_path: str = ""):
        self.clear()
        self._populate(self.invisibleRootItem(), tree, parent_path)

    def _populate(self, parent_item, tree: dict, parent_path: str):
        for name, content in tree.items():
            item = QTreeWidgetItem([name])
            full_path = f"{parent_path}/{name}"
            item.setData(0, 256, full_path)  # Pfad im Item speichern

            if isinstance(content, dict):
                item.setData(0, 257, "folder")
                self._populate(item, content, full_path)
            else:
                item.setData(0, 257, "file")

            parent_item.addChild(item)

    def _on_double_click(self, item: QTreeWidgetItem):
        if item.data(0, 257) == "file":
            self.file_opened.emit(item.data(0, 256))