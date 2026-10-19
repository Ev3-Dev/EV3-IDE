from PySide6.QtCore import Qt, QEvent, Signal, QSize
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout, QPushButton, QTabBar, QPlainTextEdit, QSplitterHandle
from PySide6.QtGui import QIcon, QShortcut, QKeySequence

from ev3_ide.core.resources import resource_path


class RightClickMenu(QFrame):
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = dict()

        # Separator
        self.separator_container_1 = QFrame()
        self.separator_container_1.setFixedHeight(5)
        self.separator_layout_1 = QVBoxLayout(self.separator_container_1)
        self.separator_layout_1.setContentsMargins(2, 2, 2, 2)
        self.separator_1 = QFrame()
        self.separator_1.setObjectName("context_separator")
        self.separator_1.setFixedHeight(1)
        self.separator_1.setFixedWidth(120)
        self.separator_layout_1.addWidget(self.separator_1)

        self.separator_container_2 = QFrame()
        self.separator_container_2.setFixedHeight(5)
        self.separator_layout_2 = QVBoxLayout(self.separator_container_2)
        self.separator_layout_2.setContentsMargins(2, 2, 2, 2)
        self.separator_2 = QFrame()
        self.separator_2.setObjectName("context_separator")
        self.separator_2.setFixedHeight(1)
        self.separator_2.setFixedWidth(120)
        self.separator_layout_2.addWidget(self.separator_2)

        # Open
        self.open_button = QPushButton(" Open")
        self.open_button.setObjectName("combo_item")
        self.open_button.setFixedHeight(26)
        open_icon = QIcon(resource_path("ui/icons/open.svg"))
        self.open_button.setIcon(open_icon)
        self.open_button.setIconSize(QSize(166, 16))

        # Run
        self.run_button = QPushButton(" Run")
        self.run_button.setObjectName("combo_item")
        self.run_button.setFixedHeight(26)

        # Compile
        self.compile_button = QPushButton(" Compile")
        self.compile_button.setObjectName("combo_item")
        self.compile_button.setFixedHeight(26)

        # Rename
        self.rename_button = QPushButton(" Rename")
        self.rename_button.setObjectName("combo_item")
        self.rename_button.setFixedHeight(26)
        rename_icon = QIcon(resource_path("ui/icons/rename.svg"))
        self.rename_button.setIcon(rename_icon)
        self.rename_button.setIconSize(QSize(166, 16))

        # Move
        self.move_button = QPushButton(" Move")
        self.move_button.setObjectName("combo_item")
        self.move_button.setFixedHeight(26)
        move_icon = QIcon(resource_path("ui/icons/move.svg"))
        self.move_button.setIcon(move_icon)
        self.move_button.setIconSize(QSize(166, 16))

        # Delete
        self.delete_button = QPushButton(" Delete")
        self.delete_button.setObjectName("combo_item")
        self.delete_button.setFixedHeight(26)
        delete_icon = QIcon(resource_path("ui/icons/delete.svg"))
        self.delete_button.setIcon(delete_icon)
        self.delete_button.setIconSize(QSize(166, 16))

        # Properties
        self.properties_button = QPushButton(" Properties")
        self.properties_button.setObjectName("combo_item")
        self.properties_button.setFixedHeight(26)
        properties_icon = QIcon(resource_path("ui/icons/properties.svg"))
        self.properties_button.setIcon(properties_icon)
        self.properties_button.setIconSize(QSize(166, 16))

        # Popup
        self.setObjectName("combo_popup")
        self.setFixedWidth(130)

        self.popup_layout = QVBoxLayout(self)
        self.popup_layout.setContentsMargins(2, 2, 2, 2)
        self.popup_layout.setSpacing(1)
        self.popup_layout.addWidget(self.open_button)
        self.popup_layout.addWidget(self.run_button)
        self.popup_layout.addWidget(self.compile_button)
        self.popup_layout.addWidget(self.separator_container_1)
        self.popup_layout.addWidget(self.rename_button)
        self.popup_layout.addWidget(self.move_button)
        self.popup_layout.addWidget(self.delete_button)
        self.popup_layout.addWidget(self.separator_container_2)
        self.popup_layout.addWidget(self.properties_button)

        # Shortcuts
        self.open_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.open_shortcut.activated.connect(lambda: self.handle_shortcut("open"))
        self.rename_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F2), self)
        self.rename_shortcut.activated.connect(lambda: self.handle_shortcut("rename"))
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Backspace), self)
        self.delete_shortcut.activated.connect(lambda: self.handle_shortcut("delete"))

        self.hide()

        QApplication.instance().installEventFilter(self)

    def handle_shortcut(self, action):
        if not self.isVisible():
            return
        if action == "open":
            self.open_button.click()
        elif action == "rename":
            self.rename_button.click()
        elif action == "delete":
            self.delete_button.click()

    def set_items(self, data):
        self.data = data
        if data["type"] == "file":
            is_executable = data["executable"] or data["name"].lower().endswith(".py")
            is_compilable = data["name"].lower().endswith(".c") or data["name"].lower().endswith(".cpp")
            self.run_button.setVisible(is_executable)
            self.compile_button.setVisible(is_compilable)
        elif data["type"] == "directory":
            self.run_button.setVisible(False)
            self.compile_button.setVisible(False)


    def show_at(self, global_pos):
        local_pos = self.parent().mapFromGlobal(global_pos)
        spacer = 5
        if local_pos.x() + self.width() >= self.parent().width():
            local_pos.setX(local_pos.x() - (local_pos.x() + self.width() - self.parent().width()) - spacer)
        if local_pos.y() + self.height() >= self.parent().height():
            local_pos.setY(local_pos.y() - (local_pos.y() + self.height() - self.parent().height()) - spacer)
        self.adjustSize()
        self.move(local_pos)
        self.raise_()
        self.show()

    def close_menu(self):
        self.hide()
        self.closed.emit()

    def eventFilter(self, obj, event):
        if not self.isVisible():
            return super().eventFilter(obj, event)
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.close_menu()
                return True
        if event.type() == QEvent.Type.Wheel:
            self.close_menu()
            return False
        if event.type() == QEvent.Type.MouseButtonPress:
            global_click_pos = event.globalPosition().toPoint()
            popup_rect = self.rect()
            popup_top_left = self.mapToGlobal(popup_rect.topLeft())
            popup_rect_global = popup_rect.translated(popup_top_left)
            if not popup_rect_global.contains(global_click_pos):
                self.close_menu()
                widget = QApplication.widgetAt(global_click_pos)
                if isinstance(widget, (QPushButton, QTabBar, QPlainTextEdit, QSplitterHandle)):
                    return False
                while widget is not None:
                    if isinstance(widget, QPlainTextEdit):
                        return False
                    widget = widget.parentWidget()
                return True
        return super().eventFilter(obj, event)
