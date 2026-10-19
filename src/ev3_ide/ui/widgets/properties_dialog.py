from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QDialog, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QGridLayout
from PySide6.QtGui import QIcon
from datetime import datetime
import stat

from ev3_ide.core.resources import resource_path


class TitleBar(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.setObjectName("title_bar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("title_label")

        self.close_button = QPushButton()
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(QSize(35, 35))
        self.close_button.setIcon(QIcon(resource_path("ui/icons/window_close.svg")))
        self.close_button.setIconSize(QSize(16, 16))
        self.close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_button.clicked.connect(self._close_window)

        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.close_button)

    def _close_window(self):
        self.window().close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window_handle = self.window().windowHandle()
            if window_handle is not None:
                window_handle.startSystemMove()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        event.accept()


class PropertiesDialog(QDialog):
    def __init__(self, file_data: dict, parent=None):
        super().__init__(parent)

        self.file_data = file_data

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,True)

        self.setFixedSize(400, 290)
        self.setObjectName("properties_dialog")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = TitleBar("Properties", self)
        self.title_bar.setFixedHeight(36)

        main_layout.addWidget(self.title_bar)

        # Content area
        content = QWidget()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 18, 18, 14)
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
        close_button.setObjectName("dialog_close_button")
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)