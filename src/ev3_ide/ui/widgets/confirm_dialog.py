from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
import ctypes

from ev3_ide.ui.widgets.dialog_title_bar import TitleBar


class ConfirmDialog(QDialog):
    def __init__(self, title, message, parent=None, confirm_text="Yes", cancel_text="No"):
        super().__init__(parent)

        # 1. WICHTIG: Kein FramelessWindowHint! Normaler Dialog.
        # So weiß das Windows-System, dass es die native Zoom-Animation nutzen soll.
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.resize(380, 90)
        self.setObjectName("dialog_window")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Eigene Titelleiste
        self.title_bar = TitleBar(title, "warning", self)
        self.title_bar.setFixedHeight(36)
        main_layout.addWidget(self.title_bar)

        # Nachricht/Inhalt
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(14, 12, 14, 12)
        content_layout.setSpacing(16)

        message_label = QLabel(message)
        message_label.setObjectName("dialog_message")
        message_label.setWordWrap(True)
        content_layout.addWidget(message_label)
        content_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addStretch()

        self.confirm_button = QPushButton(confirm_text)
        self.confirm_button.setObjectName("dialog_button")
        self.confirm_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton(cancel_text)
        self.cancel_button.setObjectName("dialog_button")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        content_layout.addLayout(button_layout)
        main_layout.addWidget(content)

        self.cancel_button.setFocus()

    def nativeEvent(self, event_type, message):
        msg = ctypes.wintypes.MSG.from_address(int(message))
        if msg.message == 0x0083:
            return True, 0
        return super().nativeEvent(event_type, message)