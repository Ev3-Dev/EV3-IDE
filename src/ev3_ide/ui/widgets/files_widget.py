from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QPushButton, QLineEdit
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QEvent

from ev3_ide.core.resources import resource_path
from ev3_ide.ui.widgets.new_file_dialog import NewMenu


class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self.verticalScrollBar(), b"value", self)
        self.animation.setDuration(160)
        self.animation.setEasingCurve(QEasingCurve.Type.OutSine)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        scrollbar = self.verticalScrollBar()
        scroll_amount = int(delta * 2)
        target = scrollbar.value() - scroll_amount
        target = max(scrollbar.minimum(), min(target, scrollbar.maximum()))
        self.animation.stop()
        self.animation.setStartValue(scrollbar.value())
        self.animation.setEndValue(target)
        self.animation.start()
        event.accept()


class FilesWidget(QWidget):
    item_clicked = Signal(dict)
    item_right_clicked = Signal(dict)
    back_requested = Signal()
    home_requested = Signal()
    refresh_requested = Signal()
    create_file_requested = Signal(str)
    create_directory_requested = Signal(str)

    def __init__(self, parent=None, overlay_parent=None):
        super().__init__(parent)

        self.setObjectName("files_widget")

        self.is_ev3_connected = False

        # Obere Leiste
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon(resource_path("ui/icons/back.svg")))
        self.back_button.setFixedSize(30, 30)
        self.back_button.setObjectName("files_back_button")
        self.back_button.clicked.connect(self.back_requested)

        self.home_button = QPushButton()
        self.home_button.setIcon(QIcon(resource_path("ui/icons/home.svg")))
        self.home_button.setFixedSize(30, 30)
        self.home_button.setObjectName("files_home_button")
        self.home_button.clicked.connect(self.home_requested)

        self.new_menu = NewMenu(overlay_parent)
        self.new_menu.file_action.triggered.connect(self.start_create_file)
        self.new_menu.directory_action.triggered.connect(self.start_create_directory)

        self.input_type = ""
        self.input_edit = None

        self.new_button = QPushButton()
        self.new_button.setIcon(QIcon(resource_path("ui/icons/new.svg")))
        self.new_button.setFixedSize(30, 30)
        self.new_button.setObjectName("files_new_button")
        self.new_button.clicked.connect(self.show_new_menu)

        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon(resource_path("ui/icons/refresh.svg")))
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.setObjectName("files_refresh_button")
        self.refresh_button.clicked.connect(self.refresh)

        # Content-Area
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.scroll_area = SmoothScrollArea()
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

    def show_new_menu(self):
        self.new_menu.show_at(self.new_button)

    def ev3_connected(self):
        self.is_ev3_connected = True

    def ev3_disconnected(self):
        self.is_ev3_connected = False

    def finish_inline_input(self):
        name = self.input_edit.text().strip()
        if not name:
            return
        if not self.input_type:
            self.input_edit.deleteLater()
            self.input_edit = None
            return
        if self.input_type == "file":
            self.create_file_requested.emit(name)
        elif self.input_type == "directory":
            self.create_directory_requested.emit(name)
        self.input_edit.deleteLater()
        self.input_edit = None

    def cancel_inline_input(self):
        if self.input_edit is None:
            return
        self.input_edit.deleteLater()
        self.input_edit = None
        self.input_type = ""

    def start_inline_input(self, item_type, placeholder):
        if not self.is_ev3_connected:
            return
        self.input_type = item_type
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText(placeholder)
        self.input_edit.setObjectName("file_input")
        self.input_edit.setFixedHeight(30)
        self.input_edit.setFont(QFont("Segoe UI", 10))
        self.input_edit.installEventFilter(self)
        self.input_edit.returnPressed.connect(self.finish_inline_input)
        self.file_layout.insertWidget(0, self.input_edit)
        self.input_edit.show()
        self.input_edit.setFocus()

    def start_create_file(self):
        self.new_menu.hide()
        self.start_inline_input(item_type="file", placeholder="Filename")

    def start_create_directory(self):
        self.new_menu.hide()
        self.start_inline_input(item_type="directory", placeholder="Directory name")

    def get_buttons_layout_widget(self):
        return [self.back_button, self.home_button, self.new_button, self.refresh_button]

    def refresh(self):
        self.scroll_area.verticalScrollBar().setValue(0)
        self.refresh_requested.emit()

    def update_directory(self, entries):
        # Alte Einträge entfernen
        while self.file_layout.count():
            item = self.file_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Neue Einträge hinzufügen
        for entry in entries:
            file_item = FileItem(entry)
            file_item.clicked.connect(self.item_clicked)
            file_item.right_clicked.connect(self.item_right_clicked)
            self.file_layout.addWidget(file_item)

        self.file_layout.addStretch()

    def eventFilter(self, obj, event):
        if obj is self.input_edit:
            if (event.type() == QEvent.Type.FocusOut) or (event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape):
                self.cancel_inline_input()
                return False
        return super().eventFilter(obj, event)


class FileItem(QFrame):
    clicked = Signal(dict)
    right_clicked = Signal(dict)

    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.setObjectName("file_item")
        self.setFixedHeight(30)

        self.data = data

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)

        self.icon = QLabel("📁" if data["type"] == "directory" else "📄")

        self.name_label = QLabel(data["name"])
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
            self.clicked.emit(self.data)
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(self.data)
        super().mousePressEvent(event)