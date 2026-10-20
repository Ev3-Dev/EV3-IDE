from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
import ctypes

from ev3_ide.ui.widgets.dialog_title_bar import TitleBar


class SaveChangesDialog(QDialog):
    def __init__(self, file_name, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Dialog)
        self.resize(380, 90)
        self.setObjectName("save_changes_dialog")

        self.result_action = "cancel"

        # Hauptlayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        # Titelleiste
        self.title_bar = TitleBar("Unsaved Changes", "warning", self)
        self.title_bar.setFixedHeight(36)
        main_layout.addWidget(self.title_bar)

        # Inhalt
        content = QWidget()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(14, 12, 14, 12)
        content_layout.setSpacing(18)

        self.message_label = QLabel(f"Do you want to save the changes to '{file_name}' before closing?")
        self.message_label.setObjectName("dialog_message")
        self.message_label.setWordWrap(True)

        content_layout.addWidget(self.message_label)
        content_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("dialog_button")
        self.save_button.clicked.connect(self.save_changes)

        self.discard_button = QPushButton("Discard")
        self.discard_button.setObjectName("dialog_button")
        self.discard_button.clicked.connect(self.discard_changes)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("dialog_button")
        self.cancel_button.clicked.connect(self.cancel)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.discard_button)
        button_layout.addWidget(self.cancel_button)

        content_layout.addLayout(button_layout)
        main_layout.addWidget(content)

        self.cancel_button.setFocus()

    def save_changes(self):
        self.result_action = "save"
        self.accept()

    def discard_changes(self):
        self.result_action = "discard"
        self.accept()

    def cancel(self):
        self.result_action = "cancel"
        self.reject()

    def get_result(self):
        return self.result_action

    def nativeEvent(self, event_type, message):
        msg = ctypes.wintypes.MSG.from_address(int(message))
        if msg.message == 0x0083:
            return True, 0
        return super().nativeEvent(event_type, message)
