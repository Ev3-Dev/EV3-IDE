from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Signal, Qt


class FilesWidget(QWidget):
    item_clicked = Signal(dict)
    item_right_clicked = Signal(dict)
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("files_widget")

        # Obere Leiste
        self.back_button = QPushButton("Back")
        self.back_button.setFixedWidth(60)
        self.back_button.setObjectName("files_back_button")
        self.back_button.clicked.connect(self.back_requested)

        # Content-Area
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("files_scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.viewport().setObjectName("files_viewport")

        self.content = QWidget()
        self.content.setObjectName("files_content")
        self.file_layout = QVBoxLayout(self.content)
        self.file_layout.setContentsMargins(0, 0, 0, 0)
        self.file_layout.setSpacing(5)

        self.scroll_area.setWidget(self.content)

        layout.addWidget(self.scroll_area)

    def get_buttons_layout_widget(self):
        return [self.back_button,]

    def update_directory(self, entries):
        # Alte Einträge entfernen
        while self.file_layout.count():
            item = self.file_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Neue Einträge hinzufügen
        for entry in entries:
            file_item = FileItem(entry["name"], entry["path"], entry["type"], entry["size"], entry["mode"], entry["modified"], entry["executable"])
            file_item.clicked.connect(self.item_clicked)
            file_item.right_clicked.connect(self.item_right_clicked)
            self.file_layout.addWidget(file_item)

        self.file_layout.addStretch()


class FileItem(QFrame):
    clicked = Signal(dict)
    right_clicked = Signal(dict)

    def __init__(self, name, path, item_type, size, mode, modified, executable, parent=None):
        super().__init__(parent)

        self.setObjectName("file_item")
        self.setFixedHeight(30)

        self.name = name
        self.path = path
        self.item_type = item_type
        self.size = size
        self.mode = mode
        self.modified = modified
        self.executable = executable

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)

        self.icon = QLabel("📁" if self.item_type == "directory" else "📄")

        self.name_label = QLabel(name)
        self.name_label.setObjectName("file_item_name")
        font = QFont("Segoe UI", 10)
        # if self.executable and self.item_type != "directory":
        #     font.setBold(True)
        self.name_label.setFont(font)

        layout.addWidget(self.icon)
        layout.addWidget(self.name_label)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit({"name": self.name, "path": self.path, "type": self.item_type})
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit({"name": self.name, "path": self.path, "type": self.item_type, "executable": self.executable})
        super().mousePressEvent(event)