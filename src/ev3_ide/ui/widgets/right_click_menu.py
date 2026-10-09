from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout, QPushButton, QSpacerItem


class RightClickMenu(QFrame):
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
        self.open_button = QPushButton("  Open")
        self.open_button.setObjectName("combo_item")
        self.open_button.setFixedHeight(26)

        # Run
        self.run_button = QPushButton("  Run")
        self.run_button.setObjectName("combo_item")
        self.run_button.setFixedHeight(26)

        # Compile
        self.compile_button = QPushButton("  Compile")
        self.compile_button.setObjectName("combo_item")
        self.compile_button.setFixedHeight(26)

        # Rename
        self.rename_button = QPushButton("  Rename")
        self.rename_button.setObjectName("combo_item")
        self.rename_button.setFixedHeight(26)

        # Move
        self.move_button = QPushButton("  Move")
        self.move_button.setObjectName("combo_item")
        self.move_button.setFixedHeight(26)

        # Delete
        self.delete_button = QPushButton("  Delete")
        self.delete_button.setObjectName("combo_item")
        self.delete_button.setFixedHeight(26)

        # Properties
        self.properties_button = QPushButton("  Properties")
        self.properties_button.setObjectName("combo_item")
        self.properties_button.setFixedHeight(26)

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

        self.hide()

        QApplication.instance().installEventFilter(self)

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

    def keyPressEvent(self, event):
        print("Event triggered")
        if event.key() == Qt.Key.Key_Escape:
            print("Escape pressed")
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if not self.isVisible():
            return super().eventFilter(obj, event)
        if event.type() == QEvent.Type.MouseButtonPress:
            global_click_pos = event.globalPosition().toPoint()
            popup_rect = self.rect()
            popup_top_left = self.mapToGlobal(popup_rect.topLeft())
            popup_rect_global = popup_rect.translated(popup_top_left)
            if not popup_rect_global.contains(global_click_pos):
                self.hide()
                return False
        return super().eventFilter(obj, event)
