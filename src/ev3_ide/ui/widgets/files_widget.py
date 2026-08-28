from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel
from PySide6.QtCore import Signal, Qt

class FilesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("files_widget")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("files_scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.viewport().setObjectName("files_viewport")

        self.content = QWidget()
        self.content.setObjectName("files_content")
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

        self.setObjectName("file_item")
        self.setAttribute(Qt.WA_Hover, True)

        self.name = name
        self.item_type = item_type
        self.executable = executable

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)

        self.icon = QLabel("📁" if item_type == "directory" else "📄")
        self.icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.name_label = QLabel(name + " , " + ("Yes" if self.executable else "No"))
        self.name_label.setObjectName("file_item_name")
        self.name_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout.addWidget(self.icon)
        layout.addWidget(self.name_label)
        layout.addStretch()