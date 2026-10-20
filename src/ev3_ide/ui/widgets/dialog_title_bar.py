from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QIcon

from ev3_ide.core.resources import resource_path


class TitleBar(QFrame):
    def __init__(self, title, icon_name, parent=None):
        super().__init__(parent)

        self._drag_start_pos = None

        self.setObjectName("title_bar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 0, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel()
        icon = QIcon(resource_path(f"ui/icons/{icon_name}.svg"))
        pixmap = icon.pixmap(20, 20)
        self.icon_label.setPixmap(pixmap)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("title_label")

        self.close_button = QPushButton()
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(QSize(35, 35))
        self.close_button.setIcon(QIcon(resource_path("ui/icons/window_close.svg")))
        self.close_button.setIconSize(QSize(16, 16))
        self.close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_button.clicked.connect(self._close_window)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.close_button)

    def _close_window(self):
        self.window().close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.globalPosition().toPoint()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            drag_distance = (event.globalPosition().toPoint() - self._drag_start_pos).manhattanLength()
            if drag_distance > QApplication.startDragDistance():
                window_handle = self.window().windowHandle()
                if window_handle is not None:
                    self._drag_start_pos = None
                    window_handle.startSystemMove()
                    event.accept()
                    return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)