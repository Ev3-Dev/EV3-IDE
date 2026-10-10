from PySide6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel, QPushButton, QLineEdit
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QEvent
import posixpath

from ev3_ide.core.resources import resource_path
from ev3_ide.ui.widgets.new_file_dialog import NewMenu
from ev3_ide.ui.widgets.right_click_menu import RightClickMenu


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
    delete_file_requested = Signal(str)
    delete_directory_requested = Signal(str)
    rename_requested = Signal(str, str)

    def __init__(self, parent=None, overlay_parent=None):
        super().__init__(parent)

        self.setObjectName("files_widget")

        self.is_ev3_connected = False
        self.selected_item = None

        self.right_click_menu = RightClickMenu(overlay_parent)
        self.right_click_menu.open_button.clicked.connect(self.open_from_menu)
        self.right_click_menu.delete_button.clicked.connect(self.delete_from_menu)
        self.right_click_menu.closed.connect(self.clear_selected_item)
        self.right_click_menu.rename_button.clicked.connect(self.rename_from_menu)

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

        QApplication.instance().installEventFilter(self)

    def open_from_menu(self):
        data = self.right_click_menu.data
        self.right_click_menu.close_menu()
        self.item_clicked.emit(data)

    def delete_from_menu(self):
        data = self.right_click_menu.data
        self.right_click_menu.close_menu()
        if data["type"] == "file":
            self.delete_file_requested.emit(data["path"])
        elif data["type"] == "directory":
            self.delete_directory_requested.emit(data["path"])

    def rename_from_menu(self):
        if self.selected_item is None:
            return
        item = self.selected_item
        self.right_click_menu.close_menu()
        item.start_rename()

    def show_new_menu(self):
        self.new_menu.show_at(self.new_button)

    def clear_selected_item(self):
        if self.selected_item is not None:
            self.selected_item.set_selected(False)
            self.selected_item = None

    def show_right_click_menu(self, pos, data):
        # Vorherige Markierung entfernen
        if self.selected_item is not None:
            self.selected_item.set_selected(False)
        # Angeklicktes Element finden
        for index in range(self.file_layout.count()):
            widget = self.file_layout.itemAt(index).widget()
            if isinstance(widget, FileItem) and widget.data["path"] == data["path"]:
                self.selected_item = widget
                break
        # Neue Markierung setzen
        if self.selected_item is not None:
            self.selected_item.set_selected(True)

        self.right_click_menu.set_items(data)
        self.right_click_menu.show_at(pos)

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
        if self.selected_item is not None:
            self.selected_item = None
        self.right_click_menu.close_menu()

        # Alte Einträge entfernen
        while self.file_layout.count():
            item = self.file_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Neue Einträge hinzufügen
        for entry in entries:
            file_item = FileItem(entry)
            file_item.clicked.connect(self.item_clicked)
            file_item.right_clicked.connect(lambda data, pos: self.show_right_click_menu(pos, data))
            self.file_layout.addWidget(file_item)
            file_item.rename_requested.connect(self.rename_requested)

        self.file_layout.addStretch()

    def eventFilter(self, obj, event):
        if self.input_edit is not None:
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                    self.cancel_inline_input()
                    return True
            if event.type() == QEvent.Type.MouseButtonPress:
                if obj is not self.input_edit:
                    click_pos = event.globalPosition().toPoint()
                    input_pos = self.input_edit.mapToGlobal(self.input_edit.rect().topLeft())
                    input_rect = self.input_edit.rect()
                    input_rect.translate(input_pos)
                    if not input_rect.contains(click_pos):
                        self.cancel_inline_input()
            if obj is self.input_edit and event.type() == QEvent.Type.FocusOut:
                self.cancel_inline_input()
        return super().eventFilter(obj, event)


class FileItem(QFrame):
    clicked = Signal(dict)
    right_clicked = Signal(dict, object)
    rename_requested = Signal(str, str)

    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.setObjectName("file_item")
        self.setFixedHeight(30)

        self.data = data
        self.rename_edit = None

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

    def start_rename(self):
        if self.rename_edit is not None:
            return
        self.rename_edit = QLineEdit(self.data["name"])
        self.rename_edit.setObjectName("file_input")
        self.rename_edit.setFixedHeight(25)
        self.rename_edit.setFont(self.name_label.font())
        self.rename_edit.setPlaceholderText(self.data["name"])
        layout = self.layout()
        layout.insertWidget(1, self.rename_edit)
        self.name_label.hide()
        self.rename_edit.installEventFilter(self)
        self.rename_edit.returnPressed.connect(self.finish_rename)
        self.rename_edit.selectAll()
        self.rename_edit.setFocus()

    def finish_rename(self):
        if self.rename_edit is None:
            return
        new_name = self.rename_edit.text().strip()
        old_name = self.data["name"]
        if not new_name or new_name == old_name:
            self.cancel_rename()
            return
        old_path = self.data["path"]
        new_path = posixpath.join(posixpath.dirname(old_path), new_name)
        self.rename_requested.emit(old_path, new_path)
        self.cancel_rename()

    def cancel_rename(self):
        if self.rename_edit is None:
            return
        self.layout().removeWidget(self.rename_edit)
        self.rename_edit.deleteLater()
        self.rename_edit = None
        self.name_label.show()

    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.data)
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(self.data, event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        if obj is self.rename_edit:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Escape:
                    self.cancel_rename()
                    return True
        return super().eventFilter(obj, event)