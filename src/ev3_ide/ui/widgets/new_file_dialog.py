from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout, QPushButton


class NewMenu(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Aktionen
        self.file_action = QAction("file", self)
        self.directory_action = QAction("directory", self)

        # Popup
        self.setObjectName("combo_popup")
        self.setFixedWidth(100)

        self.popup_layout = QVBoxLayout(self)
        self.popup_layout.setContentsMargins(2, 2, 2, 2)
        self.popup_layout.setSpacing(1)

        self._build_popup()
        self.hide()

        QApplication.instance().installEventFilter(self)

    def _build_popup(self):
        # Datei
        file_button = QPushButton("  File")
        file_button.setObjectName("combo_item")
        file_button.setFixedHeight(26)
        file_button.clicked.connect(self.file_action.trigger)

        # Ordner
        directory_button = QPushButton("  Directory")
        directory_button.setObjectName("combo_item")
        directory_button.setFixedHeight(26)
        directory_button.clicked.connect(self.directory_action.trigger)

        # Hinzufügen
        self.popup_layout.addWidget(file_button)
        self.popup_layout.addWidget(directory_button)

    def show_at(self, widget):
        global_pos = widget.mapToGlobal(widget.rect().bottomLeft())
        global_pos.setX(global_pos.x() - 50)
        local_pos = self.parent().mapFromGlobal(global_pos)
        self.adjustSize()
        self.move(local_pos)
        self.raise_()
        self.show()
        self.setFocus()

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
