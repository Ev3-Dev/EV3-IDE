from PySide6.QtWidgets import QApplication, QVBoxLayout, QComboBox, QFrame, QPushButton
from PySide6.QtCore import Qt, QEvent


class IDEComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setFixedSize(110, 30)
        self.popup = QFrame(self.parent)
        self.popup.setObjectName("combo_popup")
        self.popup.setFixedWidth(140)

        self.popup_layout = QVBoxLayout(self.popup)
        self.popup_layout.setContentsMargins(2, 2, 2, 2)
        self.popup_layout.setSpacing(1)
        self.popup.adjustSize()
        self._build_popup()
        self.popup.hide()

        QApplication.instance().installEventFilter(self)

    def _build_popup(self):
        for index, text in enumerate(["Files", "EV3 State", "Libraries"]):
            button = QPushButton(f"  {text}")
            button.setFixedHeight(26)
            button.setObjectName("combo_item")
            button.clicked.connect(lambda checked=False, button_index=index: self._select_item(button_index))
            self.popup_layout.addWidget(button)

    def _select_item(self, index):
        self.setCurrentIndex(index)
        self.popup.hide()

    def showPopup(self):
        pos = self.mapTo(self.parent, self.rect().bottomLeft())
        self.popup.adjustSize()
        self.popup.move(pos)
        self.popup.raise_()
        self.popup.show()
        self.setFocus()

    def hidePopup(self):
        self.popup.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.popup.hide()
            event.accept()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if not self.popup.isVisible():
            return super().eventFilter(obj, event)
        if event.type() == QEvent.Type.MouseButtonPress:
            global_click_pos = event.globalPosition().toPoint()
            popup_rect = self.popup.rect()
            popup_top_left = self.popup.mapToGlobal(popup_rect.topLeft())
            popup_rect_global = popup_rect.translated(popup_top_left)
            if not popup_rect_global.contains(global_click_pos):
                self.popup.hide()
                return False
        return super().eventFilter(obj, event)