from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Signal

class FilesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("files_widget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content = QWidget()
        self.file_layout = QVBoxLayout(self.content)

        self.scroll_area.setWidget(self.content)

        layout.addWidget(self.scroll_area)

    def update_directory(self, message):
        print("Directory updated:", message)
        entries = message.get("entries", [])
        # Alte Einträge entfernen
        while self.file_layout.count():
            item = self.file_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Neue Einträge hinzufügen
        for entry in entries:
            if entry["type"] == "file":
                file_item = FileItem(entry["name"], entry["type"], entry["executable"])
            else:
                file_item = FileItem(entry["name"], entry["type"], False)
            self.file_layout.addWidget(file_item)

        self.file_layout.addStretch()


class FileItem(QWidget):
    clicked = Signal()

    def __init__(self, name, item_type, executable, parent=None):
        super().__init__(parent)

        self.name = name
        self.item_type = item_type
        self.executable = executable

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)

        self.icon = QLabel("📁" if item_type == "directory" else "📄")
        self.name_label = QLabel(name + " , " + ("Yes" if self.executable else "No"))

        layout.addWidget(self.icon)
        layout.addWidget(self.name_label)
        layout.addStretch()