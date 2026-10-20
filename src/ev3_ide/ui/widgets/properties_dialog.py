from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QGridLayout
from datetime import datetime
import stat
import ctypes

from ev3_ide.ui.widgets.dialog_title_bar import TitleBar


class PropertiesDialog(QDialog):
    def __init__(self, file_data: dict, parent=None):
        super().__init__(parent)

        self.file_data = file_data

        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,True)

        self.resize(400, 290)
        self.setObjectName("dialog_window")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = TitleBar("Properties", "properties", self)
        self.title_bar.setFixedHeight(36)

        main_layout.addWidget(self.title_bar)

        # Content area
        content = QWidget()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(14, 12, 14, 12)
        content_layout.setSpacing(16)

        heading = QLabel(self.file_data.get("name", "Unknown"))
        heading.setObjectName("file_name")

        content_layout.addWidget(heading)

        properties_layout = QGridLayout()
        properties_layout.setHorizontalSpacing(20)
        properties_layout.setVerticalSpacing(12)

        properties = [
            ("Type", "File" if self.file_data.get("type", "Unknown") == "file" else "Directory" if self.file_data.get("type", "Unknown") == "directory" else "Unknown"),
            ("Location", self.file_data.get("path", "Unknown")),
            ("Size", self.format_size(int(self.file_data["size"])) if self.file_data.get("size", "Unknown") != "Unknown" else "Unknown"),
            ("Permissions", self.format_permissions(int(self.file_data["mode"])) if self.file_data.get("mode", "Unknown") != "Unknown" else "Unknown"),
            ("Modified", self.format_modified(float(self.file_data["modified"])) if self.file_data.get("modified", "Unknown") != "Unknown" else "Unknown"),
            ("Executable", self.format_boolean(bool(self.file_data["executable"])) if self.file_data.get("executable", "Unknown") != "Unknown" else "Unknown"),
            ("Editable", self.format_boolean(bool(self.file_data["editable"])) if self.file_data.get("editable", "Unknown") != "Unknown" else "Unknown"),
        ]

        for row, (label_text, value_text) in enumerate(properties):
            label = QLabel(label_text)
            label.setObjectName("property_label")

            value = QLabel(str(value_text))
            value.setObjectName("property_value")
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setWordWrap(True)

            properties_layout.addWidget(label, row, 0)
            properties_layout.addWidget(value, row, 1)

        content_layout.addLayout(properties_layout)
        content_layout.addStretch()

        # Bottom button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.setObjectName("dialog_button")
        close_button.clicked.connect(self.close)

        button_layout.addWidget(close_button)
        content_layout.addLayout(button_layout)

        main_layout.addWidget(content)

    def format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        if size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        if size < 1024 ** 3:
            return f"{size / 1024 ** 2:.1f} MB"
        return f"{size / 1024 ** 3:.1f} GB"

    def format_modified(self, timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y, %H:%M")

    def format_permissions(self, mode: int) -> str:
        return stat.filemode(mode)

    def format_boolean(self, value) -> str:
        if value is None:
            return "Unknown"
        return "Yes" if value else "No"

    def nativeEvent(self, event_type, message):
        msg = ctypes.wintypes.MSG.from_address(int(message))
        if msg.message == 0x0083:
            return True, 0
        return super().nativeEvent(event_type, message)